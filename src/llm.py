import os
import json
import time
from groq import Groq
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from src.safety import sanitize_input
from src.models import LLMOutput
from src.prompts import CV_SYSTEM_PROMPT, FEW_SHOT_MESSAGES
from src.tools import TOOL_DEFINITIONS, execute_tool

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))



# Token counting ke liye


# ─── Token Budget ──────────────────────────────────────────────────
MAX_INPUT_TOKENS = 2000  # maximum input tokens allow karo

def count_tokens(text: str) -> int:
    """Rough token count — 1 token ≈ 4 characters"""
    return len(text) // 4

def truncate_if_needed(cv_text: str) -> str:
    """CV zyada lamba ho toh truncate karo"""
    token_count = count_tokens(cv_text)
    
    print(f"CV tokens (approximate): {token_count}")
    
    if token_count > MAX_INPUT_TOKENS:
        print(f"CV too long — truncating to {MAX_INPUT_TOKENS} tokens")
        # 4 characters per token
        max_chars = MAX_INPUT_TOKENS * 4
        return cv_text[:max_chars] + "\n... [truncated]"
    
    return cv_text

# ─── Circuit Breaker ───────────────────────────────────────────────
class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=30):
        self.failure_threshold = failure_threshold  # kitni failures pe open ho
        self.recovery_timeout = recovery_timeout    # kitne second baad retry kare
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED = normal, OPEN = band, HALF-OPEN = testing

    def call(self, func, *args, **kwargs):
        # OPEN state mein check karo recovery time guzri ya nahi
        if self.state == "OPEN":
            time_passed = time.time() - self.last_failure_time
            if time_passed >= self.recovery_timeout:
                print("Circuit HALF-OPEN — ek request try kar rahe hain")
                self.state = "HALF-OPEN"
            else:
                remaining = int(self.recovery_timeout - time_passed)
                raise Exception(f"Circuit OPEN hai — {remaining} second baad try karo")

        # Function call karo
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
        print("Circuit CLOSED — sab theek hai")

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            print(f"Circuit OPEN — {self.failure_threshold} failures ke baad band hua")


circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)


# ─── LLM Call with Retry ───────────────────────────────────────────


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _call_llm_with_retry(messages: list):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        tools=TOOL_DEFINITIONS,
        tool_choice="auto",
        max_tokens=1000,
        timeout=10
    )
    
    # Token usage log karo
    usage = response.usage
    print(f"Input tokens: {usage.prompt_tokens}")
    print(f"Output tokens: {usage.completion_tokens}")
    print(f"Total tokens: {usage.total_tokens}")
    
    return response.choices[0]


def call_llm(messages: list):
    """Circuit breaker + retry dono saath"""
    return circuit_breaker.call(_call_llm_with_retry, messages)


# ─── JSON Repair Strategy ──────────────────────────────────────────
def parse_json_with_repair(raw: str) -> dict:
    """JSON parse karo — fail ho toh LLM se repair karwao"""
    # Step 1 - seedha parse karo
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("JSON malformed — repair try kar rahe hain")

    # Step 2 - common issues fix karo
    cleaned = raw.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    try:
        return json.loads(cleaned.strip())
    except json.JSONDecodeError:
        pass

    # Step 3 - LLM se repair karwao
    print("LLM se JSON repair karwa rahe hain")
    repair_messages = [
        {
            "role": "system",
            "content": "Fix the malformed JSON. Return ONLY valid JSON, nothing else."
        },
        {
            "role": "user",
            "content": f"Fix this JSON:\n{raw}"
        }
    ]
    repair_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=repair_messages,
        max_tokens=1000
    )
    repaired = repair_response.choices[0].message.content
    return json.loads(repaired)


# ─── Main Function ─────────────────────────────────────────────────
def analyze_cv(cv_text: str) -> LLMOutput:
    cv_text = sanitize_input(cv_text)
    cv_text = truncate_if_needed(cv_text)
    messages = [
        {"role": "system", "content": CV_SYSTEM_PROMPT},
        *FEW_SHOT_MESSAGES,
        {"role": "user", "content": cv_text}
    ]

    try:
        response = call_llm(messages)
    except RetryError:
        raise Exception("LLM 3 baar fail hua — baad mein try karo")

    # Tool call loop
    while response.finish_reason == "tool_calls":
        tool_call = response.message.tool_calls[0]
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)

        print(f"Tool call: {tool_name} with args: {tool_args}")

        tool_result = execute_tool(tool_name, tool_args)

        messages.append({"role": "assistant", "content": None, "tool_calls": [tool_call]})
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": tool_result
        })

        try:
            response = call_llm(messages)
        except RetryError:
            raise Exception("Tool call ke baad LLM fail hua")

    # JSON parse + repair
    raw_json = response.message.content
    parsed_dict = parse_json_with_repair(raw_json)

    return LLMOutput(**parsed_dict)