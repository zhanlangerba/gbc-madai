from typing import Union
from app.core.config import settings, ServiceType
from app.services.deepseek_service import DeepseekService
from app.services.ollama_service import OllamaService
from app.services.search_service import SearchService
class LLMFactory:
    @staticmethod
    def create_chat_service():
        """创建聊天服务实例"""
        if settings.CHAT_SERVICE == ServiceType.DEEPSEEK:
            # 如果.env文件中CHAT_SERVICE设置为DEEPSEEK，则使用DeepseekService
            return DeepseekService()
        else:
            # 否则使用OllamaService
            return OllamaService()

    @staticmethod
    def create_reasoner_service():
        """创建推理服务实例"""
        # 如果.env文件中REASON_SERVICE设置为DEEPSEEK，则使用DeepseekService的推理模式
        if settings.REASON_SERVICE == ServiceType.DEEPSEEK:
            return DeepseekService(use_reasoning=True)
        else:
            # 否则使用OllamaService
            return OllamaService()
    
    @staticmethod
    def create_search_service():
        """创建搜索服务实例"""
        return SearchService()