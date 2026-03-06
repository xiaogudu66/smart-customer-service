import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from filelock import FileLock  # 需要安装：pip install filelock

# ========== 初始化配置 ==========
print("当前工作目录:", os.getcwd())

# 加载 .env
env_path = Path(".env")
print(".env 文件是否存在:", env_path.exists())
if env_path.exists():
    print(".env 文件内容预览:")
    with open(env_path, "r") as f:
        print(f.read().strip())
load_dotenv(dotenv_path=env_path)

# 检查环境变量
api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")
print("OPENAI_API_KEY 是否已设置:", api_key is not None)
print("OPENAI_API_BASE 是否已设置:", api_base is not None)

if not api_key:
    print("错误：未找到 OPENAI_API_KEY，请检查 .env 文件。")
    exit(1)

# 创建全局 embeddings 对象
embeddings = OpenAIEmbeddings(
    model="text-embedding-ada-002",
    openai_api_key=api_key,
    openai_api_base=api_base
)

# FAISS 索引路径
INDEX_PATH = "./faiss_index"
LOCK_PATH = INDEX_PATH + ".lock"  # 用于并发控制的锁文件


# ========== 文档加载函数 ==========
def load_document(file_path):
    """根据文件扩展名加载文档"""
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext in [".txt", ".md"]:
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"不支持的文件类型: {ext}")
    return loader.load()


# ========== 文档处理函数（增量添加） ==========
def process_document(file_path):
    """处理单个文档，合并到主索引"""
    print(f"正在处理文件: {file_path}")

    # 1. 加载文档
    documents = load_document(file_path)
    print(f"加载了 {len(documents)} 页/段")

    # 2. 文本分块
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", "。", "，", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"生成了 {len(chunks)} 个文本块")

    # 3. 使用文件锁确保线程安全
    lock = FileLock(LOCK_PATH, timeout=60)  # 等待锁最多60秒
    with lock:
        # 加载现有索引（如果存在），否则创建新索引
        if os.path.exists(INDEX_PATH):
            vectorstore = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
            vectorstore.add_documents(chunks)
            print("已添加到现有索引")
        else:
            vectorstore = FAISS.from_documents(chunks, embeddings)
            print("创建新索引")

        # 保存索引
        vectorstore.save_local(INDEX_PATH)
        print(f"索引已保存到 {INDEX_PATH}")


# ========== 创建初始索引（用于直接运行脚本） ==========
def create_initial_index():
    """处理 employee_handbook.pdf 并创建初始 FAISS 索引"""
    pdf_path = "employee_handbook.pdf"
    if not os.path.exists(pdf_path):
        print(f"错误：找不到文件 {pdf_path}")
        return

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    print(f"加载了 {len(documents)} 页")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", "。", "，", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"生成了 {len(chunks)} 个文本块")

    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(INDEX_PATH)
    print(f"初始 FAISS 向量数据库已创建并保存到 {INDEX_PATH}")


# ========== 主程序入口 ==========
if __name__ == "__main__":
    # 如果命令行提供了参数，则处理指定文件
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        process_document(file_path)
    else:
        # 否则执行原有功能：处理 employee_handbook.pdf 创建初始索引
        create_initial_index()