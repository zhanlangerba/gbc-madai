from typing import List, Dict
from app.core.database import AsyncSessionLocal
from app.models.conversation import Conversation, DialogueType
from app.models.message import Message
from app.core.logger import get_logger
from sqlalchemy import select

logger = get_logger(service="conversation")

class ConversationService:
    @staticmethod
    def get_conversation_title(message: str, max_length: int = 20) -> str:
        """从消息中提取会话标题"""
        title = " ".join(message.split())
        if len(title) > max_length:
            title = title[:max_length] + "..."
        return title

    @staticmethod
    async def create_conversation(user_id: int) -> int:
        """创建新会话"""
        async with AsyncSessionLocal() as db:
            conversation = Conversation(
                user_id=user_id,
                title="新会话",
                dialogue_type=DialogueType.NORMAL
            )
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)
            
            logger.info(f"Created new conversation {conversation.id} for user {user_id}")
            return conversation.id

    @staticmethod
    async def save_message(
        user_id: int, 
        conversation_id: int, 
        messages: List[Dict], 
        response: str
    ):
        """保存对话消息"""
        try:
            async with AsyncSessionLocal() as db:
                # 查询会话
                stmt = select(Conversation).where(Conversation.id == conversation_id)
                result = await db.execute(stmt)
                conversation = result.scalar_one_or_none()
                
                if not conversation:
                    logger.error(f"Conversation {conversation_id} not found")
                    return
                    
                # 查询现有消息数量
                stmt = select(Message).where(Message.conversation_id == conversation_id)
                result = await db.execute(stmt)
                messages_count = len(result.all())
                
                # 获取用户的问题内容
                user_content = next((msg["content"] for msg in messages if msg["role"] == "user"), "")
                
                # 如果是第一条消息，更新会话标题
                if messages_count == 0:
                    title = ConversationService.get_conversation_title(user_content)
                    conversation.title = title
                
                # 保存用户消息
                user_message = Message(
                    conversation_id=conversation_id,
                    sender="user",
                    content=user_content
                )
                db.add(user_message)
                
                # 保存助手回复
                assistant_message = Message(
                    conversation_id=conversation_id,
                    sender="assistant",
                    content=response
                )
                db.add(assistant_message)
                
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}", exc_info=True)
            logger.error(f"Error details - user_id: {user_id}, conversation_id: {conversation_id}")
            logger.error(f"Messages: {messages}")

    @staticmethod
    async def get_user_conversations(user_id: int) -> List[Dict]:
        """获取用户的所有会话"""
        try:
            async with AsyncSessionLocal() as db:
                # 查询用户的所有会话，排除标题为"新会话"的对话
                stmt = select(Conversation).where(
                    Conversation.user_id == user_id,
                    Conversation.title != "新会话"  # 添加这个条件
                ).order_by(Conversation.created_at.desc())
                
                result = await db.execute(stmt)
                conversations = result.scalars().all()
                
                return [
                    {
                        "id": conv.id,
                        "title": conv.title,
                        "created_at": conv.created_at.isoformat(),
                        "status": conv.status,
                        "dialogue_type": conv.dialogue_type.value
                    }
                    for conv in conversations
                ]
                
        except Exception as e:
            logger.error(f"Error getting conversations for user {user_id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    async def get_conversation_messages(conversation_id: int, user_id: int) -> List[Dict]:
        """获取会话的所有消息"""
        try:
            async with AsyncSessionLocal() as db:
                # 首先验证会话属于该用户
                stmt = select(Conversation).where(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id
                )
                result = await db.execute(stmt)
                conversation = result.scalar_one_or_none()
                
                if not conversation:
                    raise ValueError(f"Conversation {conversation_id} not found or not owned by user {user_id}")
                
                # 查询会话的所有消息
                stmt = select(Message).where(
                    Message.conversation_id == conversation_id
                ).order_by(Message.created_at)
                
                result = await db.execute(stmt)
                messages = result.scalars().all()
                
                return [
                    {
                        "id": msg.id,
                        "sender": msg.sender,
                        "content": msg.content,
                        "created_at": msg.created_at.isoformat(),
                        "message_type": msg.message_type
                    }
                    for msg in messages
                ]
                
        except Exception as e:
            logger.error(f"Error getting messages for conversation {conversation_id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    async def delete_conversation(conversation_id: int):
        """删除会话及其所有消息"""
        try:
            async with AsyncSessionLocal() as db:
                # 查询会话
                stmt = select(Conversation).where(Conversation.id == conversation_id)
                result = await db.execute(stmt)
                conversation = result.scalar_one_or_none()
                
                if not conversation:
                    raise ValueError(f"Conversation {conversation_id} not found")
                
                # 删除会话(会自动级联删除相关消息)
                await db.delete(conversation)
                await db.commit()
                
                logger.info(f"已删除会话 {conversation_id} 及其所有消息")
        except Exception as e:
            logger.error(f"删除会话失败: {str(e)}", exc_info=True)
            raise

    @staticmethod
    async def update_conversation_name(conversation_id: int, name: str):
        """更新会话名称"""
        try:
            async with AsyncSessionLocal() as db:
                # 查询会话
                stmt = select(Conversation).where(Conversation.id == conversation_id)
                result = await db.execute(stmt)
                conversation = result.scalar_one_or_none()
                
                if not conversation:
                    raise ValueError(f"Conversation {conversation_id} not found")
                
                # 更新名称
                conversation.title = name
                await db.commit()
                
                logger.info(f"已更新会话 {conversation_id} 的名称为 {name}")
        except Exception as e:
            logger.error(f"更新会话名称失败: {str(e)}", exc_info=True)
            raise 