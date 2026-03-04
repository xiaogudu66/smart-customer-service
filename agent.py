# agent.py
from langchain_core.messages import HumanMessage

from intent_classifier import classify_intent
from query_rewriter import rewrite_query
from retriever import retrieve_documents
from rag_generator import generate_rag_answer
from tools import handle_tool_call
from memory import get_history, add_message
from llm_client import get_llm


def agent_chat(conversation_id, user_query):
    history = get_history(conversation_id)
    intent = classify_intent(user_query, history)

    if intent == "tool":
        answer = handle_tool_call(user_query)
    elif intent == "chat":
        llm = get_llm(temperature=0.7)
        messages = history + [HumanMessage(content=user_query)]
        response = llm.invoke(messages)
        answer = response.content
    else:  # document
        rewritten = rewrite_query(user_query, history)
        docs = retrieve_documents(rewritten, k=5)
        answer = generate_rag_answer(rewritten, docs)

    add_message(conversation_id, "user", user_query)
    add_message(conversation_id, "assistant", answer)
    return answer