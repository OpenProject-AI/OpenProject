from Functions import ActionManage, GetPromptFile, MessagesHistoryManage, RequestAPI, ConfigManage
import json
import re
import os
import logging
from abc import ABC, abstractmethod

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BaseChatManager(ABC):
    def __init__(self):
        self.base_url = ConfigManage.wnGet('BASE_URL')
        self.api_key = ConfigManage.wnGet('API_KEY')
        self.model_name = ConfigManage.wnGet('MODEL_NAME')
        self.prompt = GetPromptFile.GetPromptFile(base_dir=os.path.dirname(os.path.abspath(__file__)))
        self.chat_history = [
            {"role": "system", "content": self.prompt}
        ]

    @abstractmethod
    def get_api_response(self):
        """获取API响应，由子类实现"""
        pass

    def handle_api_response(self, cback):
        """处理API响应"""
        response = RequestAPI.OpenAI_API_Cback_To_Text(cback)
        self.chat_history.append({"role": "assistant", "content": response})
        return response

    def handle_action(self, response):
        """处理动作指令"""
        action = ActionManage.get_action_content(response)
        if action:
            return ActionManage.action_runner(action)
        return None

    def process_chat_round(self, user_input, length_limit=10):
        """处理一轮对话的核心逻辑"""
        # 添加用户输入到历史记录
        self.chat_history.append({"role": "user", "content": user_input})

        # 获取API响应
        cback = self.get_api_response()

        # 处理响应
        response = self.handle_api_response(cback)
        MessagesHistoryManage.LimitMessagesHistoryLength(self.chat_history, length_limit)

        # 处理动作
        action_cback = self.handle_action(response)
        if action_cback:
            return {
                "chat_history": self.chat_history,
                "action_cback": action_cback,
                "use_action": True
            }

        # 处理思考过程
        if RequestAPI.Check_ThinkText(cback):
            think_text = RequestAPI.OpenAI_API_Cback_To_ThinkText(cback)
            return {
                "chat_history": self.chat_history,
                "think_text": think_text,
                "action_cback": None,
                "use_action": False
            }

        return {
            "chat_history": self.chat_history,
            "action_cback": None,
            "use_action": False
        }

class ChatManager(BaseChatManager):
    def get_api_response(self):
        """实现OpenAI API响应获取"""
        return RequestAPI.OpenAI_Format_API(
            base_url=self.base_url,
            api_key=self.api_key,
            model=self.model_name,
            history=self.chat_history
        )

def main():
    chat_manager = ChatManager()
    while True:
        try:
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
                
        except KeyError as e:
            logging.error(f"配置错误或网络连接失败: {str(e)}")
            print(f"检查你的配置信息/网络连接是否正确！{str(e)}")
        except Exception as e:
            logging.error(f"发生未知错误: {str(e)}")
            print(f"发生错误，请联系作者！\n{str(e)}")

if __name__ == '__main__':
    main()