import streamlit as st
import uuid
from langchain_core.messages import AIMessage, ToolMessage
from src.agent import stream_chat
st.set_page_config(
    page_title="代码生成Agent",
    page_icon="💻",
    layout="wide",
)
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "你好！我是代码生成助手，请描述你需要实现的功能。"}
    ]
st.title("💻 代码生成Agent")
st.caption("基于 LangGraph + LangChain 实现的智能代码生成助手 | 支持代码执行 / 文件保存 / 文件读取")
with st.sidebar:
    st.header("⚙️ 功能面板")
    st.markdown("""
    **✅ 核心能力**
    - 自然语言生成Python代码
    - 隔离环境执行验证代码
    - 保存代码到本地文件
    - 读取本地文件内容
    - 多轮对话上下文记忆

    **🛠️ 内置工具**
    1. `execute_python_code` - 代码执行器
    2. `save_code_to_file` - 文件保存
    3. `read_file` - 文件读取
    """)

    st.divider()
    if st.button("🔄 清空对话", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = [
            {"role": "assistant", "content": "对话已重置，请描述你需要实现的功能。"}
        ]
        st.rerun()
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "tool_calls" in msg and msg["tool_calls"]:
            for tc in msg["tool_calls"]:
                with st.expander(f"🛠️ 调用工具: {tc['name']}"):
                    st.json(tc["args"])
                    if "result" in tc:
                        st.text(tc["result"])
        st.markdown(msg["content"])
if user_input := st.chat_input("请输入代码需求，例如：写一个冒泡排序并执行验证"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        pending_tool_calls = {}

        for message in stream_chat(user_input, st.session_state.session_id):
            if isinstance(message, AIMessage):
                if message.tool_calls:
                    for tc in message.tool_calls:
                        pending_tool_calls[tc["id"]] = {"name": tc["name"], "args": tc["args"]}
                        with st.expander(f"🧠 Agent决策 → 调用工具: {tc['name']}"):
                            st.json(tc["args"])
                if message.content:
                    full_response = message.content
                    message_placeholder.markdown(full_response + "▌")

            elif isinstance(message, ToolMessage):
                tool_info = pending_tool_calls.get(message.tool_call_id, {"name": "unknown", "args": {}})
                with st.expander(f"🛠️ 工具执行结果: {tool_info['name']}"):
                    st.json(tool_info["args"])
                    st.text(message.content)

        message_placeholder.markdown(full_response)
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "tool_calls": [
            {"name": v["name"], "args": v["args"], "result": ""}
            for v in pending_tool_calls.values()
        ],
    })
