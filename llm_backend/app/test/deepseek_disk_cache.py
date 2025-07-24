from openai import OpenAI
from dotenv import load_dotenv
import os
import time

# 加载 .env 文件
load_dotenv()

# 实例化 DeepSeek API 客户端
client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'), 
    base_url=os.getenv('DEEPSEEK_BASE_URL')
)


def chat_with_cache(messages):
    """单轮对话，返回响应并打印缓存情况"""
    start_time = time.time()
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )
    
    elapsed_time = time.time() - start_time
    
    # 打印缓存命中情况
    cache_hit = response.usage.prompt_cache_hit_tokens
    cache_miss = response.usage.prompt_cache_miss_tokens
    print(f"\n[耗时 {elapsed_time:.2f}s]")
    print(f"缓存命中: {cache_hit} tokens")
    print(f"缓存未命中: {cache_miss} tokens")
    
    return response.choices[0].message

def main():
    # 初始化对话历史
    messages = [
        {"role": "system", "content": "你是一位乐于助人的助手"}
    ]
    
    print("开始对话 (输入 'q' 退出):")
    
    try:
        while True:
            # 获取用户输入
            user_input = input("\n用户: ")
            if user_input.lower() == '退出':
                break
            
            # 添加用户消息
            messages.append({"role": "user", "content": user_input})
            
            # 获取模型回复
            assistant_message = chat_with_cache(messages)
            
            # 添加模型消息到历史列表中
            messages.append({
                "role": assistant_message.role,
                "content": assistant_message.content
            })
            
            # 打印模型回复
            print(f"AI助手: {assistant_message.content}")
            
    except KeyboardInterrupt:
        print("\n对话已终止")
    except Exception as e:
        print(f"\n发生错误: {e}")

if __name__ == "__main__":
    main()
