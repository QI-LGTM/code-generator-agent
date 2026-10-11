from  langchain_openai import  ChatOpenAI
from  .config import Config#.为当前包src，调用config即配置类

def get_llm():
    #返回LLM实例
    return ChatOpenAI(
        api_key=Config.LLM_API_KEY,
        base_url=Config.LLM_BASE_URL,
        model=Config.LLM_MODEL,
        temperature=Config.TEMPERATURE,
        timeout=60,
        max_retries=Config.MAX_RETRY,#最大重试
    )