import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate,PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
import streamlit as st
from helper import format_history_text, trimmed_history

load_dotenv(override=True)

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')

CYPHER_GENERATION_TEMPLATE = """
Task:Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Schema:
{schema}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
Examples: Here are a few examples of generated Cypher statements for particular questions:
# How many people played in Top Gun?
MATCH (m:Movie {{name:"Top Gun"}})<-[:ACTED_IN]-()
RETURN count(*) AS numberOfActors

The question is:
{question}"""

cypher_prompt = PromptTemplate(
    input_variables=["schema", "question"], template=CYPHER_GENERATION_TEMPLATE
)


llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0.0, max_retries=1)
graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USER, password=NEO4J_PASSWORD)

chain = GraphCypherQAChain.from_llm(
    llm, 
    graph=graph, 
    verbose=True, 
    allow_dangerous_requests=True,
     cypher_prompt=cypher_prompt,
    # function_response_system="Respond as a pirate!",
    validate_cypher=True,
    return_intermediate_steps=True
    # use_function_response=True,# model need to have native fanction calling ability
)

def run_chain(user_prompt: str,history):
    try:
        res = chain.invoke({"query": user_prompt})
        # print(res)
        intermediate_steps = res['intermediate_steps']
        return {"result": res['result'],'query':intermediate_steps[0]['query']}
    except Exception as e:
        if e.get("message") and "This query cannot be answered using the provided schema" in e.message:
            return {"error": "This query cannot be answered using the provided schema"}
        return {"error": str(e)}
    

def run_chain_with_history(user_prompt: str, history_items=5):

    chat_history_text = format_history_text(st.session_state.history, max_items=history_items)
    if chat_history_text:
        augmented_query = (
            f"""Conversation history (most recent first):
            {chat_history_text}
            Now the user asks:
            {user_prompt}
            """
        )
    else:
        augmented_query = user_prompt

    try:
        res = chain.invoke({"query": augmented_query})
        intermediate_steps = res.get("intermediate_steps", [])
        cypher_text = ""
        if  len(intermediate_steps) > 0:
            cypher_text = intermediate_steps[0].get("query", "")

        result_text = res.get("result") or res.get("output_text") or str(res)
        st.session_state.history.append({"user": user_prompt, "result": result_text, "cypher": cypher_text})
        st.session_state.history = trimmed_history(st.session_state.history, st.session_state.max_history_items)

        return {"result": result_text, "query": cypher_text}
    except Exception as e:
        msg = str(e)
        if hasattr(e, "message") and isinstance(e.message, str) and "This query cannot be answered using the provided schema" in e.message:
            return {"error": "This query cannot be answered using the provided schema"}
        return {"error": msg}