def GetPromptFile(base_dir):
    with open(f"{base_dir}/files/prompt.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    return prompt