import sys
from pathlib import Path

# 添加项目根目录到 PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

# 确保能找到 app 模块
# print(f"Python path: {sys.path}")
# print(f"Current directory: {Path.cwd()}")
# print(f"Root directory: {ROOT_DIR}")

import asyncio
from app.core.database import engine, Base
from app.models import User, Conversation, Message
from app.core.logger import get_logger

logger = get_logger(service="init_db")

async def init_db():
    try:
        logger.info("Initializing database...")
        async with engine.begin() as conn:
            # 删除所有表（如果存在）
            await conn.run_sync(Base.metadata.drop_all)
            # 创建所有表
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialization completed successfully!")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

def main():
    try:
        asyncio.run(init_db())
    except RuntimeError as e:
        logger.error(f"Runtime error: {str(e)}")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
