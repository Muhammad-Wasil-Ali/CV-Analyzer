import re

# ─── Prompt Injection Patterns ─────────────────────────────────────
INJECTION_PATTERNS = [
    "ignore all instructions",
    "ignore previous instructions", 
    "you are now",
    "forget your instructions",
    "disregard all",
    "do not follow",
    "new instruction",
    "system prompt",
]

# ─── PII Patterns ──────────────────────────────────────────────────
EMAIL_PATTERN = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
PHONE_PATTERN = re.compile(r'(\+92|0)?[-.\s]?\d{3}[-.\s]?\d{7,8}')
CNIC_PATTERN  = re.compile(r'\d{5}-\d{7}-\d{1}')


def check_prompt_injection(text: str) -> None:
    """Prompt injection detect karo — mila toh error throw karo"""
    text_lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if pattern in text_lower:
            raise ValueError(f"Prompt injection detected: '{pattern}'")


def redact_pii(text: str) -> str:
    """PII redact karo logs ke liye"""
    text = EMAIL_PATTERN.sub("[EMAIL REDACTED]", text)
    text = PHONE_PATTERN.sub("[PHONE REDACTED]", text)
    text = CNIC_PATTERN.sub("[CNIC REDACTED]", text)
    return text


def sanitize_input(cv_text: str) -> str:
    """
    Input sanitize karo:
    1. Injection check karo
    2. PII redact karo logs ke liye
    3. Clean text return karo
    """
    # Step 1 - injection check
    check_prompt_injection(cv_text)
    
    # Step 2 - log ke liye redacted version print karo
    redacted = redact_pii(cv_text)
    print(f"Input received (redacted): {redacted[:100]}...")
    
    # Step 3 - original text return karo LLM ke liye
    # (LLM ko actual data chahiye, sirf logs redact honge)
    return cv_text