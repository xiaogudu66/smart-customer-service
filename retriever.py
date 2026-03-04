# retriever.py
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")

embeddings = OpenAIEmbeddings(
    model="text-embedding-ada-002",
    openai_api_key=api_key,
    openai_api_base=api_base
)

vectorstore = FAISS.load_local(
    "./faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

def retrieve_documents(query, k=5):
    """检索相关文档块，返回 (文档, 相似度分数) 列表"""
    return vectorstore.similarity_search_with_score(query, k=k)