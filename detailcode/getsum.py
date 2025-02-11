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
) -> (str, dict):
    """
    使用给定模型对当前章节进行总结，输出新的剧情背景和角色特征。
    这次每章独立总结，不涉及前后文的关联。
    """
    prompt = f"""你是一位专业的文学编辑，擅长提炼小说的剧情背景和角色特征。下面提供了本章的具体内容。

【本章内容】：
{chapter_text}

请提炼出该章节的剧情背景和主要角色特征：
1. 剧情背景（包括重要的设定、环境、冲突、进展等）
2. 主要角色特征（包括人物性格、外貌、立场、能力等）。
3. 请不要融合多个角色到一个角色上，如果一个范类的名字如道士，如果他们都有其他名字或者特殊称谓，请使用，并作为单独一个角色如道士（虎力大仙、鹿力大仙、羊力大仙），你应该将他们作为三个角色虎力大仙、鹿力大仙、羊力大仙，并对每个角色写出下面格式，又比如沙僧（沙悟净）请不要进行别名写入括号这种操作，而是只保留沙僧这个名字
如果有多个角色，请分别列出每个角色的特点，格式如下：
- 角色名：xxx
  - 性格：xxx
  - 外貌：xxx
  - 立场：xxx
  - 能力：xxx
每个角色请严格按照这个格式
请多次检查你的角色格式，请务必保证，否则我无法处理
请用简洁的中文输出，确保内容准确，避免推测和虚构信息。
"""

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
    characters_part = {}

    lines = answer.splitlines()
    current_section = None
    current_character = None

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
            # 处理每个角色
            if line.strip().startswith("- 角色名"):
                # 新的角色开始
                current_character = line.strip().replace("- 角色名：", "").strip()
                characters_part[current_character] = {
                    "性格": "",
                    "外貌": "",
                    "立场": "",
                    "能力": ""
                }
            elif current_character:
                if "性格" in line:
                    characters_part[current_character]["性格"] += line.strip().replace("性格：", "").strip() + " "
                elif "外貌" in line:
                    characters_part[current_character]["外貌"] += line.strip().replace("外貌：", "").strip() + " "
                elif "立场" in line:
                    characters_part[current_character]["立场"] += line.strip().replace("立场：", "").strip() + " "
                elif "能力" in line:
                    characters_part[current_character]["能力"] += line.strip().replace("能力：", "").strip() + " "

    # 去除空格
    background_part = background_part.strip()

    # 格式化角色特征
    for character, traits in characters_part.items():
        for key in traits:
            traits[key] = traits[key].strip()

    return background_part, characters_part


def merge_text_from_chunks(chapter_data):
    """
    将当前章节所有 chunk 的文本拼成一个字符串。
    你可以做更复杂的处理，比如先用 Embedding+相似度筛选关键片段，再拼接。
    """
    texts = [item['text'] for item in chapter_data]
    return "\n".join(texts)


def main():
    # 指定单个章节文件路径
    chapter_file = "./novel/chapter_44.json"  # 修改为你的章节文件路径
    output_dir = "./character3"

    # 存放总结文件的输出路径
    os.makedirs(output_dir, exist_ok=True)

    output_filename = "chapter_44_summary.json"  # 修改为你输出的文件名
    output_filepath = os.path.join(output_dir, output_filename)

    # 若总结文件已存在，则跳过
    #if os.path.exists(output_filepath):
     #   print(f"总结文件 {output_filename} 已存在，跳过处理。")
      #  return

    # 加载该章的 chunks 数据
    chapter_data = load_embeddings(chapter_file)

    # 将所有 chunk 文本拼接成一个字符串
    chapter_text = merge_text_from_chunks(chapter_data)

    # 调用 summarize_chapter 生成剧情背景和角色特征
    new_background, new_characters = summarize_chapter(
        chapter_text=chapter_text,
        model_name="gpt-4o-mini"  # 或你使用的其它模型
    )

    # 输出数据
    output_data = {
        "chapter_index": 1,  # 根据章节编号修改
        "story_background": new_background,
        "character_features": new_characters
    }

    # 保存总结结果
    with open(output_filepath, "w", encoding="utf-8") as out_f:
        json.dump(output_data, out_f, ensure_ascii=False, indent=4)

    print(f"已完成章节总结，并保存到 {output_filepath}")


if __name__ == "__main__":
    main()
