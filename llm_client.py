# llm_client.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")

def get_llm(model="gpt-3.5-turbo", temperature=0):
    """返回一个配置好的 ChatOpenAI 实例"""
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        openai_api_key=api_key,
        openai_api_base=api_base
    )