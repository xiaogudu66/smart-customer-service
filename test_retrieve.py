# test_retrieve.py
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings          # 使用新的推荐包
from langchain_community.vectorstores import FAISS

# 1. 加载 .env 文件中的环境变量
env_path = Path(".env")
load_dotenv(dotenv_path=env_path)

# 2. 从环境变量读取配置
api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")

# 3. 调试：检查是否读取成功（可删除）
print("API Key 是否存在:", api_key is not None)
print("API Base:", api_base)

if not api_key:
    raise ValueError("未找到 OPENAI_API_KEY，请检查 .env 文件")

# 4. 初始化 Embedding（显式传递参数）
embeddings = OpenAIEmbeddings(
    model="text-embedding-ada-002",
    openai_api_key=api_key,
    openai_api_base=api_base
)

# 5. 加载之前保存的 FAISS 索引
#    allow_dangerous_deserialization=True 是安全的，因为我们信任自己生成的文件
vectorstore = FAISS.load_local(
    "./faiss_index", 
    embeddings, 
    allow_dangerous_deserialization=True
)

# 6. 测试检索
query = "年假有多少天？"
docs = vectorstore.similarity_search_with_score(query, k=3)
print(f"\n查询：{query}\n")
for i, (doc, score) in enumerate(docs):
    print(f"结果 {i+1} (相似度分数: {score:.4f}):")
    print(doc.page_content)
    print("-" * 60)