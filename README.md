```
#代码生成Agent
## 项目简介
基于LangGraph + LangChain实现的智能代码生成Agent，支持通过自然语言描述生成Python代码。内置代码执行、文件保存、文件读取三类工具，具备完整的Agent推理-行动循环能力，提供Streamlit可视化Web交互界面。

## 功能特性
- ✅ 自然语言生成Python代码，符合PEP8规范
- ✅ 独立子进程执行代码，自带超时保护，自动验证运行结果
- ✅ 支持代码保存到本地文件、读取本地文件内容
- ✅ 完整ReAct Agent循环：推理→调用工具→观察结果→输出结论
- ✅ 多轮对话上下文记忆，支持代码迭代修改
- ✅ Streamlit Web界面，实时展示工具调用过程
- ✅ 完善的异常处理与边界情况兼容

## 技术栈
- 编程语言：Python 3.10+
- Agent框架：LangGraph（ReAct模式）、LangChain
- Web界面：Streamlit
- 大模型：兼容OpenAI API协议的任意大模型

## 快速开始
安装依赖
​```bash
pip install -r requirements.txt
```

```
streamlit run app.py
```

浏览器自动访问 `http://localhost:8501` 即可使用。

1. 在输入框中描述需要实现的代码功能
2. Agent 会自动生成代码，并根据需求调用工具执行验证
3. 可要求 Agent 将代码保存为本地文件，或读取本地文件内容
4. 支持多轮对话，可基于已有代码继续修改优化