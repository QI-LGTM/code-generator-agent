from langgraph.prebuilt import create_react_agent #四种消息，系统提示词、用户输入、ai回复、工具执行结果
from langchain_core.messages import SystemMessage,HumanMessage,AIMessage,ToolMessage
from langchain_core.chat_history import BaseChatMessageHistory#会话历史的抽象基类
from typing import List#类型注解用
from .llm import get_llm
from .tools import get_tool
from .config import Config


SYSTEM_PROMPT="""你是一名专业的代码生成助手，根据用户的自然语言描述生成高质量的、可运行的py代码
工作流程：
1.理解用户需求，分析需要实现的功能
2.生成规范、健壮、带注释的py代码
3、必要时调用execute_python_code工具验证代码是否可运行，验证代码必须包含print语句输出结果
4.如果代码执行出错，分析原因并修正代码后重新验证
5.用户需要保存代码时，调用save_code_to_file工具保存文件
6.用户需要查看文件时，调用read_file工具读取内容

代码生成要求：
符合pep8规范，包含清晰注释
处理边界情况和异常
尽量使用标准库，减少第三方依赖
生成完成后给出简洁的代码说明和使用方法
"""


class InMemoryHistory(BaseChatMessageHistory):
    def __init__(self):
        self._messages: List = []

    @property
    def messages(self)->List:
        return self._messages

    def add_message(self,message)->None:
        self._messages.append(message)

    def add_user_message(self, message: str) -> None:
        self._messages.append(HumanMessage(content=message))

    def add_ai_message(self, message: str) -> None:
        self._messages.append(AIMessage(content=message))

    def clear(self)->None:
        self._messages = []


session_store: dict = {}


def get_session_history(session_id: str) -> InMemoryHistory:
    if session_id not in session_store:
        session_store[session_id] = InMemoryHistory()
    return session_store[session_id]


_agent = None


def get_agent():
    global _agent
    if _agent is None:
        llm = get_llm()
        tools = get_tool()
        _agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt=SystemMessage(content=SYSTEM_PROMPT),
        )
    return _agent


def stream_chat(user_input: str, session_id: str = "default"):
    agent = get_agent()
    history = get_session_history(session_id)

    messages = history.messages + [HumanMessage(content=user_input)]

    final_ai_content = ""

    for event in agent.stream({"messages": messages}, stream_mode="values"):
        last_msg = event["messages"][-1]
        yield last_msg
        if isinstance(last_msg, AIMessage) and last_msg.content:
            final_ai_content = last_msg.content

    history.add_user_message(user_input)
    if final_ai_content:
        history.add_ai_message(final_ai_content)
