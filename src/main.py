from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from src.models import CVInput, LLMOutput
from src.llm import analyze_cv

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def welcome():
    return """
    <html>
        <body style="font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px;">
            <h1>🤖 CV Analyzer API</h1>
            <p>Send your CV text and get structured analysis with job recommendations.</p>
            
            <h2>📡 Endpoint</h2>
            <code>POST /analyze_cv</code>
            
            <h2>📝 Request Format</h2>
            <pre style="background:#f4f4f4; padding:15px; border-radius:5px;">
{
  "cv_text": "Your Name\nJob Title\nEXPERIENCE\n...\nEDUCATION\n...\nSKILLS\n..."
}
            </pre>

            <h2>✅ Response Format</h2>
            <pre style="background:#f4f4f4; padding:15px; border-radius:5px;">
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
            </pre>

            <h2>📚 Interactive Docs</h2>
            <p>Test the API directly: <a href="/docs">/docs</a></p>
            <h2>📚 Interactive Docs</h2>
            <p>Test the API directly: <a href="/docs">/docs</a></p>

            <h2>💡 Important Note</h2>
            <p>🖥️ <strong>Frontend:</strong> JSON.stringify() automatically handles newlines — kuch nahi karna.</p>
            <p>📮 <strong>Postman:</strong> Multi-line text mein manually <strong>\n</strong> use karo har newline pe.</p>
            <pre style="background:#f4f4f4; padding:15px; border-radius:5px;">
✅ Sahi:  "cv_text": "Name\\nEducation\\nSkills"
❌ Galat: "cv_text": "Name
                      Education
                      Skills"
            </pre>
        </body>
    </html>
    """

@app.post("/analyze_cv", response_model=LLMOutput)
def process_cv(body: CVInput):
    try:
        result = analyze_cv(body.cv_text)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))