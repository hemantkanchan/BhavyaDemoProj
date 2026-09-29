UI folder

Files created:
- app_streamlit.py — Streamlit demo
- app_gradio.py — Gradio demo
- app_fastapi.py — FastAPI + minimal HTML demo
- requirements-ui.txt — UI libs

Quick run (PowerShell):

1) Activate venv:

    .cd 'D:\PracticePrograms\RAG\Bhavya_RAG_Project'
    .\ragproject\Scripts\Activate.ps1

2) Install UI deps (optional):

    python -m pip install -r ui/requirements-ui.txt

3) Run Streamlit:

    python -m streamlit run ui/app_streamlit.py

Or run Gradio:

    python ui/app_gradio.py

Or run FastAPI (uvicorn):

    python -m uvicorn ui.app_fastapi:app --reload

Notes:
- Prefer refactoring `ragimplementation` to expose a lightweight `answer(question)` function to avoid heavy model downloads at import time.
- If `ragimplementation` currently builds models on import, the first request will be slow as models load.
