# tools.py
import json
from llm_client import get_llm
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

tools = [
    {
        "type": "function",
        "function": {
            "name": "track_delivery",
            "description": "查询快递物流状态",
            "parameters": {
                "type": "object",
                "properties": {
                    "tracking_number": {
                        "type": "string",
                        "description": "快递单号"
                    }
                },
                "required": ["tracking_number"]
            }
        }
    }
]


def track_delivery_api(tracking_number):
    # 模拟API调用，实际可替换为 requests.get(...)
    return f"快递单号 {tracking_number} 的当前状态：已签收。"


def handle_tool_call(query):
    llm = get_llm(temperature=0)
    response = llm.invoke(
        [HumanMessage(content=query)],
        tools=tools,
        tool_choice="auto"
    )

    if response.tool_calls:
        tool_call = response.tool_calls[0]
        if tool_call["name"] == "track_delivery":
            args = tool_call["args"]
            if isinstance(args, str):
                args = json.loads(args)
            # 现在 args 是字典，可以直接使用
            tracking_number = args.get("tracking_number")
            result = track_delivery_api(tracking_number)
            messages = [
                HumanMessage(content=query),
                AIMessage(content="", tool_calls=response.tool_calls),
                ToolMessage(content=result, tool_call_id=tool_call["id"])
            ]
            final_response = llm.invoke(messages)
            return final_response.content
    else:
        return response.content