import os
import json
import re
import httpx as requests
import subprocess
from urllib.parse import urlparse

# 填写以下信息
API_KEY = ""
API_URL = ""
MODEL_NAME = ""


TIP_TEXT = """
<!-- IMPORTANT -->
你是一个智能操作系统助手，请严格遵循以下规则：

【操作类型】
1. 文件操作（file）: read/write/delete
```json
{"action":"file","operation":"操作","path":"路径"}
```

2. 网络请求（web）: get/post
```json
{"action":"web","method":"请求模式","url":"链接"}
```

3. 命令执行（cmd）: 系统命令
```json
{"action":"cmd","command":"命令"}
```


【输出要求】
● 必须使用严格JSON格式，且用json包裹
● 键顺序固定：action, operation(仅文件), method(仅网络), path/url/command, content/data
● 示例：
```json
{"action":"file","operation":"read","path":"~/doc.txt"}
```
```json
{"action":"web","method":"get","url":"https://api.example.com"}
```
```json
{"action":"cmd","command":"ls -l"}
```

【安全规则】
✖ 禁止解释代码
✖ 禁止添加额外字段
✖ 禁止使用JSON注释
✖ 不要将多个操作放到列表中

【提示】
请在用户需要的时候使用这些命令，可以正常对话（回复时无需构造JSON 响应，此响应只适用于操作。正常对话即可）
建议在对话中（非命令）适当加入 Emoji （非必需）
所有对话不一定全是用户，也有**操作返回**，这不是用户自行操作的，是您的指令的返回，用户并不知道具体的内容
如果用户用的是英文，可以用英文回复，如果用户用的是中文，可以用中文回复。其他语言的回复可以用其他语言的表述。
如果用户提醒你操作/命令错误，请返回你怎么输出的，并让用户反馈至开发者


【响应模板（用户需要你帮他操作）】
[对用户指令的回复]
[命令]

【示例】
我将帮你查询example.txt
```json
{"action":"file","operation":"read","path":"./example.txt"}
```

【响应模板（用户不需要你帮他操作）】
[回复]

【示例】
你好呀！有什么地方需要我呢？😊

"""

# 配置文件路径
CONFIG_PATH = os.path.expanduser("~/.greatai_config.json")
DEFAULT_CONFIG = {
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
context_history = [
    {"role": "system", "content": TIP_TEXT}
]

def load_config():
    """加载或初始化安全配置"""
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)
            if "security" not in config:
                raise ValueError("无效的配置文件格式")
            return config
        return create_new_config()
    except Exception as e:
        print(f"⚠️ 配置加载失败: {str(e)}，使用默认配置")
        return DEFAULT_CONFIG

def create_new_config():
    """创建新配置文件"""
    print("\n🔒 首次安全配置向导 ".center(50, "="))
    enable = input("是否启用路径安全限制？(Y/n): ").lower() != "n"
    
    config = {"security": DEFAULT_CONFIG["security"].copy()}
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
    
    save_config(config)
    return config

def save_config(config):
    """保存配置到文件"""
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    print(f"✅ 配置已保存至 {CONFIG_PATH}")

def update_security_setting():
    """运行时更新安全配置"""
    print("\n🔧 安全配置修改 ".center(50, "="))
    current = config["security"]
    enable = input(f"当前路径安全状态: {'启用' if current['enable'] else '停用'}\n是否修改？(y/N): ").lower() == "y"
    
    if not enable:
        return
    
    new_enable = input("是否启用路径安全限制？(Y/n): ").lower() != "n"
    if new_enable != current["enable"]:
        config["security"]["enable"] = new_enable
        save_config(config)
        print("✅ 已更新路径安全状态")
        return
    
    if not new_enable:
        return
    
    print("\n请选择新的安全模式：")
    print("1. 严格模式\n2. 白名单\n3. 黑名单")
    choice = input("选择模式 (1/2/3): ").strip()
    
    if choice == "1":
        base = input(f"新基础目录（当前：{current['base_dir']}）: ") or current['base_dir']
        config["security"].update({
            "mode": "strict",
            "base_dir": os.path.abspath(base)
        })
    elif choice == "2":
        paths = input("新白名单目录（多个用分号分隔）: ").split(";")
        config["security"].update({
            "mode": "whitelist",
            "whitelist": [os.path.abspath(p.strip()) for p in paths if p.strip()]
        })
    elif choice == "3":
        paths = input("新黑名单目录（多个用分号分隔）: ").split(";")
        config["security"].update({
            "mode": "blacklist",
            "blacklist": [os.path.abspath(p.strip()) for p in paths if p.strip()]
        })
    
    save_config(config)

