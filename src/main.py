from fastapi import FastAPI, HTTPException
from src.models import CVInput, LLMOutput
from src.llm import analyze_cv

app = FastAPI()

@app.post("/analyze_cv", response_model=LLMOutput)
def process_cv(body: CVInput):
    try:
        result = analyze_cv(body.cv_text)
        return result
    except ValueError as e:
        # Prompt injection ya validation error
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # LLM failure, circuit breaker, etc
        raise HTTPException(status_code=500, detail=str(e))