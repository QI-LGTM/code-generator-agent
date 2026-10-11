import os
from dotenv import load_dotenv #读取env文件

load_dotenv()

class Config:
    LLM_API_KEY=os.getenv("LLM_API_KEY","")#密钥
    LLM_BASE_URL=os.getenv("LLM_BASE_URL","https://dashscope.aliyuncs.com/compatible-mode/v1")#地址
    LLM_MODEL=os.getenv("LLM_MODEL","qwen-plus")
    TEMPERATURE=0.1#低随机性，避免每次生成代码不一致
    MAX_RETRY=3#调用失败上限为3次，防止网络波动
    CODE_TIMEOUT=10#代码执行超时为10秒，防止死循环
    MAX_HISTORY_TURNS=20#保留20轮对话，防止上下文溢出


