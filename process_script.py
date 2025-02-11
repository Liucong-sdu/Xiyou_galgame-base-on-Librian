import json

# 读取原始JSON文件
with open('2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 提取content内容
content = data['choices'][0]['message']['content']

# 处理换行符
formatted_content = content.replace('\\n\\n', '\n').replace('\\n', '\n')

# 写入目标文件
output_path = r'Librian面板\project\车迟国\我的劇本\入口.liber'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(">BG 1")
    f.write('\n')
    f.write(formatted_content)

print(f"处理完成！文件已保存至：{output_path}")
