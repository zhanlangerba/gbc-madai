from typing import List, Dict, AsyncGenerator, Callable, Optional
from openai import AsyncOpenAI
from app.core.config import settings
import json
from app.core.logger import get_logger
from app.core.database import AsyncSessionLocal
from app.models.conversation import Conversation, DialogueType
from app.models.message import Message
from app.services.redis_semantic_cache import RedisSemanticCache
import time
import asyncio

logger = get_logger(service="deepseek")

class DeepseekService:
    def __init__(self, model: str = "deepseek-chat", use_reasoning: bool = False):
        logger.info("Initializing Deepseek Service")
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
        # 根据use_reasoning参数选择模型
        if use_reasoning:
            self.model = settings.DEEPSEEK_REASON_MODEL
            logger.info(f"Using reasoning model: {self.model}")
        else:
            self.model = settings.DEEPSEEK_MODEL or model
            logger.info(f"Using chat model: {self.model}")

        self.cache = RedisSemanticCache(prefix="deepseek")

    async def _stream_cached_response(self, response: str, delay: float = 0.05) -> AsyncGenerator[str, None]:
        """模拟流式返回缓存的响应"""
        # 每次返回4个字符
        chunks = [response[i:i + 4] for i in range(0, len(response), 4)]
        for chunk in chunks:
            await asyncio.sleep(delay)  # 50ms延迟
            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

    async def generate_stream(
        self, 
        messages: List[Dict],
        user_id: Optional[int] = None,
        conversation_id: Optional[int] = None,
        on_complete: Optional[Callable[[int, int, List[Dict], str], None]] = None
    ) -> AsyncGenerator[str, None]:
        """流式生成回复"""
        try:
            # 为每个用户创建独立的缓存实例
            cache = RedisSemanticCache(prefix="deepseek", user_id=user_id)
            
            start_time = time.time()
            
            # 检查缓存
            cached_response = await cache.lookup(messages)
            if cached_response:
                response_time = time.time() - start_time
                logger.info(f"Cache hit! Response time: {response_time:.4f} seconds")
                
                # 模拟流式返回，因为速率太快了
                async for chunk in self._stream_cached_response(cached_response):
                    yield chunk
                
                if on_complete and user_id is not None and conversation_id is not None:
                    await on_complete(user_id, conversation_id, messages, cached_response)
                return

            # 缓存未命中,调用API
            full_response = []
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True
            )

            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    # 使用 ensure_ascii=False 来保持中文字符
                    content = json.dumps(chunk.choices[0].delta.content, ensure_ascii=False)

                    full_response.append(content)
                    yield f"data: {content}\n\n"
            
            # 完整响应
            complete_response = "".join(full_response)
            
            # 更新缓存
            await cache.update(messages, complete_response)
            
            response_time = time.time() - start_time
            logger.info(f"Cache miss. Response time: {response_time:.4f} seconds")
            
            # 如果有回调，执行回调
            if on_complete and user_id is not None and conversation_id is not None:
                await on_complete(user_id, conversation_id, messages, complete_response)
                
        except Exception as e:
            logger.error(f"Error in generate_stream: {str(e)}", exc_info=True)
            error_msg = json.dumps(f"生成回复时出错: {str(e)}", ensure_ascii=False)
            yield f"data: {error_msg}\n\n"

    async def generate(self, messages: List[Dict]) -> str:
        """非流式生成回复"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Generation error: {str(e)}")
            raise

    async def generate_reasoning_stream(
        self,
        messages: List[Dict],
        user_id: Optional[int] = None,
        conversation_id: Optional[int] = None,
        on_complete: Optional[Callable[[int, int, List[Dict], str], None]] = None
    ) -> AsyncGenerator[str, None]:
        """使用推理模型进行流式生成"""
        try:
            # 为推理任务创建独立的缓存实例
            cache = RedisSemanticCache(prefix="deepseek_reasoning", user_id=user_id)

            start_time = time.time()

            # 检查缓存
            cached_response = await cache.lookup(messages)
            if cached_response:
                response_time = time.time() - start_time
                logger.info(f"Reasoning cache hit! Response time: {response_time:.4f} seconds")

                # 模拟流式返回
                async for chunk in self._stream_cached_response(cached_response):
                    yield chunk

                if on_complete and user_id is not None and conversation_id is not None:
                    await on_complete(user_id, conversation_id, messages, cached_response)
                return

            # 缓存未命中,使用推理模型调用API
            full_response = []
            reasoning_model = settings.DEEPSEEK_REASON_MODEL
            logger.info(f"Using reasoning model: {reasoning_model}")

            response = await self.client.chat.completions.create(
                model=reasoning_model,
                messages=messages,
                stream=True
            )

            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = json.dumps(chunk.choices[0].delta.content, ensure_ascii=False)
                    full_response.append(content)
                    yield f"data: {content}\n\n"

            # 完整响应
            complete_response = "".join(full_response)

            # 更新缓存
            await cache.update(messages, complete_response)

            response_time = time.time() - start_time
            logger.info(f"Reasoning cache miss. Response time: {response_time:.4f} seconds")

            # 如果有回调，执行回调
            if on_complete and user_id is not None and conversation_id is not None:
                await on_complete(user_id, conversation_id, messages, complete_response)

        except Exception as e:
            logger.error(f"Error in generate_reasoning_stream: {str(e)}", exc_info=True)
            error_msg = json.dumps(f"推理生成时出错: {str(e)}", ensure_ascii=False)
            yield f"data: {error_msg}\n\n"

    async def generate_reasoning(self, messages: List[Dict]) -> str:
        """使用推理模型进行非流式生成"""
        try:
            reasoning_model = settings.DEEPSEEK_REASON_MODEL
            logger.info(f"Using reasoning model: {reasoning_model}")

            response = await self.client.chat.completions.create(
                model=reasoning_model,
                messages=messages,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Reasoning generation error: {str(e)}")
            raise