import os
from transformers import pipeline
from PIL import Image
import requests
from io import BytesIO

# 加载 RMBG-1.4 模型
pipe = pipeline("image-segmentation", model="briaai/RMBG-1.4", trust_remote_code=True)

# 目标文件夹路径
image_dir = './Librian_win64_2011/Librian面板/project/黑风岭/我的立繪'

def process_image(image_path):
    """
    对图片进行背景移除处理，并覆盖源文件。
    """
    try:
        # 使用 pipeline 进行抠图
        pillow_mask = pipe(image_path, return_mask=True)  # 获取掩码
        processed_image = pipe(image_path)  # 应用掩码并生成抠图后的图像

        # 保存处理后的图像，覆盖原图
        processed_image.save(image_path)
        print(f"已处理并覆盖：{image_path}")
    except Exception as e:
        print(f"处理图像 {image_path} 时出错：{e}")

def process_all_images_in_directory(directory):
    """
    处理指定目录下所有的 .png 图像。
    """
    for filename in os.listdir(directory):
        if filename.endswith(".png"):
            image_path = os.path.join(directory, filename)
            process_image(image_path)

# 处理目录中的所有图片
process_all_images_in_directory(image_dir)
