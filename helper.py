import streamlit as st

def init_session_state():
    if "history" not in st.session_state:
        # history is list of dicts: { "user": str, "result": str, "cypher": str }
        st.session_state.history = []
    if "max_history_items" not in st.session_state:
        st.session_state.max_history_items = 5  

def format_history_text(history, max_items=None):
    """Return plain text of last N exchanges for prepending to query"""
    if not history:
        return ""
    if max_items:
        hx = history[-max_items:]
    else:
        hx = history
    parts = []
    for i, e in enumerate(hx, start=1):
        user = e.get("user", "").strip()
        result = e.get("result", "").strip()
        cypher = e.get("cypher", "").strip()
        parts.append(f"[{i}] User: {user}\n[   ] Cypher: {cypher}\n[   ] Result: {result}\n")
    return "\n".join(parts)

def trimmed_history(history, keep):
    """Return last 'keep' items"""
    return history[-keep:] if len(history) > keep else history
