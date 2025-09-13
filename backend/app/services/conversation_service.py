#!/usr/bin/env python3
"""
对话业务逻辑服务
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import uuid4

from app.models.conversation import Conversation, Message
from app.schemas.conversation import ConversationCreate, MessageCreate


class ConversationService:
    """对话服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_conversations(
        self, 
        skip: int = 0, 
        limit: int = 100,
        agent_id: Optional[int] = None
    ) -> List[Conversation]:
        """获取对话列表"""
        query = self.db.query(Conversation)
        
        if agent_id:
            query = query.filter(Conversation.agent_id == agent_id)
        
        return query.offset(skip).limit(limit).all()
    
    def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """获取指定对话"""
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    def create_conversation(self, conversation_data: ConversationCreate) -> Conversation:
        """创建新对话"""
        session_id = conversation_data.session_id or str(uuid4())
        
        conversation = Conversation(
            title=conversation_data.title,
            session_id=session_id,
            agent_id=conversation_data.agent_id,
            metadata=conversation_data.metadata
        )
        
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        return conversation
    
    def delete_conversation(self, conversation_id: int) -> bool:
        """删除对话"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        self.db.delete(conversation)
        self.db.commit()
        
        return True
    
    def get_messages(
        self, 
        conversation_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Message]:
        """获取对话消息"""
        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).offset(skip).limit(limit).all()
    
    def add_message(self, conversation_id: int, message_data: MessageCreate) -> Message:
        """添加消息到对话"""
        message = Message(
            conversation_id=conversation_id,
            role=message_data.role,
            content=message_data.content,
            metadata=message_data.metadata
        )
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    async def get_agent_response(self, conversation_id: int, user_input: str) -> Message:
        """获取 Agent 响应"""
        # TODO: 实现 AI 模型调用逻辑
        response_content = f"收到消息: {user_input}"
        
        response_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=response_content,
            metadata={"model": "placeholder"}
        )
        
        self.db.add(response_message)
        self.db.commit()
        self.db.refresh(response_message)
        
        return response_message