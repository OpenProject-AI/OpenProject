import os
import json
import re
import httpx as requests
import subprocess
from urllib.parse import urlparse

# 配置文件路径
CONFIG_PATH = os.path.expanduser("~/.greatai_config.json")
PROMPT_PATH = os.path.join(os.path.dirname(__file__), "Functions", "prompt.txt")

# 默认配置
DEFAULT_CONFIG = {
    "api_config": {
        "api_url": "",
        "api_key": "",
        "model_name": ""
    },
    "security": {
        "enable": True,
        "mode": "strict",
        "base_dir": os.path.expanduser("~"),
        "whitelist": [],
        "blacklist": []
    }
}

# 上下文管理
MAX_CONTEXT_LENGTH = 8
context_history = []

def load_prompt():
    """动态加载提示文件"""
    try:
        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ 关键文件缺失：{PROMPT_PATH}")
        print("请确保存在Function/prompt.txt文件")
        exit(1)
    except Exception as e:
        print(f"⚠️ 提示文件读取失败: {str(e)}")
        exit(1)

def load_config():
    """加载或初始化配置"""
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                saved_config = json.load(f)
            # 合并配置确保完整性
            config = DEFAULT_CONFIG.copy()
            config.update(saved_config)
            return config
        return create_new_config()
    except Exception as e:
        print(f"⚠️ 配置加载失败: {str(e)}，使用默认配置")
        return DEFAULT_CONFIG.copy()

def create_new_config():
    """创建新配置文件"""
    config = DEFAULT_CONFIG.copy()
    config = init_api_config(config)
    config = init_security_config(config)
    save_config(config)
    return config

def init_api_config(config):
    """API配置初始化向导"""
    print("\n🚀 首次API配置向导 ".center(50, "="))
    config["api_config"]["api_url"] = input("请输入OpenAI API Base-URL: ").strip()
    config["api_config"]["api_key"] = input("请输入OpenAI API Key: ").strip()
    config["api_config"]["model_name"] = input("请输入模型名称 (如 gpt-3.5-turbo): ").strip()
    return config

def init_security_config(config):
    """安全配置初始化向导"""
    print("\n🔒 安全配置向导 ".center(50, "="))
    enable = input("是否启用路径安全限制？(Y/n): ").lower() != "n"
    config["security"]["enable"] = enable
    
    if enable:
        print("\n请选择安全模式：")
        print("1. 严格模式（仅允许操作基础目录下的文件）")
        print("2. 白名单模式（仅允许指定目录）")
        print("3. 黑名单模式（禁止指定目录）")
        choice = input("请输入选项 (1/2/3): ").strip()
        
        if choice == "1":
            base = input(f"基础目录（默认：{os.path.expanduser('~')}）: ") or os.path.expanduser("~")
            config["security"].update({
                "mode": "strict",
                "base_dir": os.path.abspath(base)
            })
        elif choice == "2":
            paths = input("允许的目录（多个用分号分隔）: ").split(";")
            config["security"].update({
                "mode": "whitelist",
                "whitelist": [os.path.abspath(p.strip()) for p in paths if p.strip()]
            })
        elif choice == "3":
            paths = input("禁止的目录（多个用分号分隔）: ").split(";")
            config["security"].update({
                "mode": "blacklist",
                "blacklist": [os.path.abspath(p.strip()) for p in paths if p.strip()]
            })
    return config

def save_config(config):
    """保存配置到文件"""
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    print(f"✅ 配置已保存至 {CONFIG_PATH}")

def check_api_config(config):
    """检查API配置是否完整"""
    api = config.get("api_config", {})
    return all([api.get("api_url"), api.get("api_key"), api.get("model_name")])

def validate_project_structure():
    """验证项目文件结构完整性"""
    required_files = {
        PROMPT_PATH: "系统提示文件"
    }
    
    missing = []
    for path, desc in required_files.items():
        if not os.path.exists(path):
            missing.append(f"{desc}: {path}")
    
    if missing:
        print("⚠️ 项目文件结构不完整，缺少以下关键文件：")
        for item in missing:
            print(f" - {item}")
        exit(1)

def send_to_openrouter(prompt, api_url, api_key, model_name):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": context_history + [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"API请求失败：{str(e)}"

def main():
    validate_project_structure()
    
    # 初始化配置
    config = load_config()
    
    # 检查API配置
    if not check_api_config(config):
        print("\n⚠️ 检测到API配置不完整")
        config = init_api_config(config)
        save_config(config)
    
    # 获取API参数
    API_URL = config["api_config"]["api_url"]
    API_KEY = config["api_config"]["api_key"]
    MODEL_NAME = config["api_config"]["model_name"]
    
    # 加载提示语
    global context_history
    context_history = [{"role": "system", "content": load_prompt()}]
    
    print("\n" + "="*40)
    print(f"🔧 当前配置状态")
    print(f"API端点: {API_URL}")
    print(f"模型名称: {MODEL_NAME}")
    print(f"安全模式: {'启用' if config['security']['enable'] else '停用'}")
    print("="*40 + "\n")
    
    # 主循环
    print("智能助手已启动，输入'exit'退出")
    print("输入 'security config' 可修改安全设置")
    
    while True:
        user_input = input("\n用户：").strip()
        
        if user_input.lower() == "exit":
            break
            
        if user_input.lower() == "security config":
            update_security_setting(config)
            continue

        # 发送请求并处理响应
        raw_response = send_to_openrouter(user_input, API_URL, API_KEY, MODEL_NAME)
        print(f"\n助手：{raw_response}")

if __name__ == "__main__":
    main()