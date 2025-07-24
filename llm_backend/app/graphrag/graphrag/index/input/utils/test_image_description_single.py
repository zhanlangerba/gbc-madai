#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试单个图片描述生成功能的独立脚本
"""

import os
import sys
import argparse
import logging
import json
from pathlib import Path
import time
import base64
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('image_description_test.log')
    ]
)

log = logging.getLogger("image_description_test")

def generate_single_image_description(
    image_path, 
    output_file=None,
    api_key="your-openai-api-key-here",
    model="gpt-4o",
    max_retries=3,
    retry_delay=2,
    max_tokens=300,
    temperature=0.7
):
    """为单个图片生成描述"""
    # 检查图片文件是否存在
    if not image_path.exists() or not image_path.is_file():
        log.error(f"图片文件不存在或不是文件: {image_path}")
        return None
    
    log.info(f"开始处理图片: {image_path}")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 读取图片并转换为base64
    try:
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # 构建请求
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的图像描述助手。请详细描述图片中的内容，包括主要对象、场景、颜色、布局等关键信息。描述应该客观、准确、全面。"
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请详细描述这张图片的内容:"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # 发送请求并获取响应
        for attempt in range(max_retries):
            try:
                log.info(f"发送API请求 (尝试 {attempt+1}/{max_retries})")
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    description = result["choices"][0]["message"]["content"]
                    log.info(f"成功生成图片描述")
                    
                    # 保存结果
                    if output_file:
                        with open(output_file, 'w', encoding='utf-8') as f:
                            json.dump({str(image_path): description}, f, ensure_ascii=False, indent=2)
                        log.info(f"描述已保存到: {output_file}")
                    
                    return description
                else:
                    log.error(f"API请求失败: {response.status_code} - {response.text}")
                    if attempt < max_retries - 1:
                        log.info(f"等待 {retry_delay * (attempt + 1)} 秒后重试...")
                        time.sleep(retry_delay * (attempt + 1))
            except Exception as e:
                log.error(f"处理图片时出错: {str(e)}")
                if attempt < max_retries - 1:
                    log.info(f"等待 {retry_delay * (attempt + 1)} 秒后重试...")
                    time.sleep(retry_delay * (attempt + 1))
        
        log.error("所有尝试均失败")
        return "[描述生成失败: 多次尝试后仍然失败]"
    
    except Exception as e:
        log.error(f"读取图片失败: {str(e)}")
        return f"[描述生成失败: 无法读取图片 - {str(e)}]"


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='测试单个图片描述生成功能')
    parser.add_argument('--image_path', type=str, required=True, help='图片文件路径')
    parser.add_argument('--output_file', type=str, default='image_description.json', help='输出文件路径')
    parser.add_argument('--model', type=str, default='gpt-4o', help='使用的模型名称')
    parser.add_argument('--max_tokens', type=int, default=300, help='生成描述的最大token数')
    parser.add_argument('--temperature', type=float, default=0.7, help='生成描述的随机性，0-1之间')
    
    args = parser.parse_args()
    
    # 检查图片文件
    image_path = Path(args.image_path)
    if not image_path.exists():
        log.error(f"图片文件不存在: {image_path}")
        return 1
    
    # 设置输出文件
    output_file = Path(args.output_file)
    
    # 记录参数
    log.info(f"图片文件: {image_path}")
    log.info(f"输出文件: {output_file}")
    log.info(f"使用模型: {args.model}")
    log.info(f"最大token数: {args.max_tokens}")
    log.info(f"温度: {args.temperature}")
    
    # 开始处理
    start_time = time.time()
    log.info("开始生成图片描述...")
    
    try:
        description = generate_single_image_description(
            image_path=image_path,
            output_file=output_file,
            model=args.model,
            max_tokens=args.max_tokens,
            temperature=args.temperature
        )
        
        if description:
            log.info(f"处理完成，描述已保存到: {output_file}")
            log.info(f"描述内容:\n{description}")
        else:
            log.error("生成描述失败")
        
        # 打印处理时间
        elapsed_time = time.time() - start_time
        log.info(f"总处理时间: {elapsed_time:.2f} 秒")
        
        return 0 if description else 1
    
    except Exception as e:
        log.error(f"处理过程中出错: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main()) 