from openai import OpenAI
import os
from dotenv import load_dotenv

# 获取项目根目录的 .env 文件
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
env_path = os.path.join(root_dir, 'llm_backend', '.env')

# 加载 .env 文件
load_dotenv(env_path)

def sync_chat():
    try:
        client = OpenAI(
            api_key=os.getenv('DEEPSEEK_API_KEY'),
            base_url=os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
        )

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一位乐于助人的智能小助手"},
                {"role": "user", "content": "你好，请你介绍一下你自己。"},
            ],
            stream=False
        )

        print(response.choices[0].message.content)
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    sync_chat() 