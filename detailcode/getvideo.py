import os
import json
import openai
import requests
import time

# 请替换为你自己的 OpenAI API KEY
openai.api_key = ""


# 加载并拼接章节内容
def load_json_file(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def merge_text_from_chunks(chapter_data):
    texts = [item['text'] for item in chapter_data]
    return "\n".join(texts)


# 生成文本总结
def summarize_text(story_background: str) -> str:
    prompt = f"""
    You are a skilled literary editor. Summarize the following long story into a short version (300-500 words) while keeping the main characters and key conflicts intact. Avoid adding unnecessary information.

    Story:
    {story_background}

    Please return a summary that contains the key characters, conflicts, and plot points, between 300 and 500 words.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a skilled literary editor."},
                {"role": "user", "content": prompt}
            ]
        )
        summary = response.choices[0].message['content'].strip()
        return summary
    except Exception as e:
        print(f"Error generating summary: {e}")
        return story_background  # In case of error, return the original text


# 生成视频提示词
def generate_video_prompt(summary: str) -> str:
    prompt = f"""
    Create a detailed video prompt for a short film based on the following summary. Be specific, focus on actions, camera angles, character appearance, background, lighting, and environment details. The prompt should be in one continuous paragraph and should be under 200 words. Include the following elements:

    1. Main action described in one sentence.
    2. Specific details about actions and gestures.
    3. Precise description of the character's appearance.
    4. Background and environment details.
    5. Camera angles and movement.
    6. Lighting and color effects.
    7. Any changes or sudden events during the scene.

    Summary:
    {summary}

    Please return the video prompt in English, keeping it clear, detailed, and under 200 words.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a skilled scriptwriter."},
                {"role": "user", "content": prompt}
            ]
        )
        video_prompt = response.choices[0].message['content'].strip()
        return video_prompt
    except Exception as e:
        print(f"Error generating video prompt: {e}")
        return ""  # Return empty string in case of error


# 调用视频生成接口
def generate_video(prompt: str):
    url = "https://api.siliconflow.cn/v1/video/submit"
    payload = {
        "model": "tencent/HunyuanVideo",
        "prompt": prompt
    }
    headers = {
        "Authorization": "Bearer sk-vkgmcrkvldamhenfivsukhxkdlceiyonzhcnntnjjqfqsnkd",  # 替换为你的实际 API 密钥
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        response_data = response.json()
        request_id = response_data.get("requestId")
        print("Video generation request ID:", request_id)
        return request_id
    except Exception as e:
        print(f"Error generating video: {e}")
        return None


# 查询视频状态并获取视频链接
def get_video_status(request_id: str):
    url = "https://api.siliconflow.cn/v1/video/status"
    payload = {"requestId": request_id}
    headers = {
        "Authorization": "Bearer sk-vkgmcrkvldamhenfivsukhxkdlceiyonzhcnntnjjqfqsnkd",  # 替换为你的实际 API 密钥
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        response_data = response.json()

        status = response_data.get("status")

        if status == "Succeed":
            video_url = response_data["results"]["videos"][0]["url"]
            print("Video URL:", video_url)
            return video_url
        elif status == "InQueue":
            print(f"Video is still in queue, position: {response_data.get('position')}. Retrying...")
            return None
        else:
            print(f"Error: {status}, Reason: {response_data.get('reason')}")
            return None

    except Exception as e:
        print(f"Error checking video status: {e}")
        return None


# 下载视频并保存
def download_video(video_url: str, save_path: str):
    try:
        response = requests.get(video_url)
        response.raise_for_status()  # 检查请求是否成功

        # 将视频内容写入文件
        with open(save_path, 'wb') as f:
            f.write(response.content)

        print(f"Video downloaded successfully and saved to: {save_path}")
    except Exception as e:
        print(f"Error downloading video: {e}")


# 轮询查询视频状态，直到视频生成成功
def poll_for_video(request_id: str, save_path: str):
    """
    轮询查询视频生成状态，直到成功获取视频链接。
    """
    while True:
        video_url = get_video_status(request_id)
        if video_url:
            download_video(video_url, save_path)
            break
        else:
            time.sleep(30)  # 等待 30 秒后再次查询


def main():
    # 设定总结 JSON 文件存放目录和输出的剧本文件目录
    novel_file = "./novel/chapter_1.json"  # 从 ./novel 加载章节数据
    chapter_data = load_json_file(novel_file)
    story_background = merge_text_from_chunks(chapter_data)  # 拼接所有chunk的文本

    # 生成文本总结
    summary = summarize_text(story_background)
    print("Story Summary:", summary)

    # 生成视频提示词
    video_prompt = generate_video_prompt(summary)
    print("Generated Video Prompt:", video_prompt)

    # 调用视频生成接口
    if video_prompt:
        request_id = generate_video(video_prompt)
        if request_id:
            # 设置保存路径
            save_path = './Librian_win64_2011/Librian面板/project/黑风岭/我的視頻/generated_video.mp4'
            # 轮询查询视频状态并下载视频
            poll_for_video(request_id, save_path)


if __name__ == "__main__":
    main()
