# app.py
import shutil
import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from agent import agent_chat
from prepare_data import process_document
import uvicorn

# 创建单个 FastAPI 实例，设置最大请求体为 100MB
app = FastAPI(
    title="智能客服API",
    max_request_body_size=100_000_000  # 100MB
)

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------- 聊天接口 ----------
class ChatRequest(BaseModel):
    conversation_id: str
    query: str

class ChatResponse(BaseModel):
    conversation_id: str
    answer: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    answer = agent_chat(request.conversation_id, request.query)
    return ChatResponse(conversation_id=request.conversation_id, answer=answer)

@app.get("/health")
async def health():
    return {"status": "ok"}

# ---------- 文件上传接口 ----------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # 检查文件类型
    allowed_extensions = [".pdf", ".txt", ".md"]
    ext = os.path.splitext(file.filename)[-1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="不支持的文件类型")

    # 保存上传的文件到临时目录
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 处理文档：解析、分块、生成嵌入、添加到现有 FAISS 索引
        process_document(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理文档失败: {str(e)}")
    finally:
        # 可选：删除临时文件
        os.remove(file_path)

    return {"message": f"文件 {file.filename} 已成功添加到知识库"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)