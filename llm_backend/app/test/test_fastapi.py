from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()  # 创建 FastAPI 应用实例

class Item(BaseModel):
    name: str  # 项目的名称
    description: str = None  # 项目的描述，默认为 None

@app.get("/")  # 定义 GET 请求的根路径
async def read_root():
    """返回欢迎消息"""
    return {"message": "Hello, World"}

@app.post("/items/")  # 定义 POST 请求的 /items 路径
async def create_item(item: Item):
    """创建一个新项目并返回其数据"""
    return item  # 返回创建的项目数据