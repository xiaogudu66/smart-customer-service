# query_rewriter.py
from llm_client import get_llm
from langchain_core.messages import HumanMessage


def rewrite_query(query, history):
    if not history:
        return query

    history_text = ""
    for msg in history[-4:]:
        role = "用户" if msg.type == "human" else "助手"
        history_text += f"{role}: {msg.content}\n"

    prompt = f"""
    对话历史：
    {history_text}

    当前用户问题：{query}

    请将当前问题改写为一个适合在知识库中检索的独立问句，消除指代，保持原意。只输出改写后的问句。
    """
    llm = get_llm(temperature=0)
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()