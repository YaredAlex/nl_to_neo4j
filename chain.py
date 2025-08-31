import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate,PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
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


explain_prompt = ChatPromptTemplate.from_messages([
("system", """You are a helpful assistant that explains Cypher queries and their results in plain English."""),
("user", "Here is the Cypher:\n```cypher\n{cypher}\n```\n\nResults JSON:\n{results_json}\n\nExplain what this query "
"does and what the results show.")
])

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

def run_chain(user_prompt: str):
    try:
        res = chain.invoke({"query": user_prompt})
        # print(res)
        intermediate_steps = res['intermediate_steps']
        return {"result": res['result'],'query':intermediate_steps[0]['query']}
    except Exception as e:
        if e.get("message") and "This query cannot be answered using the provided schema" in e.message:
            return {"error": "This query cannot be answered using the provided schema"}
        return {"error": str(e)}