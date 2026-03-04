# rag_generator.py
from llm_client import get_llm
from langchain_core.messages import SystemMessage, HumanMessage


def generate_rag_answer(query, retrieved_docs):
    context = "\n\n".join([doc.page_content for doc, _ in retrieved_docs[:3]])

    system_prompt = f"""
    你是一个专业的客服助手。请根据以下参考资料回答用户的问题。
    如果参考资料中没有相关信息，请诚实地回答“我不知道”，不要编造。
    回答末尾请附上参考来源的页码（如果有）。

    参考资料：
    {context}
    """

    llm = get_llm(temperature=0.3)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=query)
    ]
    response = llm.invoke(messages)
    return response.content