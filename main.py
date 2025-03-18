from Functions import ActionManage, GetPromptFile, MessagesHistoryManage, RequestAPI, ConfigManage
import json
import re
import os

BASE_URL = ConfigManage.wnGet('BASE_URL')
API_KEY = ConfigManage.wnGet('API_KEY')
MODEL_NAME = ConfigManage.wnGet('MODEL_NAME')


prompt = GetPromptFile.GetPromptFile(base_dir=os.path.dirname(os.path.abspath(__file__)))
chat_history = [
    {
        "role": "system",
        "content": prompt
    }
]

def round_chat(chat_history: list, user_input, length_limit=10):
    """
    一轮对话，获取
    """
    # 导入全局变量，配置信息
    global BASE_URL, API_KEY, MODEL_NAME
    # 将用户输入加入上下文
    chat_history.append(
        {
            "role": "user",
            "content": user_input
        }
    )
    # 调用RequestAPI模块，向OpenAI API发送请求
    cback = RequestAPI.OpenAI_Format_API(
        base_url=BASE_URL,
        api_key=API_KEY,
        model=MODEL_NAME,
        history=chat_history
    )
    # 将OpenAI API的返回结果转化为文本
    # 错误打点
    response = RequestAPI.OpenAI_API_Cback_To_Text(cback)
    # 将文本加入上下文
    chat_history.append(
        {
            "role": "assistant",
            "content": response
        }
    )
    MessagesHistoryManage.LimitMessagesHistoryLength(chat_history, length_limit)  # 限制上下文长度
    action = ActionManage.wnGetActionContent(response)  # 获取动作指令
    if action != None:  # 如果存在动作指令，则执行动作，如果没有，则返回None
        action_cback = ActionManage.action_runner(action)
        chat_history = action_round(chat_history, action_cback)["chat_history"]  # 修补漏洞
    else:
        action_cback = None
    # 判断是否包含思考过程
    if not RequestAPI.Check_ThinkText(cback):
        return {
            "chat_history": chat_history,
            "action_cback": action_cback
        }
    else:
        think_text = RequestAPI.OpenAI_API_Cback_To_ThinkText(cback)
        return {
            "chat_history": chat_history,
            "think_text": think_text,
            "action_cback": action_cback
        }

def action_round(chat_history: list, action_cback: dict):
    """
    把动作结果给AI
    """
    # 导入全局变量，配置信息
    global BASE_URL, API_KEY, MODEL_NAME
    # 将动作结果加入上下文
    chat_history.append(
        {
            "role": "user",
            "content": action_cback
        }
    )
    # 调用RequestAPI模块，向OpenAI API发送请求
    cback = RequestAPI.OpenAI_Format_API(
        base_url=BASE_URL,
        api_key=API_KEY,
        model=MODEL_NAME,
        history=chat_history
    )
    # 将OpenAI API的返回结果转化为文本
    response = RequestAPI.OpenAI_API_Cback_To_Text(cback)
    # 将文本加入上下文
    chat_history.append(
        {
            "role": "assistant",
            "content": response
        }
    )
    return {
        "chat_history": chat_history
    }

if __name__ == '__main__':
    while True:
        user_input = input("User >> ")
        result = round_chat(chat_history, user_input)
        if  "</think>" in result["chat_history"][-1]["content"]:
            print("Assistant >> " + result["chat_history"][-1]["content"].split("</think>")[1])
        else:
            print("Assistant >> " + result["chat_history"][-1]["content"])