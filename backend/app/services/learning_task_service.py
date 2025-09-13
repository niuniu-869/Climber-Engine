#!/usr/bin/env python3
"""
学习任务服务层
处理学习任务相关的业务逻辑
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
import random

from ..models.learning_task import LearningTask
from ..models.user import User
from ..models.skill_assessment import SkillAssessment
from ..schemas.learning_task import LearningTaskCreate, LearningTaskUpdate
from ..core.exceptions import LearningTaskNotFoundError, InvalidOperationError
from ..core.logger import get_logger

logger = get_logger(__name__)


class LearningTaskService:
    """学习任务服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_learning_tasks(self, skip: int = 0, limit: int = 100,
                         user_id: Optional[int] = None,
                         status: Optional[str] = None,
                         priority: Optional[str] = None,
                         skill_type: Optional[str] = None) -> List[LearningTask]:
        """获取学习任务列表"""
        query = self.db.query(LearningTask)
        
        if user_id:
            query = query.filter(LearningTask.user_id == user_id)
        
        if status:
            query = query.filter(LearningTask.status == status)
        
        if priority:
            query = query.filter(LearningTask.priority == priority)
        
        if skill_type:
            query = query.filter(LearningTask.skill_type == skill_type)
        
        return query.order_by(desc(LearningTask.created_at)).offset(skip).limit(limit).all()
    
    def get_learning_task_by_id(self, task_id: int) -> LearningTask:
        """根据ID获取学习任务"""
        task = self.db.query(LearningTask).filter(LearningTask.id == task_id).first()
        if not task:
            raise LearningTaskNotFoundError(f"Learning task with id {task_id} not found")
        return task
    
    def create_learning_task(self, task_data: LearningTaskCreate) -> LearningTask:
        """创建学习任务"""
        # 验证用户存在
        user = self.db.query(User).filter(User.id == task_data.user_id).first()
        if not user:
            raise InvalidOperationError(f"User with id {task_data.user_id} not found")
        
        # 创建任务
        db_task = LearningTask(
            user_id=task_data.user_id,
            title=task_data.title,
            description=task_data.description,
            skill_type=task_data.skill_type,
            difficulty_level=task_data.difficulty_level,
            estimated_duration=task_data.estimated_duration,
            priority=task_data.priority,
            learning_objectives=task_data.learning_objectives or [],
            resources=task_data.resources or [],
            prerequisites=task_data.prerequisites or [],
            success_criteria=task_data.success_criteria or [],
            status='pending',
            metadata=task_data.metadata or {}
        )
        
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        
        logger.info(f"Created learning task: {db_task.title} (ID: {db_task.id})")
        return db_task
    
    def update_learning_task(self, task_id: int, task_data: LearningTaskUpdate) -> LearningTask:
        """更新学习任务"""
        task = self.get_learning_task_by_id(task_id)
        
        # 更新字段
        update_data = task_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        task.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(task)
        
        logger.info(f"Updated learning task: {task.title} (ID: {task.id})")
        return task
    
    def delete_learning_task(self, task_id: int) -> bool:
        """删除学习任务"""
        task = self.get_learning_task_by_id(task_id)
        
        # 检查是否可以删除（只能删除未开始或已完成的任务）
        if task.status in ['in_progress', 'paused']:
            raise InvalidOperationError("Cannot delete active learning task")
        
        self.db.delete(task)
        self.db.commit()
        
        logger.info(f"Deleted learning task: {task.title} (ID: {task.id})")
        return True
    
    def start_learning_task(self, task_id: int) -> LearningTask:
        """开始学习任务"""
        task = self.get_learning_task_by_id(task_id)
        
        if task.status != 'pending':
            raise InvalidOperationError(f"Cannot start task with status: {task.status}")
        
        task.status = 'in_progress'
        task.started_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(task)
        
        logger.info(f"Started learning task: {task.title} (ID: {task.id})")
        return task
    
    def pause_learning_task(self, task_id: int) -> LearningTask:
        """暂停学习任务"""
        task = self.get_learning_task_by_id(task_id)
        
        if task.status != 'in_progress':
            raise InvalidOperationError(f"Cannot pause task with status: {task.status}")
        
        task.status = 'paused'
        task.updated_at = datetime.utcnow()
        
        # 更新实际花费时间
        if task.started_at:
            if not task.actual_duration:
                task.actual_duration = 0
            task.actual_duration += int((datetime.utcnow() - task.started_at).total_seconds())
        
        self.db.commit()
        self.db.refresh(task)
        
        logger.info(f"Paused learning task: {task.title} (ID: {task.id})")
        return task
    
    def resume_learning_task(self, task_id: int) -> LearningTask:
        """恢复学习任务"""
        task = self.get_learning_task_by_id(task_id)
        
        if task.status != 'paused':
            raise InvalidOperationError(f"Cannot resume task with status: {task.status}")
        
        task.status = 'in_progress'
        task.started_at = datetime.utcnow()  # 重新设置开始时间
        task.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(task)
        
        logger.info(f"Resumed learning task: {task.title} (ID: {task.id})")
        return task
    
    def complete_learning_task(self, task_id: int, completion_notes: Optional[str] = None) -> LearningTask:
        """完成学习任务"""
        task = self.get_learning_task_by_id(task_id)
        
        if task.status not in ['in_progress', 'paused']:
            raise InvalidOperationError(f"Cannot complete task with status: {task.status}")
        
        task.status = 'completed'
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        task.progress = 100
        
        if completion_notes:
            task.completion_notes = completion_notes
        
        # 计算实际花费时间
        if task.started_at:
            if not task.actual_duration:
                task.actual_duration = 0
            if task.status == 'in_progress':
                task.actual_duration += int((datetime.utcnow() - task.started_at).total_seconds())
        
        self.db.commit()
        self.db.refresh(task)
        
        logger.info(f"Completed learning task: {task.title} (ID: {task.id})")
        return task
    
    def update_task_progress(self, task_id: int, progress: int, notes: Optional[str] = None) -> LearningTask:
        """更新任务进度"""
        task = self.get_learning_task_by_id(task_id)
        
        if task.status not in ['in_progress', 'paused']:
            raise InvalidOperationError("Can only update progress for active tasks")
        
        if not 0 <= progress <= 100:
            raise InvalidOperationError("Progress must be between 0 and 100")
        
        task.progress = progress
        task.updated_at = datetime.utcnow()
        
        if notes:
            if not task.progress_notes:
                task.progress_notes = []
            task.progress_notes.append({
                'timestamp': datetime.utcnow().isoformat(),
                'progress': progress,
                'notes': notes
            })
        
        # 如果进度达到100%，自动完成任务
        if progress == 100:
            task.status = 'completed'
            task.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(task)
        
        logger.info(f"Updated progress for task {task.title}: {progress}%")
        return task
    
    def generate_personalized_tasks(self, user_id: int, count: int = 5) -> List[LearningTask]:
        """为用户生成个性化学习任务"""
        # 获取用户最新的技能评估
        latest_assessments = (self.db.query(SkillAssessment)
                            .filter(SkillAssessment.user_id == user_id)
                            .order_by(desc(SkillAssessment.created_at))
                            .limit(10)
                            .all())
        
        if not latest_assessments:
            # 如果没有技能评估，生成基础任务
            return self._generate_basic_tasks(user_id, count)
        
        # 分析技能弱点
        weak_skills = []
        for assessment in latest_assessments:
            percentage = (assessment.score / assessment.max_score) * 100
            if percentage < 70:  # 低于70%的技能需要改进
                weak_skills.append({
                    'skill_type': assessment.skill_type,
                    'score': percentage,
                    'weaknesses': assessment.weaknesses,
                    'recommendations': assessment.recommendations
                })
        
        # 生成针对性任务
        generated_tasks = []
        task_templates = self._get_task_templates()
        
        for i, weak_skill in enumerate(weak_skills[:count]):
            skill_type = weak_skill['skill_type']
            templates = task_templates.get(skill_type, task_templates.get('general', []))
            
            if templates:
                template = random.choice(templates)
                
                # 根据技能水平调整难度
                difficulty = 'beginner' if weak_skill['score'] < 40 else 'intermediate'
                
                task_data = LearningTaskCreate(
                    user_id=user_id,
                    title=template['title'].format(skill=skill_type),
                    description=template['description'].format(skill=skill_type),
                    skill_type=skill_type,
                    difficulty_level=difficulty,
                    estimated_duration=template['duration'],
                    priority='high' if weak_skill['score'] < 50 else 'medium',
                    learning_objectives=template['objectives'],
                    resources=template['resources'],
                    success_criteria=template['success_criteria'],
                    metadata={
                        'generated': True,
                        'based_on_assessment': True,
                        'target_skill_score': weak_skill['score']
                    }
                )
                
                task = self.create_learning_task(task_data)
                generated_tasks.append(task)
        
        # 如果生成的任务不够，补充通用任务
        if len(generated_tasks) < count:
            remaining = count - len(generated_tasks)
            basic_tasks = self._generate_basic_tasks(user_id, remaining)
            generated_tasks.extend(basic_tasks)
        
        logger.info(f"Generated {len(generated_tasks)} personalized tasks for user {user_id}")
        return generated_tasks
    
    def _generate_basic_tasks(self, user_id: int, count: int) -> List[LearningTask]:
        """生成基础学习任务"""
        basic_templates = [
            {
                'title': 'Introduction to Programming Fundamentals',
                'description': 'Learn the basic concepts of programming including variables, data types, and control structures.',
                'skill_type': 'programming_fundamentals',
                'difficulty': 'beginner',
                'duration': 7200,  # 2 hours
                'objectives': ['Understand variables and data types', 'Learn control structures', 'Practice basic algorithms'],
                'resources': ['Online tutorials', 'Practice exercises', 'Documentation'],
                'criteria': ['Complete all exercises', 'Pass quiz with 80% score']
            },
            {
                'title': 'Code Quality and Best Practices',
                'description': 'Learn about writing clean, maintainable code following industry best practices.',
                'skill_type': 'code_quality',
                'difficulty': 'intermediate',
                'duration': 5400,  # 1.5 hours
                'objectives': ['Understand clean code principles', 'Learn refactoring techniques', 'Practice code review'],
                'resources': ['Clean Code book', 'Code review guidelines', 'Refactoring tools'],
                'criteria': ['Refactor existing code', 'Conduct peer code review']
            },
            {
                'title': 'Problem Solving and Algorithms',
                'description': 'Develop problem-solving skills and learn common algorithms and data structures.',
                'skill_type': 'algorithms',
                'difficulty': 'intermediate',
                'duration': 9000,  # 2.5 hours
                'objectives': ['Learn common algorithms', 'Practice problem decomposition', 'Understand time complexity'],
                'resources': ['Algorithm visualizations', 'Practice problems', 'Complexity analysis tools'],
                'criteria': ['Solve 10 algorithm problems', 'Explain time complexity']
            }
        ]
        
        generated_tasks = []
        for i in range(min(count, len(basic_templates))):
            template = basic_templates[i]
            
            task_data = LearningTaskCreate(
                user_id=user_id,
                title=template['title'],
                description=template['description'],
                skill_type=template['skill_type'],
                difficulty_level=template['difficulty'],
                estimated_duration=template['duration'],
                priority='medium',
                learning_objectives=template['objectives'],
                resources=template['resources'],
                success_criteria=template['criteria'],
                metadata={'generated': True, 'type': 'basic'}
            )
            
            task = self.create_learning_task(task_data)
            generated_tasks.append(task)
        
        return generated_tasks
    
    def _get_task_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """获取任务模板"""
        return {
            'python': [
                {
                    'title': 'Master Python {skill} Fundamentals',
                    'description': 'Strengthen your Python programming skills with focused practice on {skill}.',
                    'duration': 7200,
                    'objectives': ['Understand Python syntax', 'Practice data structures', 'Learn OOP concepts'],
                    'resources': ['Python documentation', 'Interactive tutorials', 'Code examples'],
                    'success_criteria': ['Complete coding exercises', 'Build a small project']
                },
                {
                    'title': 'Python {skill} Advanced Techniques',
                    'description': 'Learn advanced Python techniques and best practices for {skill}.',
                    'duration': 10800,
                    'objectives': ['Master advanced features', 'Learn design patterns', 'Optimize performance'],
                    'resources': ['Advanced Python books', 'Performance profiling tools', 'Design pattern examples'],
                    'success_criteria': ['Implement design patterns', 'Optimize existing code']
                }
            ],
            'javascript': [
                {
                    'title': 'JavaScript {skill} Essentials',
                    'description': 'Build strong JavaScript fundamentals focusing on {skill}.',
                    'duration': 6300,
                    'objectives': ['Understand JS fundamentals', 'Learn DOM manipulation', 'Practice async programming'],
                    'resources': ['MDN documentation', 'Interactive coding platforms', 'Project tutorials'],
                    'success_criteria': ['Build interactive web page', 'Handle async operations']
                }
            ],
            'general': [
                {
                    'title': 'Improve {skill} Skills',
                    'description': 'Focused practice to improve your {skill} abilities.',
                    'duration': 5400,
                    'objectives': ['Identify improvement areas', 'Practice systematically', 'Apply new knowledge'],
                    'resources': ['Online courses', 'Practice exercises', 'Community forums'],
                    'success_criteria': ['Complete practice exercises', 'Demonstrate improvement']
                }
            ]
        }
    
    def get_task_recommendations(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """获取任务推荐"""
        # 获取用户已完成的任务
        completed_tasks = self.get_learning_tasks(
            user_id=user_id, 
            status='completed', 
            limit=100
        )
        
        # 获取用户当前进行中的任务
        active_tasks = self.get_learning_tasks(
            user_id=user_id,
            status='in_progress',
            limit=50
        )
        
        # 分析用户学习模式
        completed_skills = set(task.skill_type for task in completed_tasks)
        active_skills = set(task.skill_type for task in active_tasks)
        
        # 获取技能评估数据
        assessments = (self.db.query(SkillAssessment)
                      .filter(SkillAssessment.user_id == user_id)
                      .order_by(desc(SkillAssessment.created_at))
                      .limit(20)
                      .all())
        
        recommendations = []
        
        # 基于技能弱点推荐
        for assessment in assessments:
            percentage = (assessment.score / assessment.max_score) * 100
            if percentage < 75 and assessment.skill_type not in active_skills:
                recommendations.append({
                    'type': 'skill_improvement',
                    'skill_type': assessment.skill_type,
                    'current_score': percentage,
                    'priority': 'high' if percentage < 50 else 'medium',
                    'reason': f'Current skill level is {percentage:.1f}%, improvement needed',
                    'suggested_tasks': self._suggest_tasks_for_skill(assessment.skill_type, percentage)
                })
        
        # 基于学习路径推荐
        if completed_skills:
            next_skills = self._get_next_skills_in_path(completed_skills)
            for skill in next_skills:
                if skill not in active_skills:
                    recommendations.append({
                        'type': 'learning_path',
                        'skill_type': skill,
                        'priority': 'medium',
                        'reason': f'Next step in your learning path after {completed_skills}',
                        'suggested_tasks': self._suggest_tasks_for_skill(skill, 0)
                    })
        
        # 基于时间推荐（定期复习）
        for task in completed_tasks:
            if task.completed_at and (datetime.utcnow() - task.completed_at).days > 30:
                recommendations.append({
                    'type': 'review',
                    'skill_type': task.skill_type,
                    'priority': 'low',
                    'reason': f'Review {task.skill_type} skills (last practiced {(datetime.utcnow() - task.completed_at).days} days ago)',
                    'suggested_tasks': [{
                        'title': f'Review {task.skill_type} Concepts',
                        'description': f'Refresh your knowledge of {task.skill_type}',
                        'estimated_duration': 3600
                    }]
                })
        
        # 排序和限制结果
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return recommendations[:limit]
    
    def _suggest_tasks_for_skill(self, skill_type: str, current_score: float) -> List[Dict[str, Any]]:
        """为特定技能推荐任务"""
        if current_score < 30:
            difficulty = 'beginner'
            duration = 7200  # 2 hours
        elif current_score < 60:
            difficulty = 'intermediate'
            duration = 5400  # 1.5 hours
        else:
            difficulty = 'advanced'
            duration = 3600  # 1 hour
        
        return [{
            'title': f'Improve {skill_type} Skills',
            'description': f'Focused practice to enhance your {skill_type} abilities',
            'difficulty_level': difficulty,
            'estimated_duration': duration
        }]
    
    def _get_next_skills_in_path(self, completed_skills: set) -> List[str]:
        """获取学习路径中的下一个技能"""
        # 定义技能学习路径
        skill_paths = {
            'programming_fundamentals': ['python', 'javascript', 'data_structures'],
            'python': ['web_development', 'data_analysis', 'machine_learning'],
            'javascript': ['react', 'node_js', 'typescript'],
            'web_development': ['database_design', 'api_development', 'deployment'],
            'data_structures': ['algorithms', 'system_design', 'optimization']
        }
        
        next_skills = []
        for completed_skill in completed_skills:
            if completed_skill in skill_paths:
                next_skills.extend(skill_paths[completed_skill])
        
        # 去重并过滤已完成的技能
        return list(set(next_skills) - completed_skills)
    
    def get_learning_progress_statistics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """获取学习进度统计"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 基础统计
        total_tasks = self.db.query(func.count(LearningTask.id)).filter(
            and_(
                LearningTask.user_id == user_id,
                LearningTask.created_at >= start_date
            )
        ).scalar()
        
        completed_tasks = self.db.query(func.count(LearningTask.id)).filter(
            and_(
                LearningTask.user_id == user_id,
                LearningTask.status == 'completed',
                LearningTask.created_at >= start_date
            )
        ).scalar()
        
        in_progress_tasks = self.db.query(func.count(LearningTask.id)).filter(
            and_(
                LearningTask.user_id == user_id,
                LearningTask.status == 'in_progress'
            )
        ).scalar()
        
        # 学习时间统计
        total_study_time = self.db.query(func.sum(LearningTask.actual_duration)).filter(
            and_(
                LearningTask.user_id == user_id,
                LearningTask.status == 'completed',
                LearningTask.created_at >= start_date
            )
        ).scalar() or 0
        
        # 技能分布
        skill_distribution = (self.db.query(
                LearningTask.skill_type,
                func.count(LearningTask.id).label('count'),
                func.sum(LearningTask.actual_duration).label('duration')
            )
            .filter(
                and_(
                    LearningTask.user_id == user_id,
                    LearningTask.created_at >= start_date
                )
            )
            .group_by(LearningTask.skill_type)
            .all())
        
        # 每日完成情况
        daily_completion = (self.db.query(
                func.date(LearningTask.completed_at).label('date'),
                func.count(LearningTask.id).label('completed')
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
            'period_days': days,
            'summary': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'in_progress_tasks': in_progress_tasks,
                'completion_rate': round(completed_tasks / total_tasks * 100, 2) if total_tasks > 0 else 0,
                'total_study_time_seconds': total_study_time,
                'total_study_time_hours': round(total_study_time / 3600, 2),
                'average_task_duration': round(total_study_time / completed_tasks, 2) if completed_tasks > 0 else 0
            },
            'skill_distribution': [{
                'skill_type': skill,
                'task_count': count,
                'study_time_seconds': duration or 0,
                'study_time_hours': round((duration or 0) / 3600, 2)
            } for skill, count, duration in skill_distribution],
            'daily_completion': [{
                'date': date.isoformat(),
                'completed_tasks': completed
            } for date, completed in daily_completion]
        }