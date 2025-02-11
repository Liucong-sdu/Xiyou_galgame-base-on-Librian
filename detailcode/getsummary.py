import os
import json
import openai

os.environ["http_proxy"] = "http://localhost:33210"
os.environ["https_proxy"] = "http://localhost:33210"
openai.api_key = ""  # 请替换为你自己的 API KEY


def load_embeddings(filename: str):
    """
    从JSON文件加载文本和向量。
    文件结构通常为: [
      { "text": "...", "embedding": [ ... ] },
      ...
    ]
    """
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def summarize_chapter(
    chapter_text: str,
    model_name: str = "gpt-4o-mini"
) -> (str, str):
    """
    使用给定模型对当前章节进行总结，输出新的剧情背景和角色特征。
    这次每章独立总结，不涉及前后文的关联。
    """
    prompt = f"""你是一位专业的文学编辑，擅长提炼小说的剧情背景和角色特征。下面提供了本章的具体内容。

【本章内容】：
{chapter_text}

请提炼出该章节的剧情背景和主要角色特征：
1. 剧情背景（包括重要的设定、环境、冲突、进展等）
2. 主要角色特征（包括人物性格、外貌、立场、能力等）

请用简洁的中文输出，确保内容准确，避免推测和虚构信息。"""

    # 调用 ChatCompletion
    response = openai.ChatCompletion.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.choices[0].message['content']

    # 简单的拆分过程，假设 AI 输出了“剧情背景”和“角色特征”
    background_part = ""
    characters_part = ""

    lines = answer.splitlines()
    current_section = None
    for line in lines:
        if "剧情背景" in line:
            current_section = "background"
            continue
        elif "角色特征" in line:
            current_section = "characters"
            continue

        if current_section == "background":
            background_part += line + "\n"
        elif current_section == "characters":
            characters_part += line + "\n"

    # 去除空格
    background_part = background_part.strip()
    characters_part = characters_part.strip()

    return background_part, characters_part


def merge_text_from_chunks(chapter_data):
    """
    将当前章节所有 chunk 的文本拼成一个字符串。
    你可以做更复杂的处理，比如先用 Embedding+相似度筛选关键片段，再拼接。
    """
    texts = [item['text'] for item in chapter_data]
    return "\n".join(texts)


def main():
    # 存放每章总结的目录
    output_dir = "./character2"
    os.makedirs(output_dir, exist_ok=True)

    # 设定你放置 embedding 后 JSON 文件的目录
    novel_dir = "./novel"

    # 获取所有章节文件的列表（假设文件命名规范为 chapter_1.json, chapter_2.json, ...）
    chapter_files = sorted(
        [f for f in os.listdir(novel_dir) if f.startswith("chapter_") and f.endswith(".json")],
        key=lambda x: int(x.replace("chapter_", "").replace(".json", ""))
    )

    for chapter_file in chapter_files:
        chapter_index = chapter_file.replace("chapter_", "").replace(".json", "")
        output_filename = f"chapter_{chapter_index}.json"
        output_filepath = os.path.join(output_dir, output_filename)

        # 若对应的总结文件已存在，则跳过当前章节
        if os.path.exists(output_filepath):
            print(f"章节 {chapter_index} 的总结文件已存在，跳过。")
            continue

        chapter_path = os.path.join(novel_dir, chapter_file)
        # 加载该章的 chunks 数据
        chapter_data = load_embeddings(chapter_path)

        # 将所有 chunk 文本拼接成一个字符串
        chapter_text = merge_text_from_chunks(chapter_data)

        # 调用 summarize_chapter 生成剧情背景和角色特征
        new_background, new_characters = summarize_chapter(
            chapter_text=chapter_text,
            model_name="gpt-4o-mini"  # 或你使用的其它模型
        )

        output_data = {
            "chapter_index": chapter_index,
            "story_background": new_background,
            "character_features": new_characters
        }

        with open(output_filepath, "w", encoding="utf-8") as out_f:
            json.dump(output_data, out_f, ensure_ascii=False, indent=4)

        print(f"已完成第 {chapter_index} 章的总结，并保存到 {output_filepath}")

    print("全部章节的剧情背景和角色特征都已处理完毕。")


if __name__ == "__main__":
    main()
