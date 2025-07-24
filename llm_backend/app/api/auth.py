from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import create_access_token, get_current_user
from app.schemas.user import UserCreate, UserResponse, Token, UserLogin
from app.services.user_service import UserService
from datetime import timedelta
from app.core.config import settings
from app.models.user import User

router = APIRouter()

# response_model 就是 声明响应的类型，简单理解就是执行完函数后，返回的结果，需要和 UserResponse 类型一致
# 详细文档可以看：https://fastapi.tiangolo.com/tutorial/response-model/?h=
@router.post("/register", response_model=UserResponse)
# Depends(get_db) 表示 db 参数是一个依赖项，它会调用 get_db 函数来获取一个数据库会话（AsyncSession）。
# FastAPI 会在处理请求时自动执行 get_db 函数，并将返回的结果传递给 register 函数的 db 参数。
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)): 
    try:
        user_service = UserService(db)
        user = await user_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/token", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    user = await user_service.authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/validate-token")
async def validate_token(current_user: User = Depends(get_current_user)):
    """验证token是否有效"""
    return {"valid": True, "user_id": current_user.id}

@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前登录用户的信息"""
    return current_user