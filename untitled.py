import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage,HumanMessage
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph

load_dotenv(override=True)
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0.0, max_retries=1)


NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0.0, max_retries=1)
graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USER, password=NEO4J_PASSWORD)

chain = GraphCypherQAChain.from_llm(
    llm, 
    graph=graph, 
    verbose=True, 
    allow_dangerous_requests=True, # required by langchain to make dangerous requrest 
    # function_response_system="Respond as a pirate!",
    # validate_cypher=True,
    use_function_response=True,# model need to have native fanction calling ability
)
try:
    res = chain.invoke({"query": "Who is president of united states?"})
    print(type(res))
    print(res)
except Exception as e:
    print(e)
    print(e.message)




