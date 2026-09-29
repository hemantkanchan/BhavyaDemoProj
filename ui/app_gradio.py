"""
Gradio UI for the RAG chat. Run with:

    D:\PracticePrograms\RAG\Bhavya_RAG_Project\ragproject\Scripts\python.exe ui/app_gradio.py

Same import strategy as Streamlit scaffold.
"""
import gradio as gr

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

iface = gr.Interface(fn=answer, inputs="text", outputs="text", title="ACME RAG Chat")

if __name__ == "__main__":
    iface.launch()
