import re

def get_action_content(text):
    """
    获取`~+~action`和`~-~`之间的文本内容（即Action动作内容）
    """
    pattern = r'~\+~action(.*?)~-~'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        # print("Error: No action content found in the input text.")
        # print("提示：无ACTION动作内容，建议使用wnGetActionContent函数获取。")
        return None

def action_cback_render(action_type: str, action: str, is_ok: str = "yes or no", content: str = "", extra: dict = {"standard": "OpenProject/stdAction-Local"}):
    """
    根据Action类型、动作内容、是否成功、内容，渲染Action YAML回调数据。遵循OpenProject/stdAction-Local标准。
    """
    # 处理extra参数
    extra_text = ""
    extra_keys = list(extra.keys())
    extra_values = list(extra.values())
    for i in range(len(extra_keys)):
        extra_text += f"      {extra_keys[i]}: {extra_values[i]}\n"
        
    template = f"""
~+~action callback
action_type: {action_type}
action: {action}
is_ok: {is_ok}
content: |
   {content}
extra: |
{extra_text}
~-~
    """
    return template

def parse_args(args: list):
    """
    解析参数列表，返回参数字典。
    支持 --key="value" 格式，且 value 可以包含空格和转义字符。
    """
    args_dict = {}
    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith('--'):
            # 提取 key
            key = arg[2:]  # 去掉前面的 --
            if '=' in key:
                key, partial_value = key.split('=', 1)
            else:
                partial_value = ''
            
            # 如果 partial_value 以双引号开头，尝试合并后续部分
            if partial_value.startswith('"'):
                value = partial_value[1:]  # 去掉开头的双引号
                # 合并后续部分，直到找到闭合的双引号
                while i + 1 < len(args) and not value.endswith('"'):
                    i += 1
                    value += ' ' + args[i]
                if value.endswith('"'):
                    value = value[:-1]  # 去掉结尾的双引号
                args_dict[key] = value
            else:
                args_dict[key] = partial_value
        i += 1
    return args_dict

