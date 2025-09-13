#!/usr/bin/env python3
"""
技能评估服务层
处理技能评估相关的业务逻辑
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
import statistics
import json

from ..models.skill_assessment import SkillAssessment
from ..models.user import User
from ..models.coding_session import CodingSession
from ..models.code_record import CodeRecord
from ..schemas.skill_assessment import SkillAssessmentCreate, SkillAssessmentUpdate
from ..core.exceptions import SkillAssessmentNotFoundError, InvalidOperationError
from ..core.logger import get_logger

logger = get_logger(__name__)


class SkillAssessmentService:
    """技能评估服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_skill_assessments(self, skip: int = 0, limit: int = 100,
                            user_id: Optional[int] = None,
                            skill_type: Optional[str] = None) -> List[SkillAssessment]:
        """获取技能评估列表"""
        query = self.db.query(SkillAssessment)
        
        if user_id:
            query = query.filter(SkillAssessment.user_id == user_id)
        
        if skill_type:
            query = query.filter(SkillAssessment.skill_type == skill_type)
        
        return query.order_by(desc(SkillAssessment.created_at)).offset(skip).limit(limit).all()
    
    def get_skill_assessment_by_id(self, assessment_id: int) -> SkillAssessment:
        """根据ID获取技能评估"""
        assessment = self.db.query(SkillAssessment).filter(
            SkillAssessment.id == assessment_id
        ).first()
        if not assessment:
            raise SkillAssessmentNotFoundError(f"Skill assessment with id {assessment_id} not found")
        return assessment
    
    def create_skill_assessment(self, assessment_data: SkillAssessmentCreate) -> SkillAssessment:
        """创建技能评估"""
        # 验证用户存在
        user = self.db.query(User).filter(User.id == assessment_data.user_id).first()
        if not user:
            raise InvalidOperationError(f"User with id {assessment_data.user_id} not found")
        
        # 创建评估
        db_assessment = SkillAssessment(
            user_id=assessment_data.user_id,
            skill_type=assessment_data.skill_type,
            score=assessment_data.score,
            max_score=assessment_data.max_score,
            details=assessment_data.details or {},
            strengths=assessment_data.strengths or [],
            weaknesses=assessment_data.weaknesses or [],
            recommendations=assessment_data.recommendations or [],
            metadata=assessment_data.metadata or {}
        )
        
        self.db.add(db_assessment)
        self.db.commit()
        self.db.refresh(db_assessment)
        
        logger.info(f"Created skill assessment: {db_assessment.skill_type} for user {db_assessment.user_id}")
        return db_assessment
    
    def update_skill_assessment(self, assessment_id: int, 
                              assessment_data: SkillAssessmentUpdate) -> SkillAssessment:
        """更新技能评估"""
        assessment = self.get_skill_assessment_by_id(assessment_id)
        
        # 更新字段
        update_data = assessment_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(assessment, field, value)
        
        assessment.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(assessment)
        
        logger.info(f"Updated skill assessment: {assessment.skill_type} (ID: {assessment.id})")
        return assessment
    
    def delete_skill_assessment(self, assessment_id: int) -> bool:
        """删除技能评估"""
        assessment = self.get_skill_assessment_by_id(assessment_id)
        
        self.db.delete(assessment)
        self.db.commit()
        
        logger.info(f"Deleted skill assessment: {assessment.skill_type} (ID: {assessment.id})")
        return True
    
    def analyze_user_skills(self, user_id: int) -> Dict[str, Any]:
        """分析用户技能"""
        # 获取用户所有技能评估
        assessments = self.get_skill_assessments(user_id=user_id, limit=1000)
        
        if not assessments:
            return {
                'user_id': user_id,
                'total_assessments': 0,
                'skill_summary': {},
                'overall_score': 0,
                'skill_distribution': {},
                'improvement_areas': [],
                'strengths': []
            }
        
        # 按技能类型分组
        skills_by_type = {}
        for assessment in assessments:
            skill_type = assessment.skill_type
            if skill_type not in skills_by_type:
                skills_by_type[skill_type] = []
            skills_by_type[skill_type].append(assessment)
        
        # 计算每种技能的最新分数和趋势
        skill_summary = {}
        all_scores = []
        
        for skill_type, skill_assessments in skills_by_type.items():
            # 按时间排序
            skill_assessments.sort(key=lambda x: x.created_at)
            latest = skill_assessments[-1]
            
            # 计算趋势
            scores = [a.score for a in skill_assessments]
            trend = 'stable'
            if len(scores) > 1:
                if scores[-1] > scores[-2]:
                    trend = 'improving'
                elif scores[-1] < scores[-2]:
                    trend = 'declining'
            
            skill_summary[skill_type] = {
                'current_score': latest.score,
                'max_score': latest.max_score,
                'percentage': round((latest.score / latest.max_score) * 100, 2),
                'trend': trend,
                'assessment_count': len(skill_assessments),
                'last_assessed': latest.created_at.isoformat(),
                'strengths': latest.strengths,
                'weaknesses': latest.weaknesses,
                'recommendations': latest.recommendations
            }
            
            all_scores.append(latest.score / latest.max_score * 100)
        
        # 计算总体分数
        overall_score = round(statistics.mean(all_scores), 2) if all_scores else 0
        
        # 技能分布
        skill_levels = {'beginner': 0, 'intermediate': 0, 'advanced': 0, 'expert': 0}
        for score in all_scores:
            if score < 25:
                skill_levels['beginner'] += 1
            elif score < 50:
                skill_levels['intermediate'] += 1
            elif score < 75:
                skill_levels['advanced'] += 1
            else:
                skill_levels['expert'] += 1
        
        # 需要改进的领域（分数低于60%的技能）
        improvement_areas = [
            {'skill': skill, 'score': data['percentage'], 'recommendations': data['recommendations']}
            for skill, data in skill_summary.items()
            if data['percentage'] < 60
        ]
        improvement_areas.sort(key=lambda x: x['score'])
        
        # 优势领域（分数高于80%的技能）
        strengths = [
            {'skill': skill, 'score': data['percentage'], 'strengths': data['strengths']}
            for skill, data in skill_summary.items()
            if data['percentage'] >= 80
        ]
        strengths.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'user_id': user_id,
            'total_assessments': len(assessments),
            'skill_summary': skill_summary,
            'overall_score': overall_score,
            'skill_distribution': skill_levels,
            'improvement_areas': improvement_areas[:5],  # 最需要改进的5个领域
            'strengths': strengths[:5]  # 最强的5个领域
        }
    
    def get_skill_radar_data(self, user_id: int, skill_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """获取技能雷达图数据"""
        query = self.db.query(SkillAssessment).filter(SkillAssessment.user_id == user_id)
        
        if skill_types:
            query = query.filter(SkillAssessment.skill_type.in_(skill_types))
        
        # 获取每种技能的最新评估
        latest_assessments = {}
        assessments = query.all()
        
        for assessment in assessments:
            skill_type = assessment.skill_type
            if (skill_type not in latest_assessments or 
                assessment.created_at > latest_assessments[skill_type].created_at):
                latest_assessments[skill_type] = assessment
        
        # 构建雷达图数据
        radar_data = {
            'labels': [],
            'datasets': [{
                'label': 'Current Skills',
                'data': [],
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'pointBackgroundColor': 'rgba(54, 162, 235, 1)'
            }]
        }
        
        for skill_type, assessment in latest_assessments.items():
            radar_data['labels'].append(skill_type)
            percentage = (assessment.score / assessment.max_score) * 100
            radar_data['datasets'][0]['data'].append(round(percentage, 2))
        
        return radar_data
    
    def get_skill_progress_trend(self, user_id: int, skill_type: str, days: int = 90) -> Dict[str, Any]:
        """获取技能进步趋势"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        assessments = (self.db.query(SkillAssessment)
                      .filter(
                          and_(
                              SkillAssessment.user_id == user_id,
                              SkillAssessment.skill_type == skill_type,
                              SkillAssessment.created_at >= start_date
                          )
                      )
                      .order_by(SkillAssessment.created_at)
                      .all())
        
        if not assessments:
            return {
                'skill_type': skill_type,
                'period_days': days,
                'data_points': [],
                'trend': 'no_data',
                'improvement': 0,
                'average_score': 0
            }
        
        # 构建趋势数据
        data_points = []
        scores = []
        
        for assessment in assessments:
            percentage = (assessment.score / assessment.max_score) * 100
            data_points.append({
                'date': assessment.created_at.isoformat(),
                'score': assessment.score,
                'max_score': assessment.max_score,
                'percentage': round(percentage, 2)
            })
            scores.append(percentage)
        
        # 计算趋势
        trend = 'stable'
        improvement = 0
        
        if len(scores) > 1:
            first_score = scores[0]
            last_score = scores[-1]
            improvement = round(last_score - first_score, 2)
            
            if improvement > 5:
                trend = 'improving'
            elif improvement < -5:
                trend = 'declining'
        
        average_score = round(statistics.mean(scores), 2)
        
        return {
            'skill_type': skill_type,
            'period_days': days,
            'data_points': data_points,
            'trend': trend,
            'improvement': improvement,
            'average_score': average_score,
            'total_assessments': len(assessments)
        }
    
    def get_skill_recommendations(self, user_id: int) -> Dict[str, Any]:
        """获取技能提升建议"""
        analysis = self.analyze_user_skills(user_id)
        
        recommendations = {
            'priority_skills': [],
            'learning_paths': [],
            'practice_suggestions': [],
            'resource_recommendations': []
        }
        
        # 优先技能（需要改进的领域）
        for area in analysis['improvement_areas']:
            recommendations['priority_skills'].append({
                'skill': area['skill'],
                'current_score': area['score'],
                'target_score': min(area['score'] + 20, 100),
                'urgency': 'high' if area['score'] < 40 else 'medium',
                'specific_recommendations': area['recommendations']
            })
        
        # 学习路径建议
        skill_summary = analysis['skill_summary']
        
        # 基础技能路径
        if any(data['percentage'] < 50 for data in skill_summary.values()):
            recommendations['learning_paths'].append({
                'path': 'Foundation Building',
                'description': 'Focus on strengthening fundamental programming concepts',
                'duration': '2-3 months',
                'skills': [skill for skill, data in skill_summary.items() if data['percentage'] < 50]
            })
        
        # 进阶技能路径
        intermediate_skills = [skill for skill, data in skill_summary.items() 
                             if 50 <= data['percentage'] < 75]
        if intermediate_skills:
            recommendations['learning_paths'].append({
                'path': 'Intermediate Development',
                'description': 'Advance your existing skills to the next level',
                'duration': '3-4 months',
                'skills': intermediate_skills
            })
        
        # 专业化路径
        advanced_skills = [skill for skill, data in skill_summary.items() 
                         if data['percentage'] >= 75]
        if advanced_skills:
            recommendations['learning_paths'].append({
                'path': 'Specialization',
                'description': 'Deepen expertise in your strongest areas',
                'duration': '4-6 months',
                'skills': advanced_skills
            })
        
        # 实践建议
        recommendations['practice_suggestions'] = [
            {
                'type': 'coding_challenges',
                'description': 'Solve daily coding problems to improve problem-solving skills',
                'frequency': 'daily',
                'duration': '30-60 minutes'
            },
            {
                'type': 'project_based',
                'description': 'Build real-world projects to apply learned concepts',
                'frequency': 'weekly',
                'duration': '2-4 hours'
            },
            {
                'type': 'code_review',
                'description': 'Participate in code reviews to learn best practices',
                'frequency': 'weekly',
                'duration': '1-2 hours'
            }
        ]
        
        # 资源推荐
        recommendations['resource_recommendations'] = [
            {
                'type': 'documentation',
                'title': 'Official Language Documentation',
                'description': 'Read official docs for languages you\'re learning'
            },
            {
                'type': 'online_courses',
                'title': 'Structured Learning Platforms',
                'description': 'Use platforms like Coursera, Udemy, or edX for structured learning'
            },
            {
                'type': 'books',
                'title': 'Technical Books',
                'description': 'Read books on software engineering best practices'
            },
            {
                'type': 'community',
                'title': 'Developer Communities',
                'description': 'Join communities like Stack Overflow, GitHub, or Reddit'
            }
        ]
        
        return recommendations
    
    def auto_assess_from_coding_session(self, session_id: int) -> SkillAssessment:
        """基于编程会话自动评估技能"""
        # 获取编程会话
        session = self.db.query(CodingSession).filter(CodingSession.id == session_id).first()
        if not session:
            raise InvalidOperationError(f"Coding session with id {session_id} not found")
        
        # 获取代码记录
        code_records = (self.db.query(CodeRecord)
                       .filter(CodeRecord.session_id == session_id)
                       .all())
        
        # 分析代码质量和复杂度
        total_lines = sum(record.line_count for record in code_records)
        languages_used = set(record.language for record in code_records if record.language)
        
        # 基础评分逻辑（这里可以集成更复杂的代码分析工具）
        base_score = 50  # 基础分数
        
        # 根据代码量调整分数
        if total_lines > 100:
            base_score += 10
        elif total_lines > 50:
            base_score += 5
        
        # 根据语言多样性调整分数
        if len(languages_used) > 1:
            base_score += 5
        
        # 根据会话时长调整分数
        if session.total_duration and session.total_duration > 3600:  # 超过1小时
            base_score += 10
        
        # 限制分数范围
        score = min(max(base_score, 0), 100)
        
        # 创建技能评估
        assessment_data = SkillAssessmentCreate(
            user_id=session.user_id,
            skill_type=session.language or 'general_programming',
            score=score,
            max_score=100,
            details={
                'session_id': session_id,
                'total_lines': total_lines,
                'languages_used': list(languages_used),
                'session_duration': session.total_duration,
                'auto_generated': True
            },
            metadata={
                'assessment_method': 'auto_from_session',
                'session_title': session.title
            }
        )
        
        assessment = self.create_skill_assessment(assessment_data)
        
        logger.info(f"Auto-generated skill assessment from session {session_id}: score {score}")
        return assessment