config = load_config()

def is_path_allowed(path):
    """路径安全检查核心逻辑"""
    if not config["security"]["enable"]:
        return True
    
    abs_path = os.path.abspath(os.path.expanduser(path))
    security = config["security"]
    
    if security["mode"] == "strict":
        return abs_path.startswith(os.path.abspath(security["base_dir"]))
    
    if security["mode"] == "whitelist":
        return any(abs_path.startswith(p) for p in security["whitelist"])
    
    if security["mode"] == "blacklist":
        return not any(abs_path.startswith(p) for p in security["blacklist"])
    
    return False

def extract_json_blocks(text):
    """使用正则表达式增强JSON提取能力"""
    pattern = r'```json\s*(.*?)\s*```'
    matches = re.findall(pattern, text, re.DOTALL)
    valid_actions = []
    
    for match in matches:
        try:
            cleaned = re.sub(r'//.*?$', '', match, flags=re.MULTILINE)
            action = json.loads(cleaned)
            
            if "action" not in action:
                continue
                
            if action["action"] == "file":
                required = ["operation", "path"]
            elif action["action"] == "web":
                required = ["method", "url"]
            elif action["action"] == "cmd":
                required = ["command"]
            else:
                continue
                
            if all(key in action for key in required):
                valid_actions.append(action)
        except:
            continue
            
    return valid_actions

def process_response(response):
    """改进的响应处理逻辑"""
    actions = extract_json_blocks(response)
    clean_response = re.sub(r'```json\s*.*?\s*```', '', response, flags=re.DOTALL)
    clean_response = re.sub(r'【.*?】', '', clean_response).strip()
    
    return clean_response, actions

def validate_action(action):
    """操作指令验证"""
    action_types = {
        "file": {"required": ["operation", "path"], "operations": ["read", "write", "delete"]},
        "web": {"required": ["method", "url"], "methods": ["get", "post"]},
        "cmd": {"required": ["command"]}
    }
    
    if action["action"] not in action_types:
        return False
        
    spec = action_types[action["action"]]
    if not all(key in action for key in spec["required"]):
        return False
        
    if action["action"] == "file" and action["operation"] not in spec["operations"]:
        return False
        
    if action["action"] == "web" and action["method"].lower() not in spec["methods"]:
        return False
        
    return True

def confirm_action(action):
    """增强的确认提示"""
    risk_level = {
        "file": {"read": "低", "write": "中", "delete": "高"},
        "web": {"get": "低", "post": "中"},
        "cmd": "极高"
    }
    
    action_type = action["action"]
    risk = risk_level.get(action_type, "未知")
    
    if action_type == "file":
        risk = risk_level[action_type][action["operation"]]
        abs_path = os.path.abspath(os.path.expanduser(action["path"]))
        print(f"\n📁 文件操作确认 ({risk}风险)")
        print(f"操作类型: {action['operation'].upper()}")
        print(f"目标路径: {abs_path}")
        if "content" in action and len(action["content"]) > 100:
            print(f"内容预览: {action['content'][:100]}...")
    elif action_type == "web":
        risk = risk_level[action_type][action["method"]]
        print(f"\n🌐 网络请求确认 ({risk}风险)")
        print(f"请求方法: {action['method'].upper()}")
        print(f"目标URL: {action['url']}")
        if "data" in action:
            print(f"提交数据: {json.dumps(action['data'], indent=2)}")
    elif action_type == "cmd":
        print(f"\n⚠️ 高危命令确认 ({risk}风险)")
        print(f"即将执行: {action['command']}")
    
    if config["security"]["enable"] and action_type in ["file", "cmd"]:
        print(f"安全策略: {'允许' if is_action_allowed(action) else '禁止'}")
    
    return input("\n确认执行？(y/N): ").lower() == "y"

def is_action_allowed(action):
    """增强的安全检查"""
    if action["action"] == "file":
        path = action["path"]
        if not is_path_allowed(path):
            return False
            
        if action["operation"] in ["write", "delete"]:
            abs_path = os.path.abspath(os.path.expanduser(path))
            if os.path.isdir(abs_path):
                return False
                
    elif action["action"] == "cmd":
        cmd = action["command"]
        dangerous = ["rm -rf", "chmod 777", "wget", "curl | sh"]
        if any(c in cmd for c in dangerous):
            return False
            
    return True

