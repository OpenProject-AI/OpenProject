def GetPromptFile(base_dir):
    with open(f"{base_dir}/files/prompt.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    
    # 检查是否存在custom_prompt.txt文件
    custom_prompt_path = f"{base_dir}/files/custom_prompt.txt"
    try:
        with open(custom_prompt_path, "r", encoding="utf-8") as f:
            custom_prompt = f.read()
            prompt = prompt + "\n【拓展prompt】\n" + custom_prompt
    except FileNotFoundError:
        pass
    
    return prompt