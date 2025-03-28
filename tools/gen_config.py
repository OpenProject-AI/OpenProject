import os
import json
import binascii
from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT

def password_to_hex_key(password: str) -> str:
    """将密码转换为16进制密钥"""
    # 将密码转换为字节
    password_bytes = password.encode('utf-8')
    # 转换为16进制字符串
    hex_key = binascii.hexlify(password_bytes).decode('utf-8')
    # 如果长度不足32位（16字节），进行填充
    if len(hex_key) < 32:
        hex_key = hex_key.ljust(32, '0')
    # 如果长度超过32位，截取前32位
    return hex_key[:32]

def encrypt_config(config_content: str, key: str) -> str:
    """使用SM4加密配置内容"""
    try:
        # 创建SM4加密器
        crypt_sm4 = CryptSM4()
        # 设置密钥
        key_bytes = bytes.fromhex(key)
        crypt_sm4.set_key(key_bytes, SM4_ENCRYPT)
        # 加密内容
        encrypt_bytes = crypt_sm4.crypt_ecb(config_content.encode('utf-8'))
        # 转换为16进制字符串
        return binascii.hexlify(encrypt_bytes).decode('utf-8')
    except Exception as e:
        print(f"加密失败: {str(e)}")
        return ""

def decrypt_config(encrypted_content: str, key: str) -> str:
    """使用SM4解密配置内容"""
    try:
        # 创建SM4解密器
        crypt_sm4 = CryptSM4()
        # 设置密钥
        key_bytes = bytes.fromhex(key)
        crypt_sm4.set_key(key_bytes, SM4_DECRYPT)
        # 将16进制字符串转换为字节
        encrypted_bytes = binascii.unhexlify(encrypted_content)
        # 解密内容
        decrypted_bytes = crypt_sm4.crypt_ecb(encrypted_bytes)
        # 转换为字符串
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        print(f"解密失败: {str(e)}")
        return ""

def generate_encrypted_config(password: str, config_content: str, output_file: str = 'encrypted_config.txt') -> bool:
    """生成加密的配置文件"""
    try:
        # 将密码转换为密钥
        key = password_to_hex_key(password)
        # 加密配置内容
        encrypted_content = encrypt_config(config_content, key)
        if not encrypted_content:
            return False
            
        # 写入加密后的内容到文件
        with open(output_file, 'w') as f:
            f.write(encrypted_content)
        print(f"加密配置已保存到: {output_file}")
        return True
    except Exception as e:
        print(f"生成加密配置失败: {str(e)}")
        return False

def main():
    # 选择操作模式
    mode = input("请选择操作模式 (1: 加密配置, 2: 解密配置): ").strip()
    
    if mode == "1":
        # 加密模式
        base_url = input("请输入BASE_URL: ")
        api_key = input("请输入API_KEY: ")
        model_name = input("请输入MODEL_NAME: ")
        
        # 组织配置内容
        config_dict = {
            "BASE_URL": base_url,
            "API_KEY": api_key,
            "MODEL_NAME": model_name
        }
        config_content = json.dumps(config_dict)
        
        # 获取密码和输出文件名
        password = input("请输入密码: ")
        output_file = input("请输入输出文件名(默认为encrypted_config.txt): ").strip() or 'encrypted_config.txt'
        
        if generate_encrypted_config(password, config_content, output_file):
            print("配置加密成功！")
        else:
            print("配置加密失败！")
    
    elif mode == "2":
        # 解密模式
        input_file = input("请输入加密配置文件名: ").strip()
        password = input("请输入密码: ")
        
        try:
            # 读取加密文件
            with open(input_file, 'r') as f:
                encrypted_content = f.read().strip()
            
            # 将密码转换为密钥
            key = password_to_hex_key(password)
            # 解密配置内容
            decrypted_content = decrypt_config(encrypted_content, key)
            
            if decrypted_content:
                # 解析并显示解密后的配置
                config_dict = json.loads(decrypted_content)
                print("\n解密成功！配置内容如下：")
                for key, value in config_dict.items():
                    print(f"{key}: {value}")
            else:
                print("解密失败！")
        except FileNotFoundError:
            print(f"找不到文件: {input_file}")
        except json.JSONDecodeError:
            print("解密后的内容不是有效的JSON格式")
        except Exception as e:
            print(f"发生错误: {str(e)}")
    
    else:
        print("无效的操作模式！请选择 1 或 2")

if __name__ == '__main__':
    main()