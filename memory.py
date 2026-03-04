# memory.py
from langchain_core.messages import HumanMessage, AIMessage

conversation_memory = {}

def get_history(conversation_id):
    return conversation_memory.get(conversation_id, [])

def add_message(conversation_id, role, content):
    if conversation_id not in conversation_memory:
        conversation_memory[conversation_id] = []
    msg = HumanMessage(content=content) if role == "user" else AIMessage(content=content)
    conversation_memory[conversation_id].append(msg)
    # 保留最近10轮（20条）
    if len(conversation_memory[conversation_id]) > 20:
        conversation_memory[conversation_id] = conversation_memory[conversation_id][-20:]