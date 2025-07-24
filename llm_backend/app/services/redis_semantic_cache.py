from typing import Dict, List, Optional
import redis
import hashlib
import numpy as np
import json
import time
import aiohttp
import openai
from app.core.config import settings
from app.core.logger import get_logger
import asyncio
from datetime import datetime

logger = get_logger(service="redis_cache")

class RedisSemanticCache:
    """基于语义的 Redis 缓存实现"""
    
    def __init__(
        self,
        redis_url: str = None,
        model_name: str = None,
        score_threshold: float = None,
        prefix: str = "cache",
        user_id: Optional[int] = None,  # 添加用户ID
        max_cache_size: int = 1000,  # 每个用户最大缓存条数
        cleanup_interval: int = 3600  # 清理间隔(秒)
    ):
        self.redis = redis.from_url(redis_url or settings.REDIS_URL)
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.score_threshold = score_threshold or settings.REDIS_CACHE_THRESHOLD
        self.prefix = f"{prefix}:{user_id}" if user_id else prefix
        self.max_cache_size = max_cache_size
        self.cleanup_interval = cleanup_interval

        # 配置OpenAI客户端用于嵌入
        self.embedding_client = openai.AsyncOpenAI(
            api_key=settings.EMBEDDING_API_KEY,
            base_url=settings.EMBEDDING_BASE_URL
        )

        # 启动自动清理任务
        asyncio.create_task(self._auto_cleanup())
        
    async def _get_embedding(self, text: str) -> List[float]:
        """使用OpenAI兼容API生成文本向量"""
        try:
            response = await self.embedding_client.embeddings.create(
                model=self.model_name,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}", exc_info=True)
            # 如果API失败，尝试使用本地fallback（可选）
            raise

    async def get_embedding(self, text: str) -> List[float]:
        """获取文本向量"""
        try:
            # 使用OpenAI兼容API的embedding接口
            embedding = await self._get_embedding(text)
            if not embedding:
                raise ValueError("Failed to get embedding")
            return embedding
        except Exception as e:
            logger.error(f"Error in get_embedding: {str(e)}", exc_info=True)
            raise
        
    def _get_vector_key(self, message: str) -> str:
        """生成向量存储的键名"""
        message_hash = hashlib.md5(message.encode()).hexdigest()
        return f"{self.prefix}:vec:{message_hash}"
        
    def _get_response_key(self, message: str) -> str:
        """生成响应存储的键名"""
        message_hash = hashlib.md5(message.encode()).hexdigest()
        return f"{self.prefix}:resp:{message_hash}"
        
    def _get_metadata_key(self, message: str) -> str:
        """生成元数据存储的键名"""
        message_hash = hashlib.md5(message.encode()).hexdigest()
        return f"{self.prefix}:meta:{message_hash}"

    def _get_last_user_message(self, messages: List[Dict]) -> str:
        """获取最后一条用户消息"""
        for msg in reversed(messages):
            if msg["role"] == "user":
                return msg["content"]
        return ""

    async def _auto_cleanup(self):
        """自动清理过期和超量的缓存"""
        while True:
            try:
                # 获取当前用户的所有缓存键
                pattern = f"{self.prefix}:meta:*"
                all_keys = [key.decode('utf-8') for key in self.redis.keys(pattern)]  # 解码key
                
                if len(all_keys) > self.max_cache_size:
                    # 按访问时间排序
                    cache_items = []
                    for key in all_keys:
                        metadata = json.loads(self.redis.get(key.encode('utf-8')).decode('utf-8'))  # 编码key再获取
                        cache_items.append((key, metadata.get("last_access", 0)))
                    
                    # 按最后访问时间排序
                    cache_items.sort(key=lambda x: x[1])
                    
                    # 删除最旧的条目直到达到限制
                    items_to_remove = len(all_keys) - self.max_cache_size
                    for key, _ in cache_items[:items_to_remove]:
                        hash_id = key.split(":")[-1]
                        await self._remove_cache_item(hash_id)
                        
                logger.info(f"Cache cleanup completed for prefix {self.prefix}")
                
            except Exception as e:
                logger.error(f"Error in cache cleanup: {str(e)}", exc_info=True)
                
            await asyncio.sleep(self.cleanup_interval)

    async def _remove_cache_item(self, hash_id: str):
        """删除一个缓存项的所有相关键"""
        try:
            # 所有key都需要编码
            self.redis.delete(
                f"{self.prefix}:vec:{hash_id}".encode('utf-8'),
                f"{self.prefix}:resp:{hash_id}".encode('utf-8'),
                f"{self.prefix}:meta:{hash_id}".encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Error removing cache item: {str(e)}", exc_info=True)

    async def _update_metadata(self, message: str):
        """更新缓存项的元数据"""
        try:
            meta_key = self._get_metadata_key(message)
            # 从Redis读取的是bytes,需要解码
            current_meta = self.redis.get(meta_key)
            if current_meta:
                current_meta = json.loads(current_meta.decode('utf-8'))
            else:
                current_meta = {"access_count": 0}
                
            metadata = {
                "last_access": datetime.now().timestamp(),
                "access_count": current_meta["access_count"] + 1
            }
            self.redis.set(meta_key, json.dumps(metadata), ex=settings.REDIS_CACHE_EXPIRE)
        except Exception as e:
            logger.error(f"Error updating metadata: {str(e)}", exc_info=True)

    async def lookup(self, messages: List[Dict]) -> Optional[str]:
        """查找缓存的响应"""
        try:
            user_message = self._get_last_user_message(messages)
            if not user_message:
                return None

            current_vector = await self.get_embedding(user_message)
            
            # 获取当前用户的所有缓存向量
            pattern = f"{self.prefix}:vec:*"
            all_vectors = [key.decode('utf-8') for key in self.redis.keys(pattern)]  # 解码key
            max_similarity = 0
            most_similar_key = None
            
            for vec_key in all_vectors:
                cached_vector = json.loads(self.redis.get(vec_key.encode('utf-8')).decode('utf-8'))  # 编码key再获取
                similarity = np.dot(current_vector, cached_vector) / (
                    np.linalg.norm(current_vector) * np.linalg.norm(cached_vector)
                )
                
                if similarity > max_similarity:
                    max_similarity = similarity
                    most_similar_key = vec_key
            
            if max_similarity >= self.score_threshold and most_similar_key:
                hash_id = most_similar_key.split(":")[-1]
                resp_key = f"{self.prefix}:resp:{hash_id}"
                cached_response = self.redis.get(resp_key.encode('utf-8'))  # 编码key
                
                if cached_response:
                    # 更新访问元数据
                    await self._update_metadata(user_message)
                    logger.info(f"Cache hit with similarity: {max_similarity:.4f}")
                    return cached_response.decode('utf-8')
                    
            return None
            
        except Exception as e:
            logger.error(f"Error in lookup: {str(e)}", exc_info=True)
            return None

    async def update(self, messages: List[Dict], response: str, expire: int = None):
        """更新缓存"""
        try:
            user_message = self._get_last_user_message(messages)
            if not user_message:
                return

            vector = await self.get_embedding(user_message)
            
            vec_key = self._get_vector_key(user_message)
            resp_key = self._get_response_key(user_message)
            meta_key = self._get_metadata_key(user_message)
            
            expire = expire or settings.REDIS_CACHE_EXPIRE
            
            # 存储向量、响应和元数据 - 确保存储为字符串
            self.redis.set(vec_key, json.dumps(vector), ex=expire)
            self.redis.set(resp_key, response.encode('utf-8'), ex=expire)  # 编码为bytes
            
            metadata = {
                "created_at": datetime.now().timestamp(),
                "last_access": datetime.now().timestamp(),
                "access_count": 1
            }
            self.redis.set(meta_key, json.dumps(metadata), ex=expire)
            
            logger.info(f"Cache updated for message: {user_message[:50]}...")
            
        except Exception as e:
            logger.error(f"Error in update: {str(e)}", exc_info=True) 