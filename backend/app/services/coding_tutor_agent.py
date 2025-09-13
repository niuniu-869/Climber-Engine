#!/usr/bin/env python3
"""
Coding教学Agent服务
负责根据学习进度生成个性化编程教学内容和练习题
"""

import yaml
import json
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.core.database import get_db
from app.models.learning_progress import TechStackAsset, TechStackDebt, LearningProgressSummary
from app.models.learning_content import LearningArticle, LearningQuestion, QuestionAttempt
from app.models.mcp_session import MCPSession, MCPCodeSnippet
from app.models.user import User
from app.services.tech_stack_data_service import TechStackDataService


class CodingTutorAgent:
    """
    Coding教学Agent
    
    主要功能：
    1. 根据学习进度生成个性化教学内容
    2. 创建编程练习题和选择题
    3. 跟踪学习进度并更新技能评估
    4. 提供智能学习路径推荐
    """
    
    def __init__(self, 
                 config_path: str = "app/config/coding_tutor_agent_config.yaml",
                 knowledge_base_path: str = "app/config/tech_knowledge_base.yaml"):
        """初始化Agent"""
        self.config = self._load_config(config_path)
        self.knowledge_base_config = self._load_config(knowledge_base_path)
        self.logger = self._setup_logger()
        
        # 内容模板
        self.content_templates = self._load_content_templates()
        
        # 技术栈知识库
        self.tech_knowledge_base = self._load_tech_knowledge_base()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            # 使用默认配置
            return {
                'basic': {'enabled': True},
                'content_generation': {
                    'default_content_count': 5,
                    'difficulty_levels': ['beginner', 'intermediate', 'advanced', 'expert']
                },
                'ai_integration': {'enable_ai_generation': False}
            }
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('CodingTutorAgent')
        logger.setLevel(getattr(logging, self.config.get('logging', {}).get('level', 'INFO')))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_content_templates(self) -> Dict[str, Dict[str, Any]]:
        """加载内容模板"""
        return {
            'article': {
                'python': {
                    'beginner': {
                        'title': 'Python基础：{topic}入门指南',
                        'structure': ['概念介绍', '基本语法', '代码示例', '实践练习', '总结']
                    },
                    'intermediate': {
                        'title': 'Python进阶：深入理解{topic}',
                        'structure': ['核心概念', '高级特性', '最佳实践', '性能优化', '实际应用']
                    }
                },
                'javascript': {
                    'beginner': {
                        'title': 'JavaScript基础：{topic}完全指南',
                        'structure': ['基础概念', '语法详解', '实例演示', '常见错误', '练习题']
                    }
                }
            },
            'quiz': {
                'multiple_choice': {
                    'structure': {
                        'question': '',
                        'options': [],
                        'correct_answer': 0,
                        'explanation': '',
                        'difficulty': '',
                        'tags': []
                    }
                }
            }
        }
    
    def _load_tech_knowledge_base(self) -> Dict[str, Dict[str, Any]]:
        """从配置文件加载技术栈知识库"""
        return self.knowledge_base_config.get('tech_knowledge_base', {})
    
    def is_enabled(self) -> bool:
        """检查Agent是否启用"""
        return self.config.get('basic', {}).get('enabled', True)
    
    def generate_learning_content(
        self, 
        user_id: int,
        technology: Optional[str] = None,
        content_type: str = 'mixed',
        difficulty: Optional[str] = None,
        count: int = 5
    ) -> Dict[str, Any]:
        """生成学习内容"""
        if not self.is_enabled():
            return {'status': 'disabled', 'message': 'CodingTutorAgent is disabled'}
        
        self.logger.info(f"Generating learning content for user {user_id}, tech: {technology}, type: {content_type}")
        
        try:
            db = next(get_db())
            data_service = TechStackDataService(db)
            
            try:
                # 获取用户信息
                user = data_service.get_user_by_id(user_id)
                if not user:
                    return {'status': 'error', 'message': f'User {user_id} not found'}
                
                # 确定要学习的技术栈
                target_technologies = self._determine_target_technologies(
                    data_service, user_id, technology
                )
                
                if not target_technologies:
                    return {
                        'status': 'no_content',
                        'message': 'No suitable technologies found for learning'
                    }
                
                # 生成内容
                generated_content = []
                
                for tech_info in target_technologies[:count]:
                    tech_name = tech_info['technology']
                    tech_difficulty = difficulty or tech_info.get('recommended_difficulty', 'intermediate')
                    project_context = tech_info.get('project_context')
                    
                    if content_type in ['mixed', 'article']:
                        article = self._generate_article(tech_name, tech_difficulty, user_id, project_context)
                        if article:
                            generated_content.append(article)
                    
                    if content_type in ['mixed', 'quiz']:
                        quiz = self._generate_quiz(tech_name, tech_difficulty, user_id, project_context)
                        if quiz:
                            generated_content.append(quiz)
                    
                    if content_type in ['mixed', 'exercise']:
                        exercise = self._generate_exercise(tech_name, tech_difficulty, user_id, project_context)
                        if exercise:
                            generated_content.append(exercise)
                
                # 保存生成的内容到数据库
                saved_content = self._save_generated_content(db, user_id, generated_content)
                
                db.commit()
                
                return {
                    'status': 'success',
                    'content_count': len(generated_content),
                    'technologies': [tech['technology'] for tech in target_technologies],
                    'content': generated_content,
                    'saved_ids': saved_content,
                    'generated_at': datetime.utcnow().isoformat()
                }
            
            finally:
                db.close()
        
        except Exception as e:
            self.logger.error(f"Error generating learning content: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _determine_target_technologies(
        self, 
        data_service: TechStackDataService, 
        user_id: int, 
        specified_tech: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """确定目标学习技术栈 - 基于学习进度和实际项目使用情况"""
        if specified_tech:
            # 用户指定了技术栈
            return [{
                'technology': specified_tech,
                'reason': 'user_specified',
                'recommended_difficulty': self._get_recommended_difficulty(data_service, user_id, specified_tech)
            }]
        
        # 获取用户最近项目中实际使用的技术栈
        project_technologies = self._get_project_technologies(data_service.db, user_id)
        
        # 自动推荐技术栈
        recommendations = []
        
        # 优先推荐：项目中正在使用但技能不足的技术
        for tech_info in project_technologies:
            tech_name = tech_info['technology']
            
            # 检查用户对该技术的掌握程度
            asset = data_service.get_tech_stack_asset_by_name(user_id, tech_name)
            debt = data_service.get_tech_stack_debt_by_name(user_id, tech_name)
            
            if debt:  # 有技术债务，优先级最高
                recommendations.append({
                    'technology': tech_name,
                    'reason': 'project_debt_critical',
                    'urgency': debt.urgency_level,
                    'importance': debt.importance_score + 20,  # 项目相关性加分
                    'recommended_difficulty': debt.target_proficiency_level,
                    'project_context': tech_info['context'],
                    'recent_usage': tech_info['usage_frequency']
                })
            elif asset and asset.proficiency_score < 70:  # 技能不足
                next_level = self._get_next_difficulty_level(asset.proficiency_level)
                if next_level:
                    recommendations.append({
                        'technology': tech_name,
                        'reason': 'project_skill_gap',
                        'current_proficiency': asset.proficiency_score,
                        'recommended_difficulty': next_level,
                        'project_context': tech_info['context'],
                        'recent_usage': tech_info['usage_frequency']
                    })
            elif not asset:  # 项目中使用但没有技能记录
                recommendations.append({
                    'technology': tech_name,
                    'reason': 'project_new_tech',
                    'recommended_difficulty': 'beginner',
                    'project_context': tech_info['context'],
                    'recent_usage': tech_info['usage_frequency']
                })
        
        # 次要推荐：非项目相关的技术栈负债
        debts = data_service.get_tech_stack_debts(user_id, is_active=True)
        sorted_debts = sorted(debts, key=lambda d: (
            d.learning_priority,
            d.importance_score,
            d.urgency_level == 'critical',
            d.urgency_level == 'high'
        ), reverse=True)
        
        for debt in sorted_debts[:5]:  # 减少非项目相关推荐
            # 避免重复推荐
            if not any(r['technology'] == debt.technology_name for r in recommendations):
                recommendations.append({
                    'technology': debt.technology_name,
                    'reason': 'general_debt_repayment',
                    'urgency': debt.urgency_level,
                    'importance': debt.importance_score,
                    'recommended_difficulty': debt.target_proficiency_level
                })
        
        # 按重要性和项目相关性排序
        recommendations.sort(key=lambda x: (
            x.get('importance', 0) + (20 if 'project' in x['reason'] else 0),
            x.get('recent_usage', 0)
        ), reverse=True)
        
        return recommendations
    
    def _get_project_technologies(self, db: Session, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """分析用户最近项目中实际使用的技术栈"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # 获取最近的MCP会话
        recent_sessions = db.query(MCPSession).filter(
            and_(
                MCPSession.user_id == user_id,
                MCPSession.created_at >= cutoff_date,
                MCPSession.status.in_(['active', 'completed'])
            )
        ).order_by(MCPSession.created_at.desc()).limit(20).all()
        
        # 统计技术栈使用情况
        tech_usage = {}
        
        for session in recent_sessions:
            # 分析会话中的技术栈
            technologies = session.technologies or []
            frameworks = session.frameworks or []
            libraries = session.libraries or []
            tools = session.tools or []
            
            # 合并所有技术
            all_techs = technologies + frameworks + libraries + tools
            
            for tech in all_techs:
                if tech not in tech_usage:
                    tech_usage[tech] = {
                        'usage_count': 0,
                        'total_duration': 0,
                        'projects': set(),
                        'work_types': set(),
                        'complexity_scores': [],
                        'recent_tasks': []
                    }
                
                tech_usage[tech]['usage_count'] += 1
                tech_usage[tech]['total_duration'] += session.actual_duration or session.estimated_duration or 0
                tech_usage[tech]['projects'].add(session.project_name or 'Unknown')
                tech_usage[tech]['work_types'].add(session.work_type)
                
                if session.complexity_score:
                    tech_usage[tech]['complexity_scores'].append(session.complexity_score)
                
                # 记录最近的任务描述
                if len(tech_usage[tech]['recent_tasks']) < 3:
                    tech_usage[tech]['recent_tasks'].append({
                        'task': session.task_description[:100] + '...' if len(session.task_description) > 100 else session.task_description,
                        'work_type': session.work_type,
                        'date': session.created_at.isoformat()
                    })
        
        # 转换为推荐格式
        project_technologies = []
        for tech, usage in tech_usage.items():
            if usage['usage_count'] >= 2:  # 至少使用过2次才推荐
                avg_complexity = sum(usage['complexity_scores']) / len(usage['complexity_scores']) if usage['complexity_scores'] else 5.0
                
                project_technologies.append({
                    'technology': tech,
                    'usage_frequency': usage['usage_count'],
                    'total_time_spent': usage['total_duration'],
                    'project_count': len(usage['projects']),
                    'work_types': list(usage['work_types']),
                    'average_complexity': avg_complexity,
                    'context': {
                        'projects': list(usage['projects']),
                        'recent_tasks': usage['recent_tasks'],
                        'primary_use_cases': list(usage['work_types'])
                    }
                })
        
        # 按使用频率和复杂度排序
        project_technologies.sort(key=lambda x: (
            x['usage_frequency'],
            x['total_time_spent'],
            x['average_complexity']
        ), reverse=True)
        
        return project_technologies[:10]  # 返回前10个最相关的技术
    
    def _get_recommended_difficulty(
        self, 
        data_service: TechStackDataService, 
        user_id: int, 
        technology: str
    ) -> str:
        """获取推荐的学习难度"""
        # 检查用户是否已经掌握这个技术
        asset = data_service.get_tech_stack_asset_by_name(user_id, technology)
        
        if asset:
            # 已掌握，推荐更高难度
            return self._get_next_difficulty_level(asset.proficiency_level)
        
        # 未掌握，检查是否在负债列表中
        debt = data_service.get_tech_stack_debt_by_name(user_id, technology)
        
        if debt:
            return debt.target_proficiency_level
        
        # 默认中等难度
        return 'intermediate'
    
    def _get_next_difficulty_level(self, current_level: str) -> str:
        """获取下一个难度级别"""
        levels = ['beginner', 'intermediate', 'advanced', 'expert']
        
        try:
            current_index = levels.index(current_level)
            if current_index < len(levels) - 1:
                return levels[current_index + 1]
        except ValueError:
            pass
        
        return 'intermediate'
    
    def _generate_article(
        self, 
        technology: str, 
        difficulty: str, 
        user_id: int,
        project_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """生成技术文章 - 基于项目上下文"""
        try:
            # 获取技术相关的主题
            topics = self._get_topics_for_technology(technology, difficulty, project_context)
            
            if not topics:
                return None
            
            topic = random.choice(topics)
            
            # 生成文章内容
            article_content = self._create_article_content(technology, topic, difficulty, project_context)
            
            return {
                'type': 'article',
                'technology': technology,
                'difficulty': difficulty,
                'title': article_content['title'],
                'content': article_content['content'],
                'estimated_reading_time': article_content['estimated_reading_time'],
                'learning_objectives': article_content['learning_objectives'],
                'code_examples': article_content.get('code_examples', []),
                'project_relevance': article_content.get('project_relevance', {}),
                'practical_applications': article_content.get('practical_applications', []),
                'created_at': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error generating article for {technology}: {str(e)}")
            return None
    
    def _generate_quiz(
        self, 
        technology: str, 
        difficulty: str, 
        user_id: int,
        project_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """生成选择题测验 - 基于项目上下文"""
        try:
            questions_count = self.config.get('content_generation', {}).get('content_types', {}).get('quiz', {}).get('questions_per_quiz', 5)
            
            questions = []
            
            for i in range(questions_count):
                question = self._create_quiz_question(technology, difficulty, project_context)
                if question:
                    questions.append(question)
            
            if not questions:
                return None
            
            # 根据项目上下文调整标题和描述
            title = f'{technology} {difficulty.title()} 级测验'
            description = f'测试你对 {technology} 的理解程度'
            
            if project_context:
                projects = project_context.get('projects', [])
                if projects:
                    title += f' - 基于{projects[0]}项目'
                    description += f'，重点关注在{projects[0]}项目中的实际应用'
            
            result = {
                'type': 'quiz',
                'technology': technology,
                'difficulty': difficulty,
                'title': title,
                'description': description,
                'questions': questions,
                'total_questions': len(questions),
                'estimated_time_minutes': len(questions) * 2,  # 每题2分钟
                'passing_score': 70,
                'created_at': datetime.utcnow().isoformat()
            }
            
            if project_context:
                result['project_relevance'] = {
                    'usage_frequency': project_context.get('usage_frequency', 0),
                    'project_count': project_context.get('project_count', 0)
                }
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error generating quiz for {technology}: {str(e)}")
            return None
    
    def _generate_exercise(
        self, 
        technology: str, 
        difficulty: str, 
        user_id: int,
        project_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """生成编程练习 - 基于项目上下文"""
        try:
            exercise_content = self._create_exercise_content(technology, difficulty, project_context)
            
            if not exercise_content:
                return None
            
            result = {
                'type': 'exercise',
                'technology': technology,
                'difficulty': difficulty,
                'title': exercise_content['title'],
                'description': exercise_content['description'],
                'requirements': exercise_content['requirements'],
                'starter_code': exercise_content.get('starter_code', ''),
                'test_cases': exercise_content.get('test_cases', []),
                'hints': exercise_content.get('hints', []),
                'solution': exercise_content.get('solution', ''),
                'estimated_time_minutes': exercise_content.get('estimated_time', 30),
                'created_at': datetime.utcnow().isoformat()
            }
            
            if project_context:
                result['project_relevance'] = {
                    'usage_frequency': project_context.get('usage_frequency', 0),
                    'project_count': project_context.get('project_count', 0),
                    'real_world_application': True
                }
                result['practical_context'] = exercise_content.get('practical_context', {})
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error generating exercise for {technology}: {str(e)}")
            return None
    
    def _get_topics_for_technology(self, technology: str, difficulty: str, project_context: Optional[Dict[str, Any]] = None) -> List[str]:
        """获取技术相关的主题 - 基于项目上下文"""
        tech_key = technology.lower()
        
        # 基础主题
        base_topics = []
        if tech_key in self.tech_knowledge_base:
            base_topics = self.tech_knowledge_base[tech_key].get('topics', {}).get(difficulty, [])
        
        if not base_topics:
            # 默认主题
            default_topics = {
                'beginner': ['基础概念', '语法入门', '简单示例'],
                'intermediate': ['核心特性', '最佳实践', '常用模式'],
                'advanced': ['高级特性', '性能优化', '架构设计'],
                'expert': ['内部机制', '扩展开发', '系统设计']
            }
            base_topics = default_topics.get(difficulty, ['基础概念'])
        
        # 如果有项目上下文，优先选择项目相关的主题
        if project_context:
            project_topics = self._get_project_relevant_topics(technology, difficulty, project_context)
            if project_topics:
                # 项目相关主题优先，然后是基础主题
                return project_topics + [t for t in base_topics if t not in project_topics]
        
        return base_topics
    
    def _get_project_relevant_topics(self, technology: str, difficulty: str, project_context: Dict[str, Any]) -> List[str]:
        """根据项目上下文生成相关主题"""
        topics = []
        work_types = project_context.get('primary_use_cases', [])
        recent_tasks = project_context.get('recent_tasks', [])
        
        # 根据工作类型生成主题
        work_type_topics = {
            'development': [f'{technology}项目开发实践', f'{technology}开发环境配置', f'{technology}项目结构设计'],
            'debugging': [f'{technology}调试技巧', f'{technology}错误处理', f'{technology}性能问题排查'],
            'refactoring': [f'{technology}代码重构', f'{technology}设计模式应用', f'{technology}代码优化'],
            'testing': [f'{technology}单元测试', f'{technology}集成测试', f'{technology}测试驱动开发'],
            'documentation': [f'{technology}文档编写', f'{technology}API文档', f'{technology}代码注释规范'],
            'analysis': [f'{technology}代码分析', f'{technology}架构分析', f'{technology}性能分析']
        }
        
        for work_type in work_types:
            if work_type in work_type_topics:
                topics.extend(work_type_topics[work_type])
        
        # 根据最近任务生成主题
        for task_info in recent_tasks[:2]:  # 只取最近2个任务
            task_desc = task_info.get('task', '').lower()
            if 'api' in task_desc:
                topics.append(f'{technology} API开发')
            if 'database' in task_desc or 'db' in task_desc:
                topics.append(f'{technology}数据库操作')
            if 'frontend' in task_desc or 'ui' in task_desc:
                topics.append(f'{technology}前端开发')
            if 'backend' in task_desc or 'server' in task_desc:
                topics.append(f'{technology}后端开发')
        
        return list(set(topics))  # 去重
    
    def _create_article_content(
        self, 
        technology: str, 
        topic: str, 
        difficulty: str,
        project_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """创建文章内容 - 基于项目上下文"""
        # 这里可以集成AI生成或使用模板
        title = f"{technology} {difficulty.title()}: {topic}"
        
        # 生成学习目标
        learning_objectives = [
            f"理解{topic}的核心概念",
            f"掌握{topic}的基本用法",
            f"能够在实际项目中应用{topic}"
        ]
        
        # 如果有项目上下文，添加项目相关的学习目标
        if project_context:
            projects = project_context.get('projects', [])
            work_types = project_context.get('primary_use_cases', [])
            if projects:
                learning_objectives.append(f"在{', '.join(projects[:2])}等项目中应用{topic}")
            if work_types:
                learning_objectives.append(f"解决{', '.join(work_types[:2])}中的实际问题")
        
        # 生成文章结构
        sections = {
            'beginner': [
                '## 什么是{topic}？',
                '## 基本概念',
                '## 简单示例',
                '## 常见用法',
                '## 练习建议'
            ],
            'intermediate': [
                '## {topic}深入理解',
                '## 核心原理',
                '## 实际应用',
                '## 最佳实践',
                '## 常见陷阱'
            ],
            'advanced': [
                '## {topic}高级特性',
                '## 性能考虑',
                '## 架构设计',
                '## 优化策略',
                '## 实战案例'
            ]
        }
        
        section_templates = sections.get(difficulty, sections['intermediate'])
        
        content_parts = []
        code_examples = []
        practical_applications = []
        project_relevance = {}
        
        # 如果有项目上下文，添加项目相关信息
        if project_context:
            recent_tasks = project_context.get('recent_tasks', [])
            for task in recent_tasks[:2]:
                practical_applications.append({
                    'scenario': task.get('work_type', '开发'),
                    'description': f"在{task.get('task', '项目开发')}中的应用",
                    'relevance': '高'
                })
            
            project_relevance = {
                'usage_frequency': project_context.get('usage_frequency', 0),
                'project_count': project_context.get('project_count', 0),
                'complexity_level': project_context.get('average_complexity', 5.0)
            }
            
            # 添加项目相关章节
            if practical_applications:
                content_parts.append('## 在你的项目中的应用')
                content_parts.append(f'根据你最近的项目经验，{topic}主要用于：')
                for app in practical_applications:
                    content_parts.append(f'- {app["description"]}')
                content_parts.append('')
        
        for section_template in section_templates:
            section_title = section_template.format(topic=topic)
            content_parts.append(section_title)
            
            # 添加示例内容
            if '示例' in section_title or '案例' in section_title:
                code_example = self._generate_code_example(technology, topic, difficulty)
                if code_example:
                    content_parts.append(f"```{technology.lower()}\n{code_example}\n```")
                    code_examples.append({
                        'title': f"{topic}示例",
                        'code': code_example,
                        'language': technology.lower()
                    })
            else:
                content_parts.append(f"这里是关于{topic}的详细说明...")
            
            content_parts.append('')  # 空行
        
        content = '\n'.join(content_parts)
        
        result = {
            'title': title,
            'content': content,
            'estimated_reading_time': max(5, len(content) // 200),  # 估算阅读时间
            'learning_objectives': learning_objectives,
            'code_examples': code_examples
        }
        
        if practical_applications:
            result['practical_applications'] = practical_applications
        if project_relevance:
            result['project_relevance'] = project_relevance
            
        return result
    
    def _create_quiz_question(
        self, 
        technology: str, 
        difficulty: str,
        project_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """创建测验问题"""
        # 问题模板
        question_templates = {
            'python': {
                'beginner': [
                    {
                        'question': '在Python中，以下哪个是正确的变量命名？',
                        'options': ['2variable', 'variable_name', 'variable-name', 'variable name'],
                        'correct_answer': 1,
                        'explanation': 'Python变量名应该使用下划线连接，不能以数字开头，不能包含空格或连字符。'
                    },
                    {
                        'question': 'Python中哪个关键字用于定义函数？',
                        'options': ['function', 'def', 'func', 'define'],
                        'correct_answer': 1,
                        'explanation': 'Python使用def关键字来定义函数。'
                    }
                ],
                'intermediate': [
                    {
                        'question': '以下哪个是Python装饰器的正确语法？',
                        'options': ['@decorator\ndef func():', 'decorator(def func():)', 'def func() @decorator:', '@decorator func():'],
                        'correct_answer': 0,
                        'explanation': '装饰器使用@符号放在函数定义之前。'
                    }
                ]
            },
            'javascript': {
                'beginner': [
                    {
                        'question': 'JavaScript中声明变量的关键字有哪些？',
                        'options': ['var, let, const', 'variable, let, const', 'var, let, constant', 'declare, let, const'],
                        'correct_answer': 0,
                        'explanation': 'JavaScript中可以使用var、let和const来声明变量。'
                    }
                ]
            },
            'java': {
                'beginner': [
                    {
                        'question': 'Java中哪个关键字用于定义类？',
                        'options': ['class', 'Class', 'define', 'object'],
                        'correct_answer': 0,
                        'explanation': 'Java使用class关键字来定义类。'
                    }
                ],
                'intermediate': [
                    {
                        'question': 'Java中哪个访问修饰符表示只有同一个包中的类可以访问？',
                        'options': ['private', 'protected', 'package-private(默认)', 'public'],
                        'correct_answer': 2,
                        'explanation': '不写访问修饰符时，默认为package-private，只有同一个包中的类可以访问。'
                    }
                ]
            },
            'django': {
                'beginner': [
                    {
                        'question': 'Django中用于创建新项目的命令是？',
                        'options': ['django-admin startproject', 'python manage.py startproject', 'django create project', 'python django.py new'],
                        'correct_answer': 0,
                        'explanation': 'django-admin startproject 命令用于创建新的Django项目。'
                    }
                ]
            },
            'pandas': {
                'beginner': [
                    {
                        'question': 'Pandas中用于读取CSV文件的函数是？',
                        'options': ['read_csv()', 'load_csv()', 'import_csv()', 'open_csv()'],
                        'correct_answer': 0,
                        'explanation': 'pandas.read_csv()函数用于读取CSV文件并创建DataFrame。'
                    }
                ]
            },
            'redis': {
                'beginner': [
                    {
                        'question': 'Redis是什么类型的数据库？',
                        'options': ['关系型数据库', '内存数据库', '文档数据库', '图数据库'],
                        'correct_answer': 1,
                        'explanation': 'Redis是一个开源的内存数据结构存储系统。'
                    }
                ]
            },
            'git': {
                'beginner': [
                    {
                        'question': 'Git中用于提交更改的命令是？',
                        'options': ['git commit', 'git save', 'git push', 'git update'],
                        'correct_answer': 0,
                        'explanation': 'git commit命令用于将暂存区的更改提交到本地仓库。'
                    }
                ]
            }
        }
        
        tech_key = technology.lower()
        
        if tech_key in question_templates and difficulty in question_templates[tech_key]:
            questions = question_templates[tech_key][difficulty]
            if questions:
                question_data = random.choice(questions)
                return {
                    'id': f"{tech_key}_{difficulty}_{random.randint(1000, 9999)}",
                    'question': question_data['question'],
                    'options': question_data['options'],
                    'correct_answer': question_data['correct_answer'],
                    'explanation': question_data['explanation'],
                    'difficulty': difficulty,
                    'technology': technology,
                    'tags': [technology, difficulty]
                }
        
        # 生成通用问题
        return {
            'id': f"{tech_key}_{difficulty}_{random.randint(1000, 9999)}",
            'question': f'关于{technology}的{difficulty}级问题',
            'options': ['选项A', '选项B', '选项C', '选项D'],
            'correct_answer': 0,
            'explanation': f'这是一个关于{technology}的{difficulty}级问题的解释。',
            'difficulty': difficulty,
            'technology': technology,
            'tags': [technology, difficulty]
        }
    
    def _create_exercise_content(
        self, 
        technology: str, 
        difficulty: str,
        project_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """创建练习内容"""
        exercise_templates = {
            'python': {
                'beginner': {
                    'title': 'Python基础练习：计算器',
                    'description': '创建一个简单的计算器，支持加减乘除运算',
                    'requirements': [
                        '实现add、subtract、multiply、divide四个函数',
                        '处理除零错误',
                        '返回正确的计算结果'
                    ],
                    'starter_code': '''def add(a, b):
    # 实现加法
    pass

def subtract(a, b):
    # 实现减法
    pass

def multiply(a, b):
    # 实现乘法
    pass

def divide(a, b):
    # 实现除法，注意处理除零情况
    pass''',
                    'test_cases': [
                        {'input': 'add(2, 3)', 'expected': 5},
                        {'input': 'subtract(5, 3)', 'expected': 2},
                        {'input': 'multiply(4, 3)', 'expected': 12},
                        {'input': 'divide(10, 2)', 'expected': 5.0}
                    ],
                    'solution': '''def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b'''
                }
            },
            'javascript': {
                'beginner': {
                    'title': 'JavaScript基础练习：数组操作',
                    'description': '实现常用的数组操作函数',
                    'requirements': [
                        '实现数组求和函数',
                        '实现数组最大值函数',
                        '实现数组过滤函数'
                    ],
                    'starter_code': '''function sumArray(arr) {
    // 计算数组元素的总和
}

function findMax(arr) {
    // 找到数组中的最大值
}

function filterEven(arr) {
    // 过滤出数组中的偶数
}'''
                }
            }
        }
        
        tech_key = technology.lower()
        
        if tech_key in exercise_templates and difficulty in exercise_templates[tech_key]:
            return exercise_templates[tech_key][difficulty]
        
        # 生成通用练习
        return {
            'title': f'{technology} {difficulty.title()} 练习',
            'description': f'这是一个{technology}的{difficulty}级编程练习',
            'requirements': [f'使用{technology}完成指定功能'],
            'starter_code': f'// {technology} {difficulty} 练习代码\n// 请在这里实现你的解决方案',
            'estimated_time': 30
        }
    
    def _generate_code_example(
        self, 
        technology: str, 
        topic: str, 
        difficulty: str
    ) -> str:
        """生成代码示例"""
        code_templates = {
            'python': {
                'beginner': f'''# {topic} 示例
print("Hello, {topic}!")

# 基本用法
result = "这是一个{topic}的例子"
print(result)''',
                'intermediate': f'''# {topic} 高级示例
class {topic.replace(' ', '')}Example:
    def __init__(self):
        self.data = []
    
    def process(self):
        # 处理逻辑
        return self.data

# 使用示例
example = {topic.replace(' ', '')}Example()
result = example.process()'''
            },
            'javascript': {
                'beginner': f'''// {topic} 示例
console.log("Hello, {topic}!");

// 基本用法
const result = "{topic}的JavaScript示例";
console.log(result);''',
                'intermediate': f'''// {topic} 高级示例
class {topic.replace(' ', '')}Example {{
    constructor() {{
        this.data = [];
    }}
    
    process() {{
        // 处理逻辑
        return this.data;
    }}
}}

// 使用示例
const example = new {topic.replace(' ', '')}Example();
const result = example.process();'''
            }
        }
        
        tech_key = technology.lower()
        
        if tech_key in code_templates and difficulty in code_templates[tech_key]:
            return code_templates[tech_key][difficulty]
        
        return f'// {technology} {topic} 示例代码\nconsole.log("{topic} 示例");'
    
    def _save_generated_content(
        self, 
        db: Session, 
        user_id: int, 
        content_list: List[Dict[str, Any]]
    ) -> List[int]:
        """保存生成的内容到数据库"""
        saved_ids = []
        
        for content in content_list:
            try:
                if content['type'] == 'article':
                    article = LearningArticle(
                        user_id=user_id,
                        title=content['title'],
                        content=content['content'],
                        article_type='tutorial',
                        category='programming',
                        target_technologies=[content['technology']],
                        difficulty_level=content['difficulty'],
                        estimated_reading_time=content.get('estimated_reading_time', 10),
                        learning_objectives=content.get('learning_objectives', []),
                        code_examples=content.get('code_examples', []),
                        ai_model_used='built-in-templates',
                        created_at=datetime.utcnow()
                    )
                    db.add(article)
                    db.flush()
                    saved_ids.append(article.id)
                
                elif content['type'] == 'quiz':
                    for question_data in content['questions']:
                        question = LearningQuestion(
                        user_id=user_id,
                        title=question_data['question'][:100],  # 使用问题前100字符作为标题
                        question_text=question_data['question'],
                        question_type='multiple_choice',
                        options=question_data['options'],
                        correct_answer=question_data['correct_answer'],
                        explanation=question_data['explanation'],
                        target_technologies=[content['technology']],
                        difficulty_level=content['difficulty'],
                        tags=question_data.get('tags', []),
                        ai_model_used='built-in-templates',
                        created_at=datetime.utcnow()
                    )
                        db.add(question)
                        db.flush()
                        saved_ids.append(question.id)
            
            except Exception as e:
                self.logger.error(f"Error saving content: {str(e)}")
                continue
        
        return saved_ids
    
    def record_learning_attempt(
        self, 
        user_id: int, 
        content_id: int, 
        content_type: str,
        attempt_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """记录学习尝试"""
        try:
            db = next(get_db())
            
            try:
                if content_type == 'quiz':
                    # 记录答题尝试
                    attempt = QuestionAttempt(
                        user_id=user_id,
                        question_id=content_id,
                        selected_answer=attempt_data.get('selected_answer'),
                        is_correct=attempt_data.get('is_correct', False),
                        time_spent_seconds=attempt_data.get('time_spent', 0),
                        attempt_at=datetime.utcnow()
                    )
                    db.add(attempt)
                    
                    # 更新学习进度
                    question = db.query(LearningQuestion).filter(LearningQuestion.id == content_id).first()
                    if question and question.target_technologies:
                        for tech in question.target_technologies:
                            self._update_learning_progress(
                                db, user_id, tech, 
                                question.difficulty_level, attempt_data.get('is_correct', False)
                            )
                
                elif content_type == 'article':
                    # 记录文章阅读
                    self._record_article_reading(
                        db, user_id, content_id, attempt_data
                    )
                
                db.commit()
                
                return {
                    'status': 'success',
                    'message': 'Learning attempt recorded successfully',
                    'recorded_at': datetime.utcnow().isoformat()
                }
            
            finally:
                db.close()
        
        except Exception as e:
            self.logger.error(f"Error recording learning attempt: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _update_learning_progress(
        self, 
        db: Session, 
        user_id: int, 
        technology: str, 
        difficulty: str, 
        is_correct: bool
    ):
        """更新学习进度"""
        data_service = TechStackDataService(db)
        
        # 查找或创建技术栈资产
        asset = data_service.get_tech_stack_asset_by_name(user_id, technology)
        
        if not asset:
            # 创建新的技术栈资产
            from app.schemas.learning_progress import TechStackAssetCreate
            asset_data = TechStackAssetCreate(
                user_id=user_id,
                technology_name=technology,
                category='programming_language',  # 默认分类
                proficiency_level='beginner',
                proficiency_score=0.0,
                confidence_level=0.0
            )
            asset = data_service.create_tech_stack_asset(asset_data)
        
        # 根据答题结果更新熟练度
        if is_correct:
            # 正确答题，增加熟练度
            difficulty_multiplier = {
                'beginner': 1.0,
                'intermediate': 1.5,
                'advanced': 2.0,
                'expert': 2.5
            }.get(difficulty, 1.0)
            
            score_increment = 2.0 * difficulty_multiplier
            asset.proficiency_score = min(100.0, asset.proficiency_score + score_increment)
        else:
            # 错误答题，轻微减少熟练度
            asset.proficiency_score = max(0.0, asset.proficiency_score - 0.5)
        
        # 更新熟练度级别
        if asset.proficiency_score >= 80:
            asset.proficiency_level = "expert"
        elif asset.proficiency_score >= 60:
            asset.proficiency_level = "advanced"
        elif asset.proficiency_score >= 30:
            asset.proficiency_level = "intermediate"
        else:
            asset.proficiency_level = "beginner"
        
        # 更新信心水平
        asset.confidence_level = min(1.0, asset.proficiency_score / 100.0)
        asset.last_practiced_date = datetime.utcnow()
        asset.updated_at = datetime.utcnow()
    
    def _record_article_reading(
        self, 
        db: Session, 
        user_id: int, 
        article_id: int, 
        reading_data: Dict[str, Any]
    ):
        """记录文章阅读"""
        # 这里可以记录阅读时间、完成度等信息
        # 暂时简单处理
        pass
    
    def get_learning_recommendations(
        self, 
        user_id: int, 
        limit: int = 10
    ) -> Dict[str, Any]:
        """获取学习推荐"""
        try:
            db = next(get_db())
            data_service = TechStackDataService(db)
            
            try:
                recommendations = self._determine_target_technologies(
                    data_service, user_id
                )
                
                return {
                    'status': 'success',
                    'recommendations': recommendations[:limit],
                    'total_count': len(recommendations),
                    'generated_at': datetime.utcnow().isoformat()
                }
            
            finally:
                db.close()
        
        except Exception as e:
            self.logger.error(f"Error getting learning recommendations: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_agent_status(self) -> Dict[str, Any]:
        """获取Agent状态"""
        return {
            'enabled': self.is_enabled(),
            'config': {
                'default_content_count': self.config.get('content_generation', {}).get('default_content_count', 5),
                'ai_generation_enabled': self.config.get('ai_integration', {}).get('enable_ai_generation', False),
                'supported_content_types': ['article', 'quiz', 'exercise']
            },
            'tech_knowledge_base_size': len(self.tech_knowledge_base),
            'supported_technologies': list(self.tech_knowledge_base.keys())
        }