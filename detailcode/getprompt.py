import os
import json
import openai

# 请替换为你自己的 OpenAI API KEY
openai.api_key = ""


def load_json_file(filepath: str):
    """
    从指定路径加载 JSON 文件。
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def merge_text_from_chunks(chapter_data):
    """
    将当前章节所有 chunk 的文本拼成一个字符串。
    """
    texts = [item['text'] for item in chapter_data]
    return "\n".join(texts)


def extract_characters(character_features):
    """
    从角色特征中提取出可用的角色名称。
    确保只提取角色特征中存在的角色。
    """
    return list(character_features.keys())


def summarize_story(story_background: str) -> str:
    """
    使用 o1-mini 模型生成简述版本的剧情文本，要求保留关键细节和人物剧情。
    """
    prompt = f"""
    你是一个文学编辑，任务是将以下长篇故事概括为 300-500 字，保留关键细节、冲突和主要人物的剧情。请避免加入不必要的内容。

    故事内容：
    {story_background}

    请返回简述版本的剧情内容，长度控制在 300-500 字之间，保留核心冲突和人物剧情。
    """

    try:
        response = openai.ChatCompletion.create(
            model="o1-mini",
            messages=[
                {"role": "assistant", "content": "You are a skilled literary editor."},
                {"role": "user", "content": prompt}
            ]
        )
        summarized_story = response.choices[0].message['content'].strip()
        return summarized_story
    except Exception as e:
        print(f"调用 o1-mini 生成剧情简述时出错：{e}")
        return story_background  # 如果出错，返回原始文本


def generate_script_prompt(story_background: str, characters: list) -> str:
    """
    根据剧情背景和角色生成剧本的提示词。
    """
    characters_str = ", ".join(characters)
    print(characters_str)
    prompt = f"""
    你是一个剧本编剧，根据以下规则生成剧本：

    1. 旁白：直接写一段话，没有特殊符号开头。
    2. 对话：前面带名字，用方引号「」圈住言语，中间的空格可加可不加。
       例子：机房的門上鎖了，潘大爺被關在外面。  
       潘大爺「你們別玩了快來給我開門！」
       第一行是旁白，描述场景。第二行是潘大爺的对话，用方引号括起来。
    3. 多行对话：可以使用多行对话，空格缩进不是必须的。
       例子：潘大爺「歡迎來到莆田理工大學……
              欸，上面已經說過這句了嗎？
              不好意思。」
    4. 旁白转义：在旁白符合对话格式时，可以在前面加上冒号来防止被当成对话。
       例子：:靈符「夢想天生」
    5. 可用的人物：{characters_str}，人物名称只可以用{characters_str}，不允许使用可用人物之外的人物进行对话。
    请务必检查5以后再给出答案，此外你一定要注意在「」前只能出现这些人物的名字{characters_str}，而不能带有某某某说之类的话
    参考的剧本内容如下：{story_background}，剧情请不要超出参考的部分
    请再次注意，每一个「」，即“「”前，只能出现一个完整的出自{characters_str}的人名，而不能出现任何其余的东西，并且请不要带有“：”等字符，仅仅是名字
    请根据以上规则生成一段较完整的剧本，尽量出现所有人物，并不一定全部是两个人之间的对白，可以是单人的独白或者只有旁白，此外我希望剧本尽量丰富一点，不要太简短，并返回相应的内容。
    """
    return prompt


def generate_script(story_background: str, characters: list) -> str:
    """
    使用 GPT-4o-mini 生成剧本。
    """
    prompt = generate_script_prompt(story_background, characters)

    try:
        response = openai.ChatCompletion.create(
            model="o1-mini",
            messages=[
                {"role": "assistant", "content": "You are a scriptwriter."},
                {"role": "user", "content": prompt}
            ]
        )
        script = response.choices[0].message['content'].strip()
        return script
    except Exception as e:
        print(f"调用 GPT-4o-mini 生成剧本时出错：{e}")
        return ""


def save_script(script: str, filename: str):
    """
    将生成的剧本保存为文本文件，并在文件开头添加 ">BG background_image"。
    """
    # 在剧本的第一行添加 ">BG background_image"
    script_with_bg = ">BG background_image\n" + script

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(script_with_bg)


def main():
    # 设定总结 JSON 文件存放目录和输出的剧本文件目录
    novel_file = "./novel/chapter_44.json"  # 从 ./novel 加载章节数据
    character_file = "./character3/chapter_44_summary.json"  # 从 ./character3 加载角色数据
    output_dir = "./Librian_win64_2011/Librian面板/project/黑风岭/我的劇本"  # 输出的剧本文件目录
    os.makedirs(output_dir, exist_ok=True)

    # 获取章节数据并拼接文本
    chapter_data = load_json_file(novel_file)
    story_background = merge_text_from_chunks(chapter_data)  # 拼接所有chunk的文本

    # 生成故事简述
    summarized_story = summarize_story(story_background)

    # 获取角色特征并提取可用角色
    character_data = load_json_file(character_file)
    character_features = character_data.get("character_features", {})  # 从角色数据中提取
    characters = extract_characters(character_features)

    # 生成剧本
    script = generate_script(summarized_story, characters)

    # 保存剧本到文件
    output_filename = os.path.join(output_dir, "入口.liber")
    save_script(script, output_filename)

    print(f"剧本已保存到：{output_filename}")


if __name__ == "__main__":
    main()
