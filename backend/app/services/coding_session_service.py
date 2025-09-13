#!/usr/bin/env python3
"""
编程会话服务层
处理编程会话相关的业务逻辑
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from ..models.coding_session import CodingSession
from ..models.code_record import CodeRecord
from ..models.user import User
from ..schemas.coding_session import CodingSessionCreate, CodingSessionUpdate
from ..core.exceptions import CodingSessionNotFoundError, InvalidOperationError
from ..core.logger import get_logger

logger = get_logger(__name__)


class CodingSessionService:
    """编程会话服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_coding_sessions(self, skip: int = 0, limit: int = 100,
                          user_id: Optional[int] = None,
                          status: Optional[str] = None,
                          search: Optional[str] = None) -> List[CodingSession]:
        """获取编程会话列表"""
        query = self.db.query(CodingSession)
        
        # 用户过滤
        if user_id:
            query = query.filter(CodingSession.user_id == user_id)
        
        # 状态过滤
        if status:
            query = query.filter(CodingSession.status == status)
        
        # 搜索过滤
        if search:
            search_filter = or_(
                CodingSession.title.ilike(f"%{search}%"),
                CodingSession.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        return query.order_by(desc(CodingSession.created_at)).offset(skip).limit(limit).all()
    
    def get_coding_session_count(self, user_id: Optional[int] = None,
                               status: Optional[str] = None,
                               search: Optional[str] = None) -> int:
        """获取编程会话总数"""
        query = self.db.query(func.count(CodingSession.id))
        
        if user_id:
            query = query.filter(CodingSession.user_id == user_id)
        
        if status:
            query = query.filter(CodingSession.status == status)
        
        if search:
            search_filter = or_(
                CodingSession.title.ilike(f"%{search}%"),
                CodingSession.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        return query.scalar()
    
    def get_coding_session_by_id(self, session_id: int) -> CodingSession:
        """根据ID获取编程会话"""
        session = self.db.query(CodingSession).filter(CodingSession.id == session_id).first()
        if not session:
            raise CodingSessionNotFoundError(f"Coding session with id {session_id} not found")
        return session
    
    def create_coding_session(self, session_data: CodingSessionCreate) -> CodingSession:
        """创建编程会话"""
        # 验证用户存在
        user = self.db.query(User).filter(User.id == session_data.user_id).first()
        if not user:
            raise InvalidOperationError(f"User with id {session_data.user_id} not found")
        
        # 创建会话
        db_session = CodingSession(
            user_id=session_data.user_id,
            title=session_data.title,
            description=session_data.description,
            language=session_data.language,
            framework=session_data.framework,
            project_type=session_data.project_type,
            difficulty_level=session_data.difficulty_level,
            goals=session_data.goals or [],
            status='pending',
            metadata=session_data.metadata or {}
        )
        
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        
        logger.info(f"Created coding session: {db_session.title} (ID: {db_session.id})")
        return db_session
    
    def update_coding_session(self, session_id: int, session_data: CodingSessionUpdate) -> CodingSession:
        """更新编程会话"""
        session = self.get_coding_session_by_id(session_id)
        
        # 更新字段
        update_data = session_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(session, field, value)
        
        session.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(session)
        
        logger.info(f"Updated coding session: {session.title} (ID: {session.id})")
        return session
    
    def delete_coding_session(self, session_id: int) -> bool:
        """删除编程会话"""
        session = self.get_coding_session_by_id(session_id)
        
        # 检查是否可以删除（只能删除未开始或已结束的会话）
        if session.status in ['active', 'paused']:
            raise InvalidOperationError("Cannot delete active or paused coding session")
        
        self.db.delete(session)
        self.db.commit()
        
        logger.info(f"Deleted coding session: {session.title} (ID: {session.id})")
        return True
    
    def start_coding_session(self, session_id: int) -> CodingSession:
        """开始编程会话"""
        session = self.get_coding_session_by_id(session_id)
        
        if session.status != 'pending':
            raise InvalidOperationError(f"Cannot start session with status: {session.status}")
        
        session.status = 'active'
        session.started_at = datetime.utcnow()
        session.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(session)
        
        logger.info(f"Started coding session: {session.title} (ID: {session.id})")
        return session
    
    def pause_coding_session(self, session_id: int) -> CodingSession:
        """暂停编程会话"""
        session = self.get_coding_session_by_id(session_id)
        
        if session.status != 'active':
            raise InvalidOperationError(f"Cannot pause session with status: {session.status}")
        
        session.status = 'paused'
        session.updated_at = datetime.utcnow()
        
        # 更新总时长
        if session.started_at:
            if not session.total_duration:
                session.total_duration = 0
            session.total_duration += int((datetime.utcnow() - session.started_at).total_seconds())
        
        self.db.commit()
        self.db.refresh(session)
        
        logger.info(f"Paused coding session: {session.title} (ID: {session.id})")
        return session
    
    def resume_coding_session(self, session_id: int) -> CodingSession:
        """恢复编程会话"""
        session = self.get_coding_session_by_id(session_id)
        
        if session.status != 'paused':
            raise InvalidOperationError(f"Cannot resume session with status: {session.status}")
        
        session.status = 'active'
        session.started_at = datetime.utcnow()  # 重新设置开始时间
        session.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(session)
        
        logger.info(f"Resumed coding session: {session.title} (ID: {session.id})")
        return session
    
    def end_coding_session(self, session_id: int, summary: Optional[str] = None) -> CodingSession:
        """结束编程会话"""
        session = self.get_coding_session_by_id(session_id)
        
        if session.status not in ['active', 'paused']:
            raise InvalidOperationError(f"Cannot end session with status: {session.status}")
        
        session.status = 'completed'
        session.ended_at = datetime.utcnow()
        session.updated_at = datetime.utcnow()
        
        if summary:
            session.summary = summary
        
        # 计算总时长
        if session.started_at:
            if not session.total_duration:
                session.total_duration = 0
            if session.status == 'active':
                session.total_duration += int((datetime.utcnow() - session.started_at).total_seconds())
        
        self.db.commit()
        self.db.refresh(session)
        
        logger.info(f"Ended coding session: {session.title} (ID: {session.id})")
        return session
    
    def get_session_code_records(self, session_id: int,
                               skip: int = 0, limit: int = 100) -> List[CodeRecord]:
        """获取会话的代码记录"""
        return (self.db.query(CodeRecord)
                .filter(CodeRecord.session_id == session_id)
                .order_by(desc(CodeRecord.created_at))
                .offset(skip).limit(limit).all())
    
    def add_code_record(self, session_id: int, code_data: Dict[str, Any]) -> CodeRecord:
        """添加代码记录"""
        session = self.get_coding_session_by_id(session_id)
        
        if session.status not in ['active', 'paused']:
            raise InvalidOperationError("Cannot add code record to inactive session")
        
        code_record = CodeRecord(
            session_id=session_id,
            file_path=code_data.get('file_path'),
            content=code_data.get('content'),
            language=code_data.get('language'),
            operation_type=code_data.get('operation_type', 'edit'),
            line_count=code_data.get('line_count', 0),
            char_count=len(code_data.get('content', '')),
            metadata=code_data.get('metadata', {})
        )
        
        self.db.add(code_record)
        
        # 更新会话统计
        session.lines_of_code = (session.lines_of_code or 0) + code_record.line_count
        session.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(code_record)
        
        return code_record
    
    def get_session_analysis(self, session_id: int) -> Dict[str, Any]:
        """获取会话分析报告"""
        session = self.get_coding_session_by_id(session_id)
        code_records = self.get_session_code_records(session_id)
        
        # 基础统计
        total_records = len(code_records)
        total_lines = sum(record.line_count for record in code_records)
        total_chars = sum(record.char_count for record in code_records)
        
        # 语言分布
        language_stats = {}
        for record in code_records:
            lang = record.language or 'unknown'
            if lang not in language_stats:
                language_stats[lang] = {'count': 0, 'lines': 0}
            language_stats[lang]['count'] += 1
            language_stats[lang]['lines'] += record.line_count
        
        # 操作类型分布
        operation_stats = {}
        for record in code_records:
            op_type = record.operation_type or 'unknown'
            operation_stats[op_type] = operation_stats.get(op_type, 0) + 1
        
        # 时间分析
        duration_minutes = 0
        if session.total_duration:
            duration_minutes = session.total_duration / 60
        
        productivity_score = 0
        if duration_minutes > 0:
            productivity_score = total_lines / duration_minutes
        
        # 活动时间线
        timeline = []
        for record in code_records[-20:]:  # 最近20条记录
            timeline.append({
                'timestamp': record.created_at.isoformat(),
                'file_path': record.file_path,
                'operation': record.operation_type,
                'lines': record.line_count
            })
        
        return {
            'session_info': {
                'id': session.id,
                'title': session.title,
                'status': session.status,
                'duration_seconds': session.total_duration or 0,
                'duration_minutes': round(duration_minutes, 2),
                'started_at': session.started_at.isoformat() if session.started_at else None,
                'ended_at': session.ended_at.isoformat() if session.ended_at else None
            },
            'code_statistics': {
                'total_records': total_records,
                'total_lines': total_lines,
                'total_characters': total_chars,
                'productivity_score': round(productivity_score, 2)
            },
            'language_distribution': language_stats,
            'operation_distribution': operation_stats,
            'activity_timeline': timeline
        }
    
    def get_user_session_statistics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """获取用户会话统计"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 基础统计
        total_sessions = self.db.query(func.count(CodingSession.id)).filter(
            and_(
                CodingSession.user_id == user_id,
                CodingSession.created_at >= start_date
            )
        ).scalar()
        
        completed_sessions = self.db.query(func.count(CodingSession.id)).filter(
            and_(
                CodingSession.user_id == user_id,
                CodingSession.status == 'completed',
                CodingSession.created_at >= start_date
            )
        ).scalar()
        
        # 总编程时间
        total_duration = self.db.query(func.sum(CodingSession.total_duration)).filter(
            and_(
                CodingSession.user_id == user_id,
                CodingSession.created_at >= start_date
            )
        ).scalar() or 0
        
        # 总代码行数
        total_lines = self.db.query(func.sum(CodingSession.lines_of_code)).filter(
            and_(
                CodingSession.user_id == user_id,
                CodingSession.created_at >= start_date
            )
        ).scalar() or 0
        
        # 语言使用统计
        language_usage = (self.db.query(
                CodingSession.language,
                func.count(CodingSession.id).label('count'),
                func.sum(CodingSession.total_duration).label('duration')
            )
            .filter(
                and_(
                    CodingSession.user_id == user_id,
                    CodingSession.created_at >= start_date
                )
            )
            .group_by(CodingSession.language)
            .all())
        
        # 每日活动
        daily_activity = (self.db.query(
                func.date(CodingSession.created_at).label('date'),
                func.count(CodingSession.id).label('sessions'),
                func.sum(CodingSession.total_duration).label('duration')
            )
            .filter(
                and_(
                    CodingSession.user_id == user_id,
                    CodingSession.created_at >= start_date
                )
            )
            .group_by(func.date(CodingSession.created_at))
            .all())
        
        return {
            'period_days': days,
            'summary': {
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'completion_rate': round(completed_sessions / total_sessions * 100, 2) if total_sessions > 0 else 0,
                'total_duration_seconds': total_duration,
                'total_duration_hours': round(total_duration / 3600, 2),
                'total_lines_of_code': total_lines,
                'average_session_duration': round(total_duration / total_sessions, 2) if total_sessions > 0 else 0
            },
            'language_usage': [{
                'language': lang,
                'sessions': count,
                'duration_seconds': duration or 0,
                'duration_hours': round((duration or 0) / 3600, 2)
            } for lang, count, duration in language_usage],
            'daily_activity': [{
                'date': date.isoformat(),
                'sessions': sessions,
                'duration_seconds': duration or 0,
                'duration_hours': round((duration or 0) / 3600, 2)
            } for date, sessions, duration in daily_activity]
        }