import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # 添加上级目录到搜索路径
from main import BaseChatManager
from Functions import RequestAPI
import logging

logger = logging.getLogger(__name__)

class OllamaChatManager(BaseChatManager):
    def __init__(self):
        super().__init__()
        self.api_type = "ollama"
        
    def get_api_response(self):
        """实现Ollama API响应获取"""
        try:
            response = RequestAPI.Ollama_Format_API(
                base_url=self.base_url,
                model=self.model_name,
                history=self.chat_history
            )
            if "error" in response:
                raise Exception(f"Ollama API错误: {response['error']}")
            return response
        except Exception as e:
            logger.error(f"Ollama API调用失败: {str(e)}")
            raise

def app():
    """主函数"""
    chat_manager = OllamaChatManager()
    while True:
        user_input = input("User >> ")
        result = chat_manager.process_chat_round(user_input)
        
        while result["use_action"]:
            print("Assistant >> " + str(result["action_cback"]))
            result = chat_manager.process_chat_round(result["action_cback"])
            
        response = result["chat_history"][-1]["content"]
        if "</think>" in response:
            print("Assistant >> " + response.split("</think>")[1])
        else:
            print("Assistant >> " + response)