from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.hashing import get_password_hash, verify_password
from datetime import datetime
from typing import Optional
from app.core.logger import get_logger

logger = get_logger(service="user_service")

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        # 同时检查用户名和邮箱是否已存在
        query = select(User).where(
            or_(
                User.email == user_data.email,
                User.username == user_data.username
            )
        )
        result = await self.db.execute(query)
        existing_user = result.scalar_one_or_none() # 获取查询结果中的第一个用户，如果存在则返回，否则返回 None
        
        if existing_user:
            if existing_user.email == user_data.email:
                raise ValueError("该邮箱已经被注册！")
            else:
                raise ValueError("用户名已被占用！")
        
        # 创建新用户
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password)
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        验证用户
        password: 前端传来的 SHA256 哈希密码
        """
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()  # 获取查询结果中的第一个用户，如果存在则返回，否则返回 None
        
        if not user:
            logger.warning(f"User not found: {email}")
            return None
            
        if not verify_password(password, user.password_hash):
            logger.warning(f"Invalid password for user: {email}")
            return None
            
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        await self.db.commit()
        
        return user

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() 