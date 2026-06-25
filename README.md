# 🤖 CV Analyzer API

An AI-powered CV analyzer built with FastAPI + Groq (LLaMA 3.3 70B). Send your CV text and get structured analysis with job recommendations.

## 🚀 Live API  https://cv-analyzer-production-dd4e.up.railway.app/
---

## 📡 API Endpoint Post/analyze_cv

---

## 📝 Request Format

```json
{
  "cv_text": "Muhammad Wasil\nFull Stack Engineer\nEXPERIENCE\nNext.js Developer at SnipByte\nEDUCATION\nBS Computer Science COMSATS\nSKILLS\nReact, FastAPI, Docker"
}
```

> **Note:** Use `\n` for newlines in Postman. Frontend `JSON.stringify()` handles this automatically.

---

## ✅ Response Format

```json
{
  "name": "Muhammad Wasil",
  "education": {
    "university_name": "COMSATS University",
    "degree_title": "BS Computer Science",
    "cgpa": 3.35,
    "date": "2022-2026"
  },
  "skills": ["React.js", "FastAPI", "Docker"],
  "experience": 2,
  "suggested_roles": ["Full Stack Developer", "AI Engineer"]
}
```

---

## 🛠️ Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/muhammad-wasil-ali/cv-analyzer-api.git
cd cv-analyzer-api
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Setup environment**
```bash
# .env file banao
GROQ_API_KEY=your_groq_api_key_here
```

> Get free Groq API key: [console.groq.com](https://console.groq.com)

**4. Run server**
```bash
uvicorn src.main:app --reload
```

**5. Test karo**
```bash
python test.py
```

---

## 📚 Interactive Docs   http://localhost:8000/docs

---

## 🏗️ Project Structure
cv-analyzer/
├── src/
│   ├── main.py       # FastAPI endpoints
│   ├── models.py     # Pydantic schemas
│   ├── llm.py        # Groq client + tool loop + reliability
│   ├── tools.py      # Tool definitions + functions
│   ├── prompts.py    # System prompt + few-shot examples
│   └── safety.py     # Prompt injection + PII handling
├── test.py           # Local testing script
├── .env              # API keys (git ignored)
└── requirements.txt


---

## ⚠️ Common Errors

| Error | Reason | Fix |
|-------|--------|-----|
| 422 Unprocessable | `cv_text` key missing | JSON mein `"cv_text"` key zaroori hai |
| 422 Unprocessable | Multi-line text in Postman | `\n` use karo newlines ke liye |
| 400 Bad Request | Prompt injection detected | Remove words like "ignore instructions" |
| 500 Internal Error | LLM failed / circuit breaker open | 30 seconds baad retry karo |

---

## 🧠 Tech Stack

- **FastAPI** — Backend framework
- **Groq** — Free LLM API (LLaMA 3.3 70B)
- **Pydantic** — Schema validation
- **Tenacity** — Retry + exponential backoff
- **Railway** — Deployment

---

## 👨‍💻 Built By

**Muhammad Wasil Ali** — Full Stack AI Engineer  
[GitHub](https://github.com/muhammad-wasil-ali) • [LinkedIn](https://linkedin.com/in/muhammad-wasil-ali)
