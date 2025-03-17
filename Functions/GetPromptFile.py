def GetPromptFile():
    with open("files/prompt.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    return prompt