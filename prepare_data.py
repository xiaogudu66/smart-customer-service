import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings          # 使用新的包
from langchain_community.vectorstores import FAISS

# 打印当前工作目录
print("当前工作目录:", os.getcwd())

# 检查 .env 文件是否存在
env_path = Path(".env")
print(".env 文件是否存在:", env_path.exists())
if env_path.exists():
    print(".env 文件内容预览:")
    with open(env_path, "r") as f:
        print(f.read().strip())

# 加载 .env
load_dotenv(dotenv_path=env_path)

# 检查环境变量
api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")
print("OPENAI_API_KEY 是否已设置:", api_key is not None)
print("OPENAI_API_BASE 是否已设置:", api_base is not None)

if not api_key:
    print("错误：未找到 OPENAI_API_KEY，请检查 .env 文件。")
    exit(1)

# 加载 PDF
pdf_path = "employee_handbook.pdf"
if not os.path.exists(pdf_path):
    print(f"错误：找不到文件 {pdf_path}")
    exit(1)

loader = PyPDFLoader(pdf_path)
documents = loader.load()
print(f"加载了 {len(documents)} 页")

# 文本分块
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
    separators=["\n\n", "\n", "。", "，", " ", ""]
)
chunks = text_splitter.split_documents(documents)
print(f"生成了 {len(chunks)} 个文本块")

# 初始化 Embedding（使用新包，参数不变）
embeddings = OpenAIEmbeddings(
    model="text-embedding-ada-002",
    openai_api_key=api_key,
    openai_api_base=api_base
)

# 创建 FAISS 向量数据库并保存到本地
persist_directory = "./faiss_index"
vectorstore = FAISS.from_documents(
    documents=chunks,
    embedding=embeddings
)
vectorstore.save_local(persist_directory)  # 保存到本地
print(f"FAISS 向量数据库已创建并保存到 {persist_directory}")