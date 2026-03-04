# intent_classifier.py
from llm_client import get_llm
from langchain_core.messages import SystemMessage, HumanMessage


def classify_intent(query, history=None):
    llm = get_llm(temperature=0)
    system_prompt = """
    你是一个意图分类器。请根据用户的问题，判断它属于哪一类：
    - document：需要查询内部知识库，例如询问公司政策、产品信息、操作指南等。
    - tool：需要调用外部API获取实时数据，例如查快递、查天气、查订单状态等。
    - chat：日常闲聊、问候、感谢、情感表达等。

    请只输出一个单词：document、tool 或 chat。
    """
    messages = [SystemMessage(content=system_prompt)]
    if history:
        for msg in history[-2:]:
            messages.append(msg)
    messages.append(HumanMessage(content=query))

    response = llm.invoke(messages)
    intent = response.content.strip().lower()
    if intent not in ["document", "tool", "chat"]:
        intent = "document"
    return intent