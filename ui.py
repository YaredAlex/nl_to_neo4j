import streamlit as st
from chain import run_chain

def render_app(handle_submit):
    st.set_page_config(page_title='NL -> Cypher -> Neo4j -> Result', layout='wide')
    st.title('Query Movie Details')

    with st.sidebar:
        st.header('History')

    prompt = st.text_area('Prompt (e.g. "Who played in Top Gun?")', height=140)
    submit = st.button('Run')

    if submit:
        if not prompt.strip():
            st.warning('Please write a prompt before running.')
            return
        with st.spinner('Generating Cypher and running query...'):
            out = handle_submit(prompt)
        if out.get('error'):
            st.error(f"Error: {out['error']}")
            return
        st.subheader('Results')
        result = out.get('result')
        st.write(result)
        query = out.get('query')
        st.subheader('Query')
        st.caption(query)

def main():
    render_app(handle_submit=lambda prompt:run_chain(prompt))

main()