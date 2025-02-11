from answ import api_use

try:
    # 读取输入文件
    with open('1.txet', 'r', encoding='utf-8') as f:
        input_text = f.read()
    
    # 调用API处理文本
    result = api_use(input_text)
    
    # 写入输出文件
    with open('2.json', 'w', encoding='utf-8') as f:
        f.write(result)
        
    print("文件处理完成，已生成2.json")
    
except FileNotFoundError:
    print("错误：找不到1.txet文件")
except Exception as e:
    print(f"处理过程中发生错误：{str(e)}")
