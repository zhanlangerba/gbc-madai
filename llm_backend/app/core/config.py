from pydantic_settings import BaseSettings
from enum import Enum
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent
ENV_FILE = ROOT_DIR / ".env"

class ServiceType(str, Enum):
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"

class Settings(BaseSettings):
    # Deepseek settings
    DEEPSEEK_API_KEY: str
    DEEPSEEK_BASE_URL: str
    DEEPSEEK_MODEL: str
    DEEPSEEK_REASON_MODEL: str  # 专门用于推理任务的模型
    
    # Vision Model settings (独立配置)
    VISION_API_KEY: str
    VISION_BASE_URL: str
    VISION_MODEL: str

    # Embedding Model settings (独立配置)
    EMBEDDING_API_KEY: str
    EMBEDDING_BASE_URL: str
    EMBEDDING_MODEL: str
    
    # Ollama settings
    OLLAMA_BASE_URL: str
    OLLAMA_CHAT_MODEL: str
    OLLAMA_REASON_MODEL: str
    OLLAMA_EMBEDDING_MODEL: str
    OLLAMA_AGENT_MODEL: str
    # Service selection
    CHAT_SERVICE: ServiceType = ServiceType.DEEPSEEK
    REASON_SERVICE: ServiceType = ServiceType.DEEPSEEK
    AGENT_SERVICE: ServiceType = ServiceType.DEEPSEEK
    
    # Search settings
    SEARCH_SERVICE: str = "bocha_ai"  # 默认使用博查AI搜索

    # SerpAPI settings
    SERPAPI_KEY: str

    # 百度AI搜索设置
    BAIDU_AI_SEARCH_API_KEY: str
    BAIDU_AI_SEARCH_BASE_URL: str = "https://qianfan.baidubce.com/v2/ai_search"
    BAIDU_AI_SEARCH_MODEL: str = "ernie-3.5-8k"

    # 博查AI搜索设置
    BOCHA_AI_API_KEY: str
    BOCHA_AI_BASE_URL: str = "https://api.bochaai.com/v1"

    SEARCH_RESULT_COUNT: int = 3
    
    # Database settings
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    
    # Neo4j settings
    NEO4J_URL: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    NEO4J_DATABASE: str = "neo4j"
    
    # JWT settings
    SECRET_KEY: str = "your-secret-key"  # 在生产环境中使用安全的密钥
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis settings
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    REDIS_CACHE_EXPIRE: int = 3600
    REDIS_CACHE_THRESHOLD: float = 0.8
    
    # Embedding settings 
    EMBEDDING_TYPE: str = "ollama"  # ollama 或 sentence_transformer
    EMBEDDING_MODEL: str = "bge-m3"  # ollama embedding模型
    EMBEDDING_THRESHOLD: float = 0.90  # 语义相似度阈值
    
    # GraphRAG settings
    GRAPHRAG_PROJECT_DIR: str = "llm_backend/app/graphrag"  # GraphRAG项目目录
    GRAPHRAG_DATA_DIR: str = "data"                         # 数据目录名称
    GRAPHRAG_QUERY_TYPE: str = "local"                      # 查询类型
    GRAPHRAG_RESPONSE_TYPE: str = "text"                    # 响应类型
    GRAPHRAG_COMMUNITY_LEVEL: int = 3                       # 社区级别
    GRAPHRAG_DYNAMIC_COMMUNITY: bool = False                # 是否动态选择社区

    # GraphRAG模型配置
    GRAPHRAG_API_BASE: str
    GRAPHRAG_API_KEY: str
    GRAPHRAG_MODEL_NAME: str
    Embedding_API_BASE: str
    Embedding_API_KEY: str
    Embedding_MODEL_NAME: str
    
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def REDIS_URL(self) -> str:
        """构建Redis URL"""
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def NEO4J_CONN_URL(self) -> str:
        """构建Neo4j连接URL"""
        return f"{self.NEO4J_URL}"
    
    class Config:
        env_file = str(ENV_FILE)  # 使用绝对路径
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings() 