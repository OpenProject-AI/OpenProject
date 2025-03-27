import httpx
import json
import asyncio
import re
import logging

# 配置日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 添加控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logger.addHandler(console_handler)

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
    
    try:
        cback.raise_for_status()
        logger.info(f"HTTP Request: POST {api_url} \"{cback.status_code} {cback.reason_phrase}\"")
        logger.debug(f"Request Headers: {headers}")
        logger.debug(f"Request Data: {data}")
        
        response = cback.json()
        return response
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP状态错误: {e.response.status_code} - {e.response.text}")
        raise
    except httpx.RequestError as e:
        logger.error(f"网络请求错误: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise

def Ollama_Format_API(base_url, model, history: list = [], max_retries: int = 3):
    """
    Ollama 格式API的BaseURL格式为： https://{domain}/api
    参数解释：
    - base_url: Ollama 格式API的域名
    - model: 使用的模型名称
    - history: 历史消息列表，表示一条消息，如[{"role": "user", "content": "你好"}]，其中role是角色，可填写"user"或"system"（即prompt）或assistant，content是消息内容
    - max_retries: 最大重试次数
    """
    headers = {
        "Content-Type": "application/json"
    }
    api_url = f"{base_url}/chat"
    data = {
        "model": model,
        "messages": history,
        "stream": False
    }
    
    for attempt in range(max_retries):
        try:
            logger.info(f"正在调用Ollama API，第{attempt + 1}次尝试...")
            cback = httpx.post(
                api_url,
                headers=headers,
                json=data,
                timeout=200
            )
            cback.raise_for_status()
            response = cback.json()
            
            if "error" in response:
                raise Exception(f"Ollama API返回错误: {response['error']}")
                
            logger.info("Ollama API调用成功")
            return response
            
        except (httpx.HTTPStatusError, httpx.RequestError, Exception) as e:
            error_msg = {
                httpx.HTTPStatusError: f"HTTP状态错误: {getattr(e, 'response', {}).get('status_code', '')} - {getattr(e, 'response', {}).get('text', '')}",
                httpx.RequestError: f"网络请求错误: {str(e)}",
                Exception: f"未预期的错误: {str(e)}"
            }.get(type(e), f"未知错误: {str(e)}")
            
            logger.error(error_msg)
            if attempt == max_retries - 1:
                raise
            
            wait_time = (attempt + 1) * 2
            logger.info(f"等待{wait_time}秒后重试...")
            asyncio.sleep(wait_time)

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
    # 设置调试模式
    logger.setLevel(logging.DEBUG)
    
    # 示例代码
    base_url = "http://localhost:11434/api"
    model = "llama2"
    history = [
        {"role": "user", "content": "你是谁？"}
    ]
    try:
        result = Ollama_Format_API(base_url, model, history)
        print(result["message"]["content"])
    except Exception as e:
        logger.error(f"API调用失败: {str(e)}")