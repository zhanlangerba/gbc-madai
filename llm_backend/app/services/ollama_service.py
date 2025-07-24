from typing import List, Dict, AsyncGenerator, Optional, Callable
import aiohttp
import json
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(service="ollama")

class OllamaService:
    def __init__(self):
        logger.info("Initializing Ollama Service")
        self.base_url = settings.OLLAMA_BASE_URL
        self.chat_model = settings.OLLAMA_CHAT_MODEL
        self.reason_model = settings.OLLAMA_REASON_MODEL

    async def generate_stream(
        self, 
        messages: List[Dict],
        user_id: Optional[int] = None,
        conversation_id: Optional[int] = None,
        on_complete: Optional[Callable] = None
    ) -> AsyncGenerator[str, None]:
        """流式生成回复"""
        try:
            # 根据不同的用途使用不同的模型
            model = self.reason_model
            logger.info(f"Using model: {model}")
            
            full_response = []
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": True,
                        "keep_alive": -1,
                        "options": {
                            "temperature": 0.7,
                        }
                    }
                ) as response:
                    async for line in response.content:
                        if line:
                            try:
                                chunk = json.loads(line)
                                if content := chunk.get("message", {}).get("content"):
                                    full_response.append(content)
                                    # 使用 json.dumps 确保内容格式正确
                                    content = json.dumps(content, ensure_ascii=False)
                                    yield f"data: {content}\n\n"
                            except json.JSONDecodeError as e:
                                logger.error(f"JSON decode error: {str(e)}")
                                continue

            # 如果有回调函数，调用它
            if on_complete:
                complete_response = "".join(full_response)
                await on_complete(user_id, conversation_id, messages, complete_response)

        except Exception as e:
            logger.error(f"Stream generation error: {str(e)}")
            error_msg = json.dumps(f"生成回复时出错: {str(e)}", ensure_ascii=False)
            yield f"data: {error_msg}\n\n"
            raise

    async def generate(self, messages: List[Dict]) -> str:
        """非流式生成回复"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.chat_model,
                        "messages": messages,
                        "stream": False,
                        "keep_alive": -1,
                        "options": {
                            "temperature": 0.7,
                        }
                    }
                ) as response:
                    result = await response.json()
                    return result["message"]["content"]

        except Exception as e:
            print(f"Generation error: {str(e)}")
            raise 