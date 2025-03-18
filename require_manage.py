with open('requirements.txt', 'r', encoding='utf_16_le') as f:
    requirements = f.readlines()
    requirements_plain = f.read()

with open('requirements_win.txt', 'w', encoding='utf_16_le') as f:
    f.writelines(requirements)

# 不写入包含pywin32的行
with open('requirements_other.txt', "w", encoding="utf_16_le") as f:
    for line in requirements:
        if "pywin32" not in line:
            f.write(line)