def send_to_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": context_history + [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"API请求失败：{str(e)}"

def execute_action(action):
    """执行动作并返回结果"""
    if not validate_action(action):
        return {"status": "失败", "content": "无效的操作指令"}
        
    if not is_action_allowed(action):
        return {"status": "失败", "content": "操作被安全策略禁止"}
    
    try:
        action_type = action["action"]
        params = {k: v for k, v in action.items() if k != "action"}
        
        if action_type == "file":
            op = params["operation"]
            path = params["path"]
            abs_path = os.path.abspath(os.path.expanduser(path))
            
            if op == "read":
                with open(abs_path, "r") as f:
                    return {"action_type": "file", "status": "成功", "content": f.read()}
            
            elif op == "write":
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, "w") as f:
                    f.write(params.get("content", ""))
                return {"action_type": "file", "status": "成功", "content": f"文件已写入：{abs_path}"}
            
            elif op == "delete":
                os.remove(abs_path)
                return {"action_type": "file", "status": "成功", "content": f"文件已删除：{abs_path}"}
                
        elif action_type == "web":
            method = params["method"].lower()
            url = params["url"]
            
            if not validate_url(url):
                return {"action_type": "web", "status": "失败", "content": "无效URL"}
            
            try:
                if method == "get":
                    resp = requests.get(url, timeout=10)
                elif method == "post":
                    resp = requests.post(url, json=params.get("data", {}), timeout=10)
                return {"action_type": "web", "status": "成功", "content": resp.text}
            except:
                return {"action_type": "web", "status": "失败", "content": "请求失败"}
            
        elif action_type == "cmd":
            try:
                result = subprocess.run(
                    params["command"],
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                output = f"退出码：{result.returncode}\n输出：{result.stdout}\n错误：{result.stderr}"
                return {"action_type": "cmd", "status": "成功", "content": output}
            except:
                return {"action_type": "cmd", "status": "失败", "content": "执行超时"}
            
    except Exception as e:
        return {"action_type": action_type, "status": "失败", "content": str(e)}

def validate_url(url):
    """验证URL有效性"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def format_result(result):
    """格式化执行结果"""
    if result["status"] == "失败":
        return f"[{result['action_type']}操作] 状态：失败 ❌\n原因：{result['content']}"
    
    content = result["content"]
    if result["action_type"] == "web" and len(content) > 2000:
        content = content[:2000] + "\n[...内容过长已截断...]"
    
    return f"[{result['action_type']}操作] 状态：成功 ✅\n结果：{content}"



def main():
    print("智能助手已启动，输入'exit'退出")
    print(f"当前安全状态：{'🔒启用' if config['security']['enable'] else '⚠️停用'}")
    print("输入 'security config' 可修改安全设置")
    
    while True:
        user_input = input("\n用户：").strip()
        
        if user_input.lower() == "exit":
            break
            
        if user_input.lower() == "security config":
            update_security_setting()
            continue

        raw_response = send_to_openrouter(user_input)
        response_text, actions = process_response(raw_response)
        print(f"\n助手：{response_text}")
        
        execution_results = []
        for action in actions:
            if confirm_action(action):
                result = execute_action(action)
                print(f"\n{format_result(result)}")
                execution_results.append({
                    "action": action,
                    "result": result
                })
            else:
                execution_results.append({
                    "action": action,
                    "result": {
                        "action_type": action["action"],
                        "status": "取消",
                        "content": "用户取消执行"
                    }
                })

        context_history.append({"role": "user", "content": user_input})
        context_history.append({
            "role": "assistant",
            "content": f"{response_text}\n[系统提示]操作结果：{json.dumps(execution_results, ensure_ascii=False)}"
        })

        if execution_results:
            result_summary = "\n".join([
                f"{res['result']['action_type']}操作：{res['result']['status']}" 
                for res in execution_results
            ])
            follow_up_prompt = f"操作执行结果：\n{result_summary}\n请给出后续响应"
            
            follow_up_response = send_to_openrouter(follow_up_prompt)
            clean_follow_up, _ = process_response(follow_up_response)
            print(f"\n助手：{clean_follow_up}")
            
            context_history.append({"role": "user", "content": follow_up_prompt})
            context_history.append({"role": "assistant", "content": clean_follow_up})
        
        

if __name__ == "__main__":
    main()