def action_runner(content: str):
    """
    解析Action动作内容，返回字典形式的Action数据
    """
    action = {}
    check_security = True
    try: 
        parts = content.split(' ')
        action = {
            'type': parts[0],  # 类型，例如 "File"
            'action': parts[1],  # 动作，例如 "read"
            'args': parse_args(parts[2:])  # 解析参数，返回字典
        }
        print(f"Debug: Parsed action = {action}")  # 打印调试信息
    except Exception as e:
        print(f'Error: {e}')
        return None
    
    if check_security:
        print("\033[1;31m操作请求\033[0m")
        print(f"\033[1;32m操作类别：{action['type']}\033[0m")
        print(f"\033[1;32m操作动作：{action['action']}\033[0m")
        print(f"\033[1;32m操作参数：{action['args']}\033[0m")
        print("\033[1;31m请确认以上信息是否正确，输入 yes 继续，输入 no 取消操作。\033[0m")
        confirm = input("\033[1;31m请输入 yes 或 no：\033[0m")
        if confirm.lower() != 'yes':
            return action_cback_render(
                action_type=action['type'],
                action=action['action'],
                is_ok="no",
                content="Operation cancelled by user",
                extra={}
            )
    
    if action["type"] == "File":
        # 如果为读文件动作
        if action["action"] == "read":
            # 解析参数
            path = action['args'].get('path')
            if not path:
                return action_cback_render(
                    action_type="File",
                    action="read",
                    is_ok="no",
                    content="Missing path parameter",
                    extra={}
                )
            
            letter_limit = 4000
            
            # 打开文件，读取内容
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 使用字符串切片来截取内容的前letter_limit个字
                content = content[:letter_limit]
                
                return action_cback_render(
                    action_type="File",
                    action="read",
                    is_ok="yes",
                    content=content,
                    extra={"path": path, "letter_limit": letter_limit}
                )
            except FileNotFoundError:
                return action_cback_render(
                    action_type="File",
                    action="read",
                    is_ok="no",
                    content="File not found",
                    extra={"path": path, "letter_limit": letter_limit}
                )
            except Exception as e:
                return action_cback_render(
                    action_type="File",
                    action="read",
                    is_ok="no",
                    content=str(e),
                    extra={"path": path, "letter_limit": letter_limit}
                )
        elif action["action"] == "write":
            # 解析参数
            path = action['args'].get('path')
            content = action['args'].get('content')
            if not path or not content:
                return action_cback_render(
                    action_type="File",
                    action="write",
                    is_ok="no",
                    content="Missing path or content parameter",
                    extra={}
                )
            
            # 打开文件，写入内容
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return action_cback_render(
                    action_type="File",
                    action="write",
                    is_ok="yes",
                    content=content,
                    extra={"path": path}
                )
            except Exception as e:
                return action_cback_render(
                    action_type="File",
                    action="write",
                    is_ok="no",
                    content=str(e),
                    extra={"path": path}
                )
        elif action["action"] == "delete":
            # 解析参数
            path = action['args'].get('path')
            if not path:
                return action_cback_render(
                    action_type="File",
                    action="delete",
                    is_ok="no",
                    content="Missing path parameter",
                    extra={}
                )
            
            # 删除文件
            try:
                import os
                os.remove(path)
                
                return action_cback_render(
                    action_type="File",
                    action="delete",
                    is_ok="yes",
                    content="",
                    extra={"path": path}
                )
            except FileNotFoundError:
                return action_cback_render(
                    action_type="File",
                    action="delete",
                    is_ok="no",
                    content="File not found",
                    extra={"path": path}
                )
            except Exception as e:
                return action_cback_render(
                    action_type="File",
                    action="delete",
                    is_ok="no",
                    content=str(e),
                    extra={"path": path}
                )
        else:
            print(f"Error: Unknown action {action['action']} for type {action['type']}")
            return None
    elif action["type"] == "Directory":
        if action["action"] == "create":
            # 解析参数
            path = action['args'].get('path')
            if not path:
                return action_cback_render(
                    action_type="Directory",
                    action="create",
                    is_ok="no",
                    content="Missing path parameter",
                    extra={}
                )
            
            # 创建目录
            try:
                import os
                os.makedirs(path)
                
                return action_cback_render(
                    action_type="Directory",
                    action="create",
                    is_ok="yes",
                    content="",
                    extra={"path": path}
                )
            except FileExistsError:
                return action_cback_render(
                    action_type="Directory",
                    action="create",
                    is_ok="no",
                    content="Directory already exists",
                    extra={"path": path}
                )
            except Exception as e:
                return action_cback_render(
                    action_type="Directory",
                    action="create",
                    is_ok="no",
                    content=str(e),
                    extra={"path": path}
                )
        elif action["action"] == "delete":
            # 解析参数
            path = action['args'].get('path')
            if not path:
                return action_cback_render(
                    action_type="Directory",
                    action="delete",
                    is_ok="no",
                    content="Missing path parameter",
                    extra={}
                )
            
            # 删除目录
            try:
                import os
                os.rmdir(path)
                
                return action_cback_render(
                    action_type="Directory",
                    action="delete",
                    is_ok="yes",
                    content="",
                    extra={"path": path}
                )
            except OSError:
                return action_cback_render(
                    action_type="Directory",
                    action="delete",
                    is_ok="no",
                    content="Directory not empty or does not exist",
                    extra={"path": path}
                )
            except Exception as e:
                return action_cback_render(
                    action_type="Directory",
                    action="delete",
                    is_ok="no",
                    content=str(e),
                    extra={"path": path}
                )
        elif action["action"] == "read":
            # 解析参数
            path = action['args'].get('path')
            if not path:
                return action_cback_render(
                    action_type="Directory",
                    action="read",
                    is_ok="no",
                    content="Missing path parameter",
                    extra={}
                )
            
            # 列出目录
            try:
                import os
                files = os.listdir(path)
                
                return action_cback_render(
                    action_type="Directory",
                    action="read",
                    is_ok="yes",
                    content=str(files),
                    extra={"path": path}
                )
            except FileNotFoundError:
                return action_cback_render(
                    action_type="Directory",
                    action="read",
                    is_ok="no",
                    content="Directory not found",
                    extra={"path": path}
                )
            except Exception as e:
                return action_cback_render(
                    action_type="Directory",
                    action="read",
                    is_ok="no",
                    content=str(e),
                    extra={"path": path}
                )
        else:
            print(f"Error: Unknown action {action['action']} for type {action['type']}")
            return None
    elif action["type"] == "Command":
        if action["action"] == "execute":
            # 解析参数
            command = action['args'].get('command')
            if not command:
                return action_cback_render(
                    action_type="Command",
                    action="execute",
                    is_ok="no",
                    content="Missing command parameter",
                    extra={}
                )
            
            # 执行命令
            try:
                import subprocess
                result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                
                return action_cback_render(
                    action_type="Command",
                    action="execute",
                    is_ok="yes",
                    content=str(result.decode('utf-8')),
                    extra={"command": command}
                )
            except subprocess.CalledProcessError as e:
                return action_cback_render(
                    action_type="Command",
                    action="execute",
                    is_ok="no",
                    content=str(e.output.decode('utf-8')),
                    extra={"command": command}
                )
            except Exception as e:
                return action_cback_render(
                    action_type="Command",
                    action="execute",
                    is_ok="no",
                    content=str(e),
                    extra={"command": command}
                )
        else:
            print(f"Error: Unknown action {action['action']} for type {action['type']}")
            return None
    elif action["type"] == "Network":
        if action["action"] == "get":
            # 解析参数
            url = action['args'].get('url')
            if not url:
                return action_cback_render(
                    action_type="Network",
                    action="get",
                    is_ok="no",
                    content="Missing url parameter",
                    extra={}
                )
            
            # 获取网页内容
            try:
                import requests
                response = requests.get(url)
                content = response.content.decode('utf-8')
                
                return action_cback_render(
                    action_type="Network",
                    action="get",
                    is_ok="yes",
                    content=content,
                    extra={"url": url}
                )
            except requests.exceptions.RequestException as e:
                return action_cback_render(
                    action_type="Network",
                    action="get",
                    is_ok="no",
                    content=str(e),
                    extra={"url": url}
                )
        elif action["action"] == "post":
            # 解析参数
            url = action['args'].get('url')
            data = action['args'].get('data')
            if not url or not data:
                return action_cback_render(
                    action_type="Network",
                    action="post",
                    is_ok="no",
                    content="Missing url or data parameter",
                    extra={}
                )
            
            # 发送POST请求
            try:
                import requests
                response = requests.post(url, data=data)
                content = response.content.decode('utf-8')
                
                return action_cback_render(
                    action_type="Network",
                    action="post",
                    is_ok="yes",
                    content=content,
                    extra={"url": url, "data": data}
                )
            except requests.exceptions.RequestException as e:
                return action_cback_render(
                    action_type="Network",
                    action="post",
                    is_ok="no",
                    content=str(e),
                    extra={"url": url, "data": data}
                )
        elif action["action"] == "put":
            # 解析参数
            url = action['args'].get('url')
            data = action['args'].get('data')
            if not url or not data:
                return action_cback_render(
                    action_type="Network",
                    action="put",
                    is_ok="no",
                    content="Missing url or data parameter",
                    extra={}
                )
            
            # 发送PUT请求
            try:
                import requests
                response = requests.put(url, data=data)
                content = response.content.decode('utf-8')
                
                return action_cback_render(
                    action_type="Network",
                    action="put",
                    is_ok="yes",
                    content=content,
                    extra={"url": url, "data": data}
                )
            except requests.exceptions.RequestException as e:
                return action_cback_render(
                    action_type="Network",
                    action="put",
                    is_ok="no",
                    content=str(e),
                    extra={"url": url, "data": data}
                )
        elif action["action"] == "delete":
            # 解析参数
            url = action['args'].get('url')
            if not url:
                return action_cback_render(
                    action_type="Network",
                    action="delete",
                    is_ok="no",
                    content="Missing url parameter",
                    extra={}
                )
            
            # 发送DELETE请求
            try:
                import requests
                response = requests.delete(url)
                content = response.content.decode('utf-8')
                
                return action_cback_render(
                    action_type="Network",
                    action="delete",
                    is_ok="yes",
                    content=content,
                    extra={"url": url}
                )
            except requests.exceptions.RequestException as e:
                return action_cback_render(
                    action_type="Network",
                    action="delete",
                    is_ok="no",
                    content=str(e),
                    extra={"url": url}
                )
        elif action["action"] == "head":
            # 解析参数
            url = action['args'].get('url')
            if not url:
                return action_cback_render(
                    action_type="Network",
                    action="head",
                    is_ok="no",
                    content="Missing url parameter",
                    extra={}
                )
            
            # 发送HEAD请求
            try:
                import requests
                response = requests.head(url)
                content = response.content.decode('utf-8')
                
                return action_cback_render(
                    action_type="Network",
                    action="head",
                    is_ok="yes",
                    content=content,
                    extra={"url": url}
                )
            except requests.exceptions.RequestException as e:
                return action_cback_render(
                    action_type="Network",
                    action="head",
                    is_ok="no",
                    content=str(e),
                    extra={"url": url}
                )
        elif action["action"] == "options":
            # 解析参数
            url = action['args'].get('url')
            if not url:
                return action_cback_render(
                    action_type="Network",
                    action="options",
                    is_ok="no",
                    content="Missing url parameter",
                    extra={}
                )
            
            # 发送OPTIONS请求
            try:
                import requests
                response = requests.options(url)
                content = response.content.decode('utf-8')
                
                return action_cback_render(
                    action_type="Network",
                    action="options",
                    is_ok="yes",
                    content=content,
                    extra={"url": url}
                )
            except requests.exceptions.RequestException as e:
                return action_cback_render(
                    action_type="Network",
                    action="options",
                    is_ok="no",
                    content=str(e),
                    extra={"url": url}
                )
        else:
            print(f"Error: Unknown action {action['action']} for type {action['type']}")
    else:
        print(f"Error: Unknown type {action['type']}")
    return None

def wnGetActionContent(text):
    """
    万能获取Action内容，没有的话返回None，不报错
    """
    pattern = r'~\+~action(.*?)~-~'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        # print("Error: No action content found in the input text.")
        return None
    

if __name__ == '__main__':
    content = r"""
    你好
    再见
    """
    content = wnGetActionContent(content)   # 获取Action内容
    print(content)
    print(action_runner(content))