import os
import json
import openai
import requests
import time

# 代理设置（如不需要代理可移除下面两行）
os.environ["http_proxy"] = "http://localhost:33210"
os.environ["https_proxy"] = "http://localhost:33210"

# 请替换为你自己的 OpenAI API KEY
openai.api_key = ""

def load_summary(filename: str):
    """
    从 JSON 文件加载章节总结数据。
    """
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def download_image(url: str, filename: str):
    """
    根据图片 URL 下载图片并保存到指定文件
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
        else:
            print(f"下载图片失败，状态码：{response.status_code}")
    except Exception as e:
        print(f"下载图片时发生错误：{e}")

def generate_refined_prompt(story_background: str, model_name: str = "gpt-4o-mini") -> str:
    """
    利用 GPT-4o-mini 模型根据剧情背景生成一个详细且写实风格的图像生成提示词。
    """
    prompt_template = f"""你是一位资深的艺术指导，你的任务是根据给定的小说剧情背景为图像生成提供一个详细的提示词。请综合以下剧情背景内容，生成一个用于调用图像生成模型的详细提示词，要求：

1. 描述清晰、具体，便于图像生成模型准确理解场景、情感和细节；
2. 提示词中应包含场景，人物，构图等信息，风格为写实风格；
3. 保留原有剧情中的关键要素，不要添加与剧情无关的信息。
4. 请以英文输出,但是不要超过120词，但你要确保人物形象的正确

剧情背景：
{story_background}

请输出生成的提示词。"""

    try:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[{"role": "system", "content": "You are a creative art prompt generator."},
                      {"role": "user", "content": prompt_template}]
        )
        refined_prompt = response.choices[0].message['content'].strip()
        return refined_prompt
    except Exception as e:
        print(f"调用 GPT-4o-mini 生成提示词时出错：{e}")
        return (
            f"请根据以下剧情背景，创作一幅写实风格的艺术插画。画面要求真实自然，细节丰富，仿佛是一张高分辨率的摄影照片。"
            f"请在画面中真实呈现出故事中的关键场景、环境和情感，光影效果自然，色调符合实际场景。\n\n"
            f"剧情背景：\n{story_background}\n\n"
            f"请务必注重场景的真实感和细节表现。"
        )

def generate_refined_character_prompt(character_name: str, features: dict, model_name: str = "gpt-4o-mini") -> str:
    """
    利用 GPT-4o-mini 对角色提示词进行精炼，使其更符合生成的需求
    """
    character_description = f"性格：{features['性格']} 外貌：{features['外貌']} 立场：{features['立场']} 能力：{features['能力']}"
    prompt_template = f"""你是一个艺术指导，任务是根据以下角色描述生成一个详细的提示词来帮助图像生成模型准确理解角色形象。要求：

1. 清晰、详细地描述角色的外貌和个性；
2. 描述风格为写实风格，尽量细致，展现人物的个性和特点；
3. 请尽量具体，例如人物的发型、服装、面部特征、姿势等。
4. 请以英文输出,但是不要超过100词，但你要确保人物形象的正确
5. 你还需要保证输出的图片是一个单独的人物而不是多个
角色名：{character_name}
角色描述：{character_description}

请输出生成的提示词。"""

    try:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[{"role": "system", "content": "You are a creative art prompt generator."},
                      {"role": "user", "content": prompt_template}]
        )
        refined_prompt = response.choices[0].message['content'].strip()
        return refined_prompt
    except Exception as e:
        print(f"调用 GPT-4o-mini 生成角色提示词时出错：{e}")
        return f"Please create a portrait of {character_name} based on their traits: {character_description}."

def generate_image_with_retry(prompt: str, model_name: str = "black-forest-labs/FLUX.1-pro", retries: int = 3, delay: int = 5):
    """
    调用图像生成模型生成背景图像或人物图像，并在失败时进行重试。
    """
    url = "https://api.siliconflow.cn/v1/images/generations"
    payload = {
        "height": 768,
        "width": 1376,
        "model": model_name,
        "safety_tolerance": 0,
        "prompt": prompt,
        "seed": 4999999999
    }
    headers = {
        "Authorization": "",  # 替换为你的实际 API 密钥
        "Content-Type": "application/json"
    }

    # 尝试生成图片，最多重试 retries 次
    for attempt in range(retries):
        try:
            # 调用 Silicon Flow API 生成图片
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # 如果响应状态码不是 200，抛出异常

            # 获取返回的图片 URLs
            response_data = response.json()
            image_url = response_data["images"][0]["url"]
            return image_url
        except Exception as e:
            print(f"第 {attempt + 1} 次调用 Image API 出现错误：{e}")
            if attempt < retries - 1:
                print(f"等待 {delay} 秒后重新尝试...")
                time.sleep(delay)  # 等待一段时间再重试
            else:
                print("重试次数用尽，生成图片失败。")
                return None

def generate_images_for_summary(summary_file: str, chapter_index: int, images_dir: str):
    """
    根据章节总结中的剧情背景生成图片：
    1. 从 summary_file 加载 JSON，总结数据中提取剧情背景。
    2. 使用剧情背景调用 GPT-4o-mini 生成精炼的图像生成提示词。
    3. 调用图像生成服务生成背景图片并保存。
    4. 对每个角色生成图片并保存。
    """
    # 加载章节总结
    summary_data = load_summary(summary_file)
    story_background = summary_data.get("story_background", "")
    character_features = summary_data.get("character_features", {})

    if not story_background:
        print(f"章节 {chapter_index} 的总结中未找到 'story_background'，跳过该章节。")
        return

    # 构造该章节图片保存的文件夹路径
    chapter_images_dir = os.path.join(images_dir, f"chapter_{chapter_index}")
    os.makedirs(chapter_images_dir, exist_ok=True)

    # 使用剧情背景生成背景图像
    refined_prompt = generate_refined_prompt(story_background)
    print(f"【第 {chapter_index} 章】背景生成的提示词：\n{refined_prompt}\n")

    background_image_url = generate_image_with_retry(refined_prompt)
    if background_image_url:
        background_image_filename = os.path.join(
            "./Librian_win64_2011/Librian面板/project/黑风岭/我的圖片", "background_image.png"
        )
        download_image(background_image_url, background_image_filename)
        print(f"已下载背景图片到：{background_image_filename}")

    # 对每个角色生成图片
    for character_name, features in character_features.items():
        character_prompt = generate_refined_character_prompt(character_name, features)
        print(f"【第 {chapter_index} 章】角色 {character_name} 生成的提示词：\n{character_prompt}\n")

        character_image_url = generate_image_with_retry(character_prompt)
        if character_image_url:
            character_image_filename = os.path.join(
                "./Librian_win64_2011/Librian面板/project/黑风岭/我的立繪", f"{character_name}.png"
            )
            download_image(character_image_url, character_image_filename)
            print(f"已下载角色 {character_name} 图片到：{character_image_filename}")

def main():
    # 设定总结 JSON 文件存放目录和图片保存目录
    summary_file = "./character3/chapter_44_summary.json"  # 指定单一文件
    images_dir = "./images_2"  # 图片将保存在此目录中
    os.makedirs(images_dir, exist_ok=True)

    # 获取章节索引
    chapter_index = 1  # 根据实际情况修改

    print(f"正在处理第 {chapter_index} 章的图片生成...")
    generate_images_for_summary(summary_file, chapter_index, images_dir)

    print("图片生成完毕。")

if __name__ == "__main__":
    main()
