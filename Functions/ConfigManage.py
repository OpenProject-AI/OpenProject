import json
import os
from typing import Union
import dotenv
from typing import Union, List, Dict, Any
import asyncio

# 获取用户目录
user_dir = os.path.expanduser('~')

cfg_default_path = user_dir + '\openproject_config.env'

def init_config(config_file=cfg_default_path, template: dict = None) -> None:
    ''' 
    创建一个新的配置文件。
    '''
    if template is None:
        template = {
            'BASE_URL': "https://Domain/v1",
            'API_KEY': "your_api_key",
            'MODEL_NAME': "your_model_name",
            'API_MODE': "openai"
        }
    # 遍历template字典，将其写入./cfg.env文件中
    try:
        for key, value in template.items():
            # 写入文件
            dotenv.set_key(config_file, key, str(value))
            print(f"[CFG LOADER] WRITE TO {config_file}: {key} = {value}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def convert_value(value: Union[str, None]) -> Union[bool, str, int, float, List, Dict, None]:
    if value is None:
        return None
    
    # 尝试转换为 bool
    if value.lower() in ['true', 'false']:
        return value.lower() == 'true'
    
    # 尝试转换为 int
    try:
        return int(value)
    except ValueError:
        pass
    
    # 尝试转换为 float
    try:
        return float(value)
    except ValueError:
        pass
    
    # 尝试转换为 list (假设列表是以逗号分隔的字符串)
    if ',' in value:
        return value.split(',')
    
    # 尝试转换为 dict (假设字典是以 JSON 格式的字符串)
    import json
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        pass
    
    # 如果以上转换都失败，则返回原始字符串
    return value

def get_config(name: str, default: Union[str, int, float, bool, List, Dict, None] = None, path: str = cfg_default_path) -> Any:
    dotenv.load_dotenv(path)
    cfg_vl = os.getenv(name, default)
    
    # 转换值
    converted_value = convert_value(cfg_vl)
    
    print(f'[CFG LOADER] READ FROM {path}: {name} = {"*" * len(converted_value)} | Type: {type(converted_value)}')
    return converted_value

def wnGet(name: str, default: Union[str, int, float, bool, List, Dict, None] = None, path: str = cfg_default_path) -> Any:
    """
    万能获取，自动检测配置文件是否存在，不存在则创建。创建之后再次返回值。
    """
    # Check File
    if not os.path.exists(path):
        # init_config(path)
        init_wizard()
    # Get Value
    return get_config(name, default, path)

# 初始化向导
def init_wizard() -> None:
    print("鉴于您还没有配置过 OpenProject 相关信息，下面将为您进行配置向导。")
    print("请按照提示输入相关信息。")
    api_mode = input("请选择 API 接口类型（openai/ollama/custom）：")
    if api_mode.lower() == "openai":
        # OpenAI API
        print("您选择了 OpenAI API 接口。")
        base_url = input("请输入 OpenAI 服务器Base-URL（例如：https://Domain/v1）：")
        api_key = input("请输入 OpenAI API Key：")
        model_name = input("请输入 OpenAI 模型名称：")
        template = {
            'BASE_URL': base_url,
            'API_KEY': api_key,
            'MODEL_NAME': model_name,
            'API_MODE': "openai"
        }
        init_config(template=template)
        print("配置成功！继续使用！")
    elif api_mode.lower() == "ollama":
        # OLlama API
        print("您选择了 OLlama API 接口。[警告：Ollama API 接口目前处于测试阶段。且因未知原因，Prompt有概率失效导致功能异常。]")
        base_url = input("请输入 OLlama 服务器Base-URL（例如：https://Domain/api）：")
        model_name = input("请输入 OLlama 模型名称：")
        template = {
            'BASE_URL': base_url,
            'MODEL_NAME': model_name,
            'API_MODE': "ollama"
        }
        init_config(template=template)
        print("配置成功！继续使用！")
    elif api_mode.lower() == "custom":
        # Custom API
        print("您选择了自定义 API 接口。警告：自定义 API 接口需要您自行编写代码，请确保您已经完成相关配置。且默认情况下，OpenProject将会使用 POST 方法发送请求。功能有概率失效")
        base_url = input("请输入自定义服务器Base-URL（例如：https://Domain）：")
        endpoint = input("请输入自定义 API 接口路径（例如：/api/v1/chat）：")
        print("请注意：自定义 API 接口需要您自行编写代码，请确保您已经完成相关配置。且默认情况下，OpenProject将会使用 POST 方法发送请求。")
        template = {
            'BASE_URL': base_url,
            'ENDPOINT': endpoint,
            'API_MODE': "custom"
        }
        init_config(template=template)
        print("配置成功！继续使用！")
    else:
        print("输入错误，请重新输入。")
        init_wizard()
        