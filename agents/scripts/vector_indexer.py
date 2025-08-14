import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv; load_dotenv()
os.environ.setdefault("OPENAI_API_KEY", os.getenv("OPEN_AI_KEY", ""))

USE_LOCAL = os.getenv("EMBEDDING_BACKEND","openai").lower() == "local"
if USE_LOCAL:
    from chromadb.utils import embedding_functions
    local_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=os.getenv("LOCAL_EMBED_MODEL","all-MiniLM-L6-v2")
    )

# Use OpenAI or other embedding model
from openai import OpenAI

# Optional: configure if using LangChain embedding wrapper
# from langchain.embeddings import OpenAIEmbeddings

# 1. Initialize ChromaDB
client = chromadb.PersistentClient(path="./chroma_data")

collection = client.get_or_create_collection(
    name="reddit_posts",
    metadata={"description": "Agent‑1 Reddit posts & comments context"}
)

# 2. Initialize embedding function
openai_client = OpenAI(api_key=os.getenv("OPEN_AI_KEY"))

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

def embed_texts(texts):
    if USE_LOCAL:
        return local_ef(texts)
    resp = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )
    return [d.embedding for d in resp.data]

# 3. Index new items (e.g. fetched Reddit threads or comments)
def index_items(items: list):
    """
    items: list of dict with keys 'id', 'text', 'subreddit', 'type', 'timestamp'
    """
    texts = [i["text"] for i in items]
    ids = [i["id"] for i in items]
    metadatas = [{"subreddit": i["subreddit"], "type": i["type"], "ts": i["timestamp"]} for i in items]
    embeddings = embed_texts(texts)
    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

# 4. Retrieve context for new post prompt
def retrieve_context(subreddit: str, query_text: str, top_k=3):
    q_emb = embed_texts([query_text])[0]
    results = collection.query(
        query_embeddings=[q_emb],
        n_results=top_k,
        where={"subreddit": subreddit}
    )
    # results["documents"] is list[list[str]]
    context = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        snippet = f"[{meta.get('type')} in r/{meta.get('subreddit')}]: {doc[:300]}..."
        context.append(snippet)
    return context

if __name__ == "__main__":
    # Example usage:
    example = [{
        "id": "rMLQ1234",
        "text": "Turning Ilya Sutskever's 30 papers into stories...",
        "subreddit": "MachineLearning",
        "type": "post",
        "timestamp": "2025-07-28T12:00:00Z"
    }]
    index_items(example)
    print("Indexed example. Sample context:", retrieve_context("MachineLearning", example[0]["text"]))

