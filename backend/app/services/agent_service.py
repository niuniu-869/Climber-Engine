#!/usr/bin/env python3
"""
Agent 业务逻辑服务
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate


class AgentService:
    """Agent 服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_agents(
        self, 
        skip: int = 0, 
        limit: int = 100,
        agent_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Agent]:
        """获取 Agent 列表"""
        query = self.db.query(Agent)
        
        if agent_type:
            query = query.filter(Agent.type == agent_type)
        
        if is_active is not None:
            query = query.filter(Agent.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()
    
    def get_agent(self, agent_id: int) -> Optional[Agent]:
        """获取指定 Agent"""
        return self.db.query(Agent).filter(Agent.id == agent_id).first()
    
    def get_agent_by_name(self, name: str) -> Optional[Agent]:
        """根据名称获取 Agent"""
        return self.db.query(Agent).filter(Agent.name == name).first()
    
    def create_agent(self, agent_data: AgentCreate) -> Agent:
        """创建新的 Agent"""
        agent = Agent(
            name=agent_data.name,
            description=agent_data.description,
            type=agent_data.type,
            config=agent_data.config,
            prompt_template=agent_data.prompt_template,
            version=agent_data.version
        )
        
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        
        return agent
    
    def update_agent(self, agent_id: int, agent_data: AgentUpdate) -> Optional[Agent]:
        """更新 Agent"""
        agent = self.get_agent(agent_id)
        if not agent:
            return None
        
        update_data = agent_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
        
        self.db.commit()
        self.db.refresh(agent)
        
        return agent
    
    def delete_agent(self, agent_id: int) -> bool:
        """删除 Agent"""
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        
        self.db.delete(agent)
        self.db.commit()
        
        return True
    
    def activate_agent(self, agent_id: int) -> bool:
        """激活 Agent"""
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        
        agent.is_active = True
        self.db.commit()
        
        return True
    
    def deactivate_agent(self, agent_id: int) -> bool:
        """停用 Agent"""
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        
        agent.is_active = False
        self.db.commit()
        
        return True
    
    def get_active_agents(self) -> List[Agent]:
        """获取所有活跃的 Agent"""
        return self.db.query(Agent).filter(Agent.is_active == True).all()
    
    def get_agents_by_type(self, agent_type: str) -> List[Agent]:
        """根据类型获取 Agent"""
        return self.db.query(Agent).filter(
            and_(Agent.type == agent_type, Agent.is_active == True)
        ).all()