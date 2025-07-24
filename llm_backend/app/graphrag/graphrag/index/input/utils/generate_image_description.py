#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试图片描述生成功能的独立脚本
"""

import os
import sys
import argparse
import logging
import json
from pathlib import Path
import time

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

# 导入图片描述生成函数
# 注意：如果直接运行此脚本，请确保graphrag包在Python路径中
# 或者将下面的导入语句替换为直接复制函数代码
try:
    from graphrag.index.input.util import generate_image_descriptions, generate_image_descriptions_sync
except ImportError:
    log.error("无法导入graphrag包，请确保它已安装或在Python路径中")
    
    # 提供一个简化版的函数实现，以便脚本可以独立运行
    import base64
    import requests
    
    def generate_image_descriptions_sync(
        image_dir, 
        output_file=None,
        api_key=None,
        model="gpt-4o",
        max_retries=3,
        retry_delay=2,
        max_tokens=300,
        temperature=0.7
    ):
        """简化版的同步图片描述生成函数"""
        # 获取API密钥
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("未提供API密钥，请设置OPENAI_API_KEY环境变量或直接传入api_key参数")
        
        # 检查图片目录是否存在
        if not image_dir.exists() or not image_dir.is_dir():
            log.warning(f"图片目录不存在或不是目录: {image_dir}")
            return {}
        
        # 获取所有图片文件
        image_files = []
        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            image_files.extend(list(image_dir.glob(f"*{ext}")))
            image_files.extend(list(image_dir.glob(f"*{ext.upper()}")))
        
        if not image_files:
            log.warning(f"图片目录中没有找到图片: {image_dir}")
            return {}
        
        log.info(f"找到 {len(image_files)} 张图片，开始生成描述")
        
        descriptions = {}
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        for i, image_path in enumerate(image_files):
            log.info(f"处理图片 {i+1}/{len(image_files)}: {image_path.name}")
            
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
                success = False
                for attempt in range(max_retries):
                    try:
                        response = requests.post(
                            "https://api.openai.com/v1/chat/completions",
                            headers=headers,
                            json=payload
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            description = result["choices"][0]["message"]["content"]
                            descriptions[str(image_path)] = description
                            log.info(f"成功生成图片描述: {image_path.name}")
                            success = True
                            break
                        else:
                            log.error(f"API请求失败 (尝试 {attempt+1}/{max_retries}): {response.status_code} - {response.text}")
                            if attempt < max_retries - 1:
                                time.sleep(retry_delay * (attempt + 1))  # 指数退避
                    except Exception as e:
                        log.error(f"处理图片时出错 (尝试 {attempt+1}/{max_retries}): {str(e)}")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay * (attempt + 1))
                
                if not success:
                    descriptions[str(image_path)] = f"[描述生成失败: 多次尝试后仍然失败]"
            
            except Exception as e:
                log.error(f"读取图片失败: {image_path} - {str(e)}")
                descriptions[str(image_path)] = f"[描述生成失败: 无法读取图片 - {str(e)}]"
            
            # 每处理完一张图片后保存一次，防止中途失败
            if output_file is not None:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(descriptions, f, ensure_ascii=False, indent=2)
            
            # 添加延迟，避免API限制
            if i < len(image_files) - 1:
                time.sleep(1)
        
        log.info(f"所有图片处理完成，共生成 {len(descriptions)} 个描述")
        
        # 最终保存
        if output_file is not None and descriptions:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(descriptions, f, ensure_ascii=False, indent=2)
            log.info(f"所有描述已保存到: {output_file}")
        
        return descriptions


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='测试图片描述生成功能')
    parser.add_argument('--image_dir', type=str, required=True, help='图片目录路径')
    parser.add_argument('--output_file', type=str, default='image_descriptions.json', help='输出文件路径')
    parser.add_argument('--api_key', type=str, help='OpenAI API密钥，如果不提供则从环境变量获取')
    parser.add_argument('--model', type=str, default='gpt-4o', help='使用的模型名称')
    parser.add_argument('--max_tokens', type=int, default=300, help='生成描述的最大token数')
    parser.add_argument('--temperature', type=float, default=0.7, help='生成描述的随机性，0-1之间')
    
    args = parser.parse_args()
    
    # 检查API密钥
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        log.error("未提供API密钥，请设置OPENAI_API_KEY环境变量或使用--api_key参数")
        return 1
    
    # 检查图片目录
    image_dir = Path(args.image_dir)
    if not image_dir.exists() or not image_dir.is_dir():
        log.error(f"图片目录不存在或不是目录: {image_dir}")
        return 1
    
    # 设置输出文件
    output_file = Path(args.output_file)
    
    # 记录参数
    log.info(f"图片目录: {image_dir}")
    log.info(f"输出文件: {output_file}")
    log.info(f"使用模型: {args.model}")
    log.info(f"最大token数: {args.max_tokens}")
    log.info(f"温度: {args.temperature}")
    
    # 开始处理
    start_time = time.time()
    log.info("开始生成图片描述...")
    
    try:
        descriptions = generate_image_descriptions_sync(
            image_dir=image_dir,
            output_file=output_file,
            api_key=api_key,
            model=args.model,
            max_tokens=args.max_tokens,
            temperature=args.temperature
        )
        
        # 打印结果摘要
        log.info(f"处理完成，共生成 {len(descriptions)} 个描述")
        log.info(f"描述已保存到: {output_file}")
        
        # 打印处理时间
        elapsed_time = time.time() - start_time
        log.info(f"总处理时间: {elapsed_time:.2f} 秒")
        
        # 打印一个示例描述
        if descriptions:
            sample_key = next(iter(descriptions))
            sample_desc = descriptions[sample_key]
            log.info(f"示例描述 ({sample_key}):\n{sample_desc[:200]}...")
        
        return 0
    
    except Exception as e:
        log.error(f"处理过程中出错: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main()) 