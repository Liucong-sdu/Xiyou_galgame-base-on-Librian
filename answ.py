import requests
def api_use(text):

 url = "https://api.siliconflow.cn/v1/chat/completions"

 payload = {
    "model": "Pro/deepseek-ai/DeepSeek-V3",
    "messages": [
        {
            "role": "user",
            "content": f"""
1. 旁白和对话
规则：
旁白：直接写一段话，没有特殊符号开头。
对话：前面带名字，用方引号「」圈住言语，中间的空格可加可不加。
例子：
机房的門上鎖了，潘大爺被關在外面。
潘大爺 「你們別玩了快來給我開門！」
第一行是旁白，描述场景。
第二行是潘大爺的对话，用方引号「」括起来。
2. 多行对话
规则：
可以使用多行对话，空格缩进不是必须的。
例子：
潘大爺 「歡迎來到莆田理工大學……
欸，上面已經說過這句了嗎？
不好意思。」
潘大爺的对话分为三行，游戏中也表现为三行对话。
3. 旁白转义
规则：
在旁白符合对话格式时，可以在前面加上冒号来防止被当成对话。
例子：
:靈符「夢想天生」
这行旁白不会被当成对话，行首的冒号不会显示在画面上。

请严格按照以上规则生成剧本，参考的剧本内容如下：{text}，
可用的人物：
孙悟空、猪八戒、沙僧、唐僧、鹿力大仙、虎力大仙、羊力大仙、车迟国国王，
人物名称只可以用以上给出的，不允许使用可用人物之外的人物进行对话，给出相应的输出"""
        }
    ],
    "stream": False,
    "max_tokens": 4096,
    "stop": ["null"],
    "temperature": 0.5,
    "top_p": 0.7,
    "top_k": 50,
    "frequency_penalty": 0.0,
    "n": 1,
    "response_format": {"type": "text"},
    "tools": [
        {
            "type": "function",
            "function": {
                "description": "<string>",
                "name": "<string>",
                "parameters": {},
                "strict": False
            }
        }
    ]
 }
 headers = {
    "Authorization": "Bearer <api_key>",#此处是apikey
    "Content-Type": "application/json"
}

 response = requests.request("POST", url, json=payload, headers=headers)#response.text
 return response.text
 
