# retriever.py
import os
# retriever.py
import os
import time
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

INDEX_PATH = "./faiss_index"
_last_mtime = 0
_vectorstore = None

def _load_vectorstore():
    global _vectorstore, _last_mtime
    if os.path.exists(INDEX_PATH):
        _vectorstore = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        _last_mtime = os.path.getmtime(INDEX_PATH)
        print(f"索引已加载，修改时间: {_last_mtime}")
    else:
        _vectorstore = None
        _last_mtime = 0
        print("索引文件不存在")

def get_vectorstore():
    global _vectorstore, _last_mtime
    if os.path.exists(INDEX_PATH):
        current_mtime = os.path.getmtime(INDEX_PATH)
        # 如果索引文件更新了或从未加载，则重新加载
        if current_mtime > _last_mtime or _vectorstore is None:
            print("检测到索引更新，重新加载...")
            _load_vectorstore()
    else:
        _vectorstore = None
        _last_mtime = 0
    return _vectorstore

def retrieve_documents(query, k=5):
    vectorstore = get_vectorstore()
    if vectorstore is None:
        return []
    return vectorstore.similarity_search_with_score(query, k=k)