"""
Streamlit UI for the RAG chat. Run with:

    D:\PracticePrograms\RAG\Bhavya_RAG_Project\ragproject\Scripts\python.exe -m streamlit run ui/app_streamlit.py

This file attempts to import `answer()` from `ragimplementation` if available. If `ragimplementation` exposes only `chain`, it falls back to calling `chain.invoke`.
"""
import streamlit as st


# Try to import a lightweight answer() wrapper from ragimplementation.
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

st.title("HR RAG Chat")
q = st.text_input("Ask a question about HR policy:")
if st.button("Ask") and q:
    with st.spinner("Thinking..."):
        resp = answer(q)
    st.subheader("Answer")
    st.write(resp)
