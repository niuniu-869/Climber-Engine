#!/usr/bin/env python3
"""
用户服务层
处理用户相关的业务逻辑
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from ..models.user import User
from ..models.coding_session import CodingSession
from ..models.skill_assessment import SkillAssessment
from ..models.learning_task import LearningTask
from ..models.technical_debt import TechnicalDebt
from ..schemas.user import UserCreate, UserUpdate
from ..core.exceptions import UserNotFoundError, UserAlreadyExistsError
from ..core.security import get_password_hash, verify_password
from ..core.logger import get_logger

logger = get_logger(__name__)


class UserService:
    """用户服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_users(self, skip: int = 0, limit: int = 100, 
                  search: Optional[str] = None,
                  is_active: Optional[bool] = None) -> List[User]:
        """获取用户列表"""
        query = self.db.query(User)
        
        # 搜索过滤
        if search:
            search_filter = or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # 状态过滤
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()
    
    def get_user_count(self, search: Optional[str] = None,
                      is_active: Optional[bool] = None) -> int:
        """获取用户总数"""
        query = self.db.query(func.count(User.id))
        
        if search:
            search_filter = or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        return query.scalar()
    
    def get_user_by_id(self, user_id: int) -> User:
        """根据ID获取用户"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        return user
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.db.query(User).filter(User.email == email).first()
    
    def create_user(self, user_data: UserCreate) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        if self.get_user_by_username(user_data.username):
            raise UserAlreadyExistsError(f"Username {user_data.username} already exists")
        
        # 检查邮箱是否已存在
        if self.get_user_by_email(user_data.email):
            raise UserAlreadyExistsError(f"Email {user_data.email} already exists")
        
        # 创建用户
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            role=user_data.role,
            is_active=user_data.is_active,
            preferences=user_data.preferences or {},
            metadata=user_data.metadata or {}
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        logger.info(f"Created user: {db_user.username} (ID: {db_user.id})")
        return db_user
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """更新用户"""
        user = self.get_user_by_id(user_id)
        
        # 检查用户名冲突
        if user_data.username and user_data.username != user.username:
            existing_user = self.get_user_by_username(user_data.username)
            if existing_user:
                raise UserAlreadyExistsError(f"Username {user_data.username} already exists")
        
        # 检查邮箱冲突
        if user_data.email and user_data.email != user.email:
            existing_user = self.get_user_by_email(user_data.email)
            if existing_user:
                raise UserAlreadyExistsError(f"Email {user_data.email} already exists")
        
        # 更新字段
        update_data = user_data.dict(exclude_unset=True)
        if 'password' in update_data:
            update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"Updated user: {user.username} (ID: {user.id})")
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户（软删除）"""
        user = self.get_user_by_id(user_id)
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        logger.info(f"Deactivated user: {user.username} (ID: {user.id})")
        return True
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """用户认证"""
        user = self.get_user_by_username(username)
        if not user or not user.is_active:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        self.db.commit()
        
        return user
    
    def get_user_coding_sessions(self, user_id: int, 
                               skip: int = 0, limit: int = 100,
                               status: Optional[str] = None) -> List[CodingSession]:
        """获取用户的编程会话"""
        query = self.db.query(CodingSession).filter(CodingSession.user_id == user_id)
        
        if status:
            query = query.filter(CodingSession.status == status)
        
        return query.order_by(desc(CodingSession.created_at)).offset(skip).limit(limit).all()
    
    def get_user_skill_assessments(self, user_id: int,
                                 skip: int = 0, limit: int = 100) -> List[SkillAssessment]:
        """获取用户的技能评估"""
        return (self.db.query(SkillAssessment)
                .filter(SkillAssessment.user_id == user_id)
                .order_by(desc(SkillAssessment.created_at))
                .offset(skip).limit(limit).all())
    
    def get_user_learning_tasks(self, user_id: int,
                              skip: int = 0, limit: int = 100,
                              status: Optional[str] = None) -> List[LearningTask]:
        """获取用户的学习任务"""
        query = self.db.query(LearningTask).filter(LearningTask.user_id == user_id)
        
        if status:
            query = query.filter(LearningTask.status == status)
        
        return query.order_by(desc(LearningTask.created_at)).offset(skip).limit(limit).all()
    
    def get_user_technical_debts(self, user_id: int,
                               skip: int = 0, limit: int = 100,
                               status: Optional[str] = None) -> List[TechnicalDebt]:
        """获取用户的技术债务"""
        query = self.db.query(TechnicalDebt).filter(TechnicalDebt.user_id == user_id)
        
        if status:
            query = query.filter(TechnicalDebt.status == status)
        
        return query.order_by(desc(TechnicalDebt.created_at)).offset(skip).limit(limit).all()
    
    def get_user_dashboard_data(self, user_id: int) -> Dict[str, Any]:
        """获取用户仪表板数据"""
        user = self.get_user_by_id(user_id)
        
        # 统计数据
        total_sessions = self.db.query(func.count(CodingSession.id)).filter(
            CodingSession.user_id == user_id
        ).scalar()
        
        active_sessions = self.db.query(func.count(CodingSession.id)).filter(
            and_(
                CodingSession.user_id == user_id,
                CodingSession.status == 'active'
            )
        ).scalar()
        
        total_assessments = self.db.query(func.count(SkillAssessment.id)).filter(
            SkillAssessment.user_id == user_id
        ).scalar()
        
        pending_tasks = self.db.query(func.count(LearningTask.id)).filter(
            and_(
                LearningTask.user_id == user_id,
                LearningTask.status == 'pending'
            )
        ).scalar()
        
        open_debts = self.db.query(func.count(TechnicalDebt.id)).filter(
            and_(
                TechnicalDebt.user_id == user_id,
                TechnicalDebt.status == 'open'
            )
        ).scalar()
        
        # 最近活动
        recent_sessions = self.get_user_coding_sessions(user_id, limit=5)
        recent_assessments = self.get_user_skill_assessments(user_id, limit=3)
        recent_tasks = self.get_user_learning_tasks(user_id, limit=5)
        
        # 技能趋势（最近30天）
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_skill_scores = (self.db.query(SkillAssessment.score, SkillAssessment.created_at)
                             .filter(
                                 and_(
                                     SkillAssessment.user_id == user_id,
                                     SkillAssessment.created_at >= thirty_days_ago
                                 )
                             )
                             .order_by(SkillAssessment.created_at)
                             .all())
        
        return {
            "user_info": {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role,
                "last_login_at": user.last_login_at,
                "created_at": user.created_at
            },
            "statistics": {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "total_assessments": total_assessments,
                "pending_tasks": pending_tasks,
                "open_debts": open_debts
            },
            "recent_activity": {
                "sessions": [{
                    "id": s.id,
                    "title": s.title,
                    "status": s.status,
                    "created_at": s.created_at
                } for s in recent_sessions],
                "assessments": [{
                    "id": a.id,
                    "skill_type": a.skill_type,
                    "score": a.score,
                    "created_at": a.created_at
                } for a in recent_assessments],
                "tasks": [{
                    "id": t.id,
                    "title": t.title,
                    "status": t.status,
                    "priority": t.priority,
                    "created_at": t.created_at
                } for t in recent_tasks]
            },
            "skill_trend": {
                "scores": [{
                    "score": score,
                    "date": created_at.isoformat()
                } for score, created_at in recent_skill_scores]
            }
        }
    
    def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> User:
        """更新用户偏好设置"""
        user = self.get_user_by_id(user_id)
        user.preferences = {**(user.preferences or {}), **preferences}
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"Updated preferences for user: {user.username} (ID: {user.id})")
        return user
    
    def get_user_activity_summary(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """获取用户活动摘要"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 编程会话活动
        session_activity = (self.db.query(
                func.date(CodingSession.created_at).label('date'),
                func.count(CodingSession.id).label('count')
            )
            .filter(
                and_(
                    CodingSession.user_id == user_id,
                    CodingSession.created_at >= start_date
                )
            )
            .group_by(func.date(CodingSession.created_at))
            .all())
        
        # 学习任务完成情况
        task_completion = (self.db.query(
                func.date(LearningTask.completed_at).label('date'),
                func.count(LearningTask.id).label('count')
            )
            .filter(
                and_(
                    LearningTask.user_id == user_id,
                    LearningTask.status == 'completed',
                    LearningTask.completed_at >= start_date
                )
            )
            .group_by(func.date(LearningTask.completed_at))
            .all())
        
        return {
            "period_days": days,
            "session_activity": [{
                "date": date.isoformat(),
                "sessions": count
            } for date, count in session_activity],
            "task_completion": [{
                "date": date.isoformat(),
                "completed_tasks": count
            } for date, count in task_completion]
        }