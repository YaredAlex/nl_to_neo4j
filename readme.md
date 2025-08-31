# Streamlit Neo4j LLM App Using Gemini + LangChain

## Start

1. `pip install -r requirements.txt`
2. `streamlit run ui.py`

## Notes

- The chain uses Gemini (via langchain-google-genai). Set `GOOGLE_API_KEY`
- The chain uses langchain_neo4j package. Set `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`

## Example prompts

1. Who played in Top Gun?
2. Which actors acted in The Matrix
3. Which movies were released in 1999
4. Which actor has acted in the most movies
5. Find actors who acted in at least 3 movies released after 2000
6. Which pairs of actors have acted together in more than one movie?
7. List all movies where Tom Hanks and Meg Ryan acted together.
