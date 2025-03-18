import httpx
import json
import asyncio
import re

def OpenAI_Format_API(base_url, api_key, model, history: list = []):
    """
    请注意：
    BaseURL需为：https://{domain}/{OpenAI_API_PATH}/v1  （结尾不加斜杠!!）
    
    参数解释：
    - base_url: OpenAI 格式API的域名
    - api_key: API 密钥
    - model: 使用的模型名称
    - history: 历史消息列表，表示一条消息，如[{"role": "user", "content": "你好"}]，其中role是角色，可填写"user"或"system"（即prompt），content是消息内容
    """
    # 定义参数，请求头等基本内容
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    api_url = f"{base_url}/chat/completions"
    data = {
        "model": model,
        "messages": history
    }
    cback = httpx.post(
        api_url,
        headers = headers,
        json = data,
        timeout=200
    )
    return cback.json()

def Ollama_Format_API(base_url, model, history: list = []):
    """
    Ollama 格式API的BaseURL格式为： https://{domain}/api
    参数解释：
    - base_url: Ollama 格式API的域名
    - model: 使用的模型名称
    - history: 历史消息列表，表示一条消息，如[{"role": "user", "content": "你好"}]，其中role是角色，可填写"user"或"system"（即prompt）或assistant，content是消息内容
    """
    # 定义参数，请求头等基本内容
    headers = {
        "Content-Type": "application/json"
    }
    api_url = f"{base_url}/chat"
    data = {
        "model": model,
        "messages": history,
        "stream": False
    }
    cback = httpx.post(
        api_url,
        headers = headers,
        json = data,
        timeout=200
    )
    return cback.json()

def OpenAI_API_Cback_To_Text(cback):
    """
    将OpenAI API返回的json格式的结果转换为文本格式
    """
    return cback["choices"][0]["message"]["content"]

def OpenAI_API_Cback_To_ThinkText(cback):
    """
    将OpenAI API返回的json格式的结果转换模型思考的输出
    """
    content = cback["choices"][0]["message"]["content"]
    # 使用正则表达式提取在<think>到</think>之间的文本
    match = re.search(r'<think>(.*?)</think>', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        return "No think text found"

def Check_ThinkText(cback):
    """
    检查模型思考的输出是否存在
    """
    content = cback["choices"][0]["message"]["content"]
    # 使用正则表达式检查是否存在<think>和</think>标签
    match = re.search(r'<think>(.*?)</think>', content, re.DOTALL)
    if match:
        return True
    else:
        return False
    

if __name__ == '__main__':
    # 示例代码
    base_url = "http://125.122.157.239:9009/api"
    api_key = "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"
    model = "deepseek-r1:1.5b"
    history = [
        {"role": "user", "content": "你是谁？"}
    ]
    result = Ollama_Format_API(base_url, model, history)
    print(result["message"]["content"])