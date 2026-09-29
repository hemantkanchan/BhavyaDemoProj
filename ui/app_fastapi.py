"""
FastAPI + minimal HTML UI. Run with:

    D:\PracticePrograms\RAG\Bhavya_RAG_Project\ragproject\Scripts\python.exe -m uvicorn ui.app_fastapi:app --reload

Visit: http://127.0.0.1:8000/
"""
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

try:
    from ragimplementation import answer
except Exception:
    try:
        from ragimplementation import chain
        def answer(q):
            return chain.invoke({"question": q})
    except Exception as e:
        def answer(q):
            return f"Error importing ragimplementation: {e}"

app = FastAPI()

HTML = """
<!doctype html>
<title>RAG Chat</title>
<form method="post" action="/ask">
  <input name="q" style="width:80%" placeholder="Ask a question" />
  <button type="submit">Ask</button>
</form>
<pre>{resp}</pre>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML.format(resp="")

@app.post("/ask", response_class=HTMLResponse)
def ask(q: str = Form(...)):
    resp = answer(q)
    return HTML.format(resp=resp)
