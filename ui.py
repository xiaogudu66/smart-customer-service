import streamlit as st
import requests
import json
import uuid  # 新增导入

st.set_page_config(page_title="智能客服", page_icon="💬")
st.title("💬 智能客服")

# 初始化会话状态
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())  # 使用 uuid 生成唯一 ID
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 处理用户输入
if prompt := st.chat_input("请输入你的问题..."):
    # 添加用户消息到界面
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 调用后端 API
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                response = requests.post(
                    "http://localhost:8000/chat",
                    json={
                        "conversation_id": st.session_state.conversation_id,
                        "query": prompt
                    },
                    timeout=30
                )
                if response.status_code == 200:
                    answer = response.json()["answer"]
                else:
                    answer = f"错误：{response.status_code} - {response.text}"
            except Exception as e:
                answer = f"请求失败：{str(e)}"

        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

# ui.py (在原文件基础上添加)
import streamlit as st
import requests
import uuid

# ... 原有的页面配置和聊天逻辑 ...

# 在侧边栏添加上传区域
with st.sidebar:
    st.header("📤 扩展知识库")
    uploaded_file = st.file_uploader("上传新文档 (PDF/TXT/MD)", type=["pdf", "txt", "md"])

    if uploaded_file is not None:
        # 显示上传按钮
        if st.button("开始上传并处理"):
            with st.spinner("正在处理文档，请稍候..."):
                # 准备文件
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                try:
                    response = requests.post("http://localhost:8000/upload", files=files, timeout=300)
                    if response.status_code == 200:
                        st.success(f"✅ 文档已成功添加到知识库！")
                    else:
                        st.error(f"❌ 处理失败：{response.json().get('detail', '未知错误')}")
                except Exception as e:
                    st.error(f"❌ 请求异常：{str(e)}")

    st.divider()
    st.markdown("### 当前会话ID")
    st.code(st.session_state.conversation_id)

# ... 原有的聊天界面代码保持不变 ...
