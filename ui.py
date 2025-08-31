import streamlit as st
from chain import run_chain_with_history
from helper import init_session_state

def render_app():
    st.set_page_config(page_title='NL -> Cypher -> Neo4j -> Result', layout='wide')
    st.title('Query Movie Details')
    prev = ""
    init_session_state()

    with st.sidebar:
        st.header('History')
        if st.session_state.history:
            for idx, h in enumerate(reversed(st.session_state.history), start=1):
                label = f"{idx}. {h['user'][:60]}" 
                if st.button(label, key=f"history_{idx}"):
                    # re-run selected prompt
                    out = run_chain_with_history(h["user"], history_items=5)
                    prev = h["user"]
                    if out.get("error"):
                        st.error(out["error"])
                    else:
                        st.success("Re-run finished. Check main area for result.")
                        st.session_state["last_rerun"] = out
        else:
            st.write("No history yet.")
    
        if st.button("Clear history"):
            st.session_state.history = []
            st.rerun()

    # Main panel
    prompt = st.text_area('Prompt (e.g. "Who played in Top Gun?")', height=140,value=prev)
    submit = st.button('Run')

    if "last_rerun" in st.session_state:
        last = st.session_state.pop("last_rerun")
        if last.get("error"):
            st.error(last["error"])
        else:
            st.subheader("Re-run Result")
            st.write(last["result"])
            st.subheader("Cypher")
            st.caption(last["query"])
            
    
    if submit:
        if not prompt.strip():
            st.warning('Please write a prompt before running.')
            return
        with st.spinner('Generating Cypher and running query...'):
            out = run_chain_with_history(prompt, history_items=5)
        if out.get('error'):
            st.error(f"Error: {out['error']}")
            return
        st.subheader('Results')
        st.write(out.get('result'))
        st.subheader('Cypher')
        st.caption(out.get('query'))

def main():
    render_app()

main()
