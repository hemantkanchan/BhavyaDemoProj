"""Compatibility shim to make the existing `ragimplementation` script importable.

This file lazily executes the original script (named `ragimplementation` without
`.py` in the repo root) using `runpy.run_path` the first time the chain is
needed, and exposes `get_chain()` and `answer(question)` helpers for UIs.

Usage:
    from ragimplementation import answer
    answer("your question")
"""
from __future__ import annotations
import runpy
import os
import threading
from typing import Any

_root = os.path.dirname(__file__)
_script_path = os.path.join(_root, "ragimplementation")
_globals: dict[str, Any] = {}
_loaded = False
_lock = threading.Lock()


def _load() -> None:
    """Execute the original script once and cache its globals."""
    global _loaded, _globals
    with _lock:
        if _loaded:
            return
        if not os.path.exists(_script_path):
            raise FileNotFoundError(f"Original script not found at {_script_path}")
        _globals = runpy.run_path(_script_path, run_name="__main__")
        _loaded = True


def get_chain():
    """Return the `chain` object from the script, or None if not present."""
    _load()
    return _globals.get("chain")


def answer(question: str) -> Any:
    """Invoke the chain and return a compact result.

    The returned dict contains:
      - `answer`: string result produced by the chain
      - `sources`: list of {source, snippet} for top documents
      - `tokens`: best-effort token usage info (may be None)

    This prevents returning the entire raw chain output and large objects.
    """
    chain = get_chain()
    if chain is None:
        raise RuntimeError("`chain` not found in ragimplementation script")

    # Run the chain
    raw = chain.invoke({"question": question})

    def _ensure_str_output(x: Any) -> str:
        if isinstance(x, str):
            return x
        if isinstance(x, dict):
            return x.get("text") or x.get("content") or str(x)
        return str(x)

    answer_str = _ensure_str_output(raw)

    # Best-effort: find token usage info anywhere in the raw result
    def _find_token_usage(obj: Any):
        keys_of_interest = {"prompt_tokens", "completion_tokens", "total_tokens", "tokens", "usage", "token_count", "token_usage", "tokens_used"}
        if isinstance(obj, dict):
            if any(k in obj for k in keys_of_interest):
                return {k: obj[k] for k in obj.keys() if k in keys_of_interest}
            for v in obj.values():
                found = _find_token_usage(v)
                if found:
                    return found
        elif isinstance(obj, (list, tuple)):
            for item in obj:
                found = _find_token_usage(item)
                if found:
                    return found
        return None

    tokens_info = _find_token_usage(raw)

    # Retrieve top documents used for context from available vectorstore/retriever
    sources = []
    try:
        vect = _globals.get("vectordb") or _globals.get("vectorstore") or _globals.get("retriever")
        if vect is not None:
            # Some objects expose `similarity_search`, others may be retrievers
            if hasattr(vect, "similarity_search"):
                docs = vect.similarity_search(question, k=3)
            else:
                # try as_retriever then internal call
                try:
                    retr = vect.as_retriever(search_kwargs={"k": 3}) if hasattr(vect, "as_retriever") else vect
                    # prefer `similarity_search` on retr
                    if hasattr(retr, "similarity_search"):
                        docs = retr.similarity_search(question, k=3)
                    else:
                        # fallback: try _get_relevant_documents (may require run_manager)
                        docs = retr._get_relevant_documents(question) if hasattr(retr, "_get_relevant_documents") else []
                except Exception:
                    docs = []
            for d in docs:
                try:
                    meta = getattr(d, "metadata", None) or (d.get("metadata") if isinstance(d, dict) else None)
                    src = None
                    if isinstance(meta, dict):
                        src = meta.get("source") or meta.get("id") or str(meta)
                    else:
                        src = str(meta)
                    content = getattr(d, "page_content", None) or (d.get("page_content") if isinstance(d, dict) else str(d))
                    snippet = (content[:400] + "...") if isinstance(content, str) and len(content) > 400 else content
                    sources.append({"source": src, "snippet": snippet})
                except Exception:
                    continue
    except Exception:
        sources = []

    return {"answer": answer_str, "sources": sources, "tokens": tokens_info}


__all__ = ["get_chain", "answer"]
