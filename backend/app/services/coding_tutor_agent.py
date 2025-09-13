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
    
    def __init__(self, config_path: str = "app/config/coding_tutor_agent_config.yaml"):
        """初始化Agent"""
        self.config = self._load_config(config_path)
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
        """加载技术栈知识库"""
        return {
            'python': {
                'topics': {
                    'beginner': ['变量和数据类型', '控制流', '函数', '列表和字典', '文件操作'],
                    'intermediate': ['面向对象编程', '异常处理', '模块和包', '装饰器', '生成器'],
                    'advanced': ['元类', '并发编程', '性能优化', '设计模式', '测试驱动开发'],
                    'expert': ['CPython内部机制', '扩展开发', '内存管理', '高性能计算', '分布式系统']
                },
                'common_patterns': [
                    '列表推导式', '上下文管理器', '迭代器模式', '单例模式', 'MVC架构'
                ],
                'best_practices': [
                    'PEP 8代码风格', '异常处理', '文档字符串', '单元测试', '代码重构'
                ]
            },
            'javascript': {
                'topics': {
                    'beginner': ['变量声明', '数据类型', '函数', '数组和对象', 'DOM操作'],
                    'intermediate': ['闭包', '原型链', '异步编程', 'ES6+特性', '模块系统'],
                    'advanced': ['设计模式', '性能优化', '函数式编程', 'TypeScript', '构建工具'],
                    'expert': ['V8引擎原理', '微前端架构', '性能监控', '安全最佳实践', 'Node.js高级特性']
                }
            },
            'react': {
                'topics': {
                    'beginner': ['组件基础', 'JSX语法', 'Props和State', '事件处理', '条件渲染'],
                    'intermediate': ['Hooks', '状态管理', '路由', '表单处理', '生命周期'],
                    'advanced': ['性能优化', '自定义Hooks', '上下文API', '错误边界', '代码分割'],
                    'expert': ['Fiber架构', '服务端渲染', '微前端', '测试策略', '构建优化']
                }
            },
            'java': {
                'topics': {
                    'beginner': ['基本语法', '数据类型', '控制结构', '数组', '字符串处理'],
                    'intermediate': ['面向对象编程', '继承和多态', '接口和抽象类', '异常处理', '集合框架'],
                    'advanced': ['多线程编程', '网络编程', '数据库连接', '设计模式', 'JVM调优'],
                    'expert': ['JVM内部机制', '性能调优', '分布式系统', '微服务架构', '企业级开发']
                }
            },
            'django': {
                'topics': {
                    'beginner': ['项目结构', '模型定义', '视图函数', '模板系统', 'URL配置'],
                    'intermediate': ['表单处理', '用户认证', '中间件', '静态文件', '数据库迁移'],
                    'advanced': ['REST API开发', '缓存策略', '信号系统', '自定义管理命令', '部署配置'],
                    'expert': ['性能优化', '安全最佳实践', '大规模应用架构', '微服务集成', '高可用部署']
                }
            },
            'postman': {
                'topics': {
                    'beginner': ['界面介绍', '发送请求', '查看响应', '保存请求', '创建集合'],
                    'intermediate': ['环境变量', '测试脚本', '数据驱动测试', '工作流程', '团队协作'],
                    'advanced': ['自动化测试', 'CI/CD集成', '监控和报告', '模拟服务器', 'API文档生成'],
                    'expert': ['企业级管理', '高级脚本编写', '性能测试', '安全测试', '大规模API管理']
                }
            },
            'pandas': {
                'topics': {
                    'beginner': ['数据结构', '数据读取', '基本操作', '数据选择', '简单统计'],
                    'intermediate': ['数据清洗', '数据转换', '分组聚合', '数据合并', '时间序列'],
                    'advanced': ['性能优化', '大数据处理', '自定义函数', '数据可视化', '机器学习集成'],
                    'expert': ['内存优化', '并行处理', '扩展开发', '企业级数据管道', '实时数据处理']
                }
            },
            'redis': {
                'topics': {
                    'beginner': ['基本概念', '数据类型', '基本命令', '连接配置', '简单操作'],
                    'intermediate': ['持久化机制', '发布订阅', '事务处理', '管道操作', '脚本编程'],
                    'advanced': ['集群配置', '主从复制', '哨兵模式', '性能调优', '监控管理'],
                    'expert': ['分布式架构', '高可用设计', '数据分片', '故障恢复', '企业级部署']
                }
            },
            'git': {
                'topics': {
                    'beginner': ['版本控制概念', '基本命令', '提交和推送', '分支基础', '克隆仓库'],
                    'intermediate': ['分支管理', '合并冲突', '标签管理', '远程仓库', '工作流程'],
                    'advanced': ['高级分支策略', '重写历史', '子模块', '钩子脚本', '大文件管理'],
                    'expert': ['企业级工作流', '自动化集成', '性能优化', '安全管理', '大型项目管理']
                }
            }
        }
    
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
                    
                    if content_type in ['mixed', 'article']:
                        article = self._generate_article(tech_name, tech_difficulty, user_id)
                        if article:
                            generated_content.append(article)
                    
                    if content_type in ['mixed', 'quiz']:
                        quiz = self._generate_quiz(tech_name, tech_difficulty, user_id)
                        if quiz:
                            generated_content.append(quiz)
                    
                    if content_type in ['mixed', 'exercise']:
                        exercise = self._generate_exercise(tech_name, tech_difficulty, user_id)
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
        """确定目标学习技术栈"""
        if specified_tech:
            # 用户指定了技术栈
            return [{
                'technology': specified_tech,
                'reason': 'user_specified',
                'recommended_difficulty': self._get_recommended_difficulty(data_service, user_id, specified_tech)
            }]
        
        # 自动推荐技术栈
        recommendations = []
        
        # 获取用户的技术栈负债（需要学习的技术）
        debts = data_service.get_tech_stack_debts(user_id, is_active=True)
        
        # 按优先级排序
        sorted_debts = sorted(debts, key=lambda d: (
            d.learning_priority,
            d.importance_score,
            d.urgency_level == 'critical',
            d.urgency_level == 'high'
        ), reverse=True)
        
        for debt in sorted_debts[:10]:  # 取前10个
            recommendations.append({
                'technology': debt.technology_name,
                'reason': 'debt_repayment',
                'urgency': debt.urgency_level,
                'importance': debt.importance_score,
                'recommended_difficulty': debt.target_proficiency_level
            })
        
        # 获取用户现有资产中需要提升的技术
        assets = data_service.get_tech_stack_assets(user_id, is_active=True)
        
        for asset in assets:
            if asset.proficiency_score < 80:  # 熟练度低于80的可以继续提升
                current_level = asset.proficiency_level
                next_level = self._get_next_difficulty_level(current_level)
                
                if next_level:
                    recommendations.append({
                        'technology': asset.technology_name,
                        'reason': 'skill_improvement',
                        'current_proficiency': asset.proficiency_score,
                        'recommended_difficulty': next_level
                    })
        
        return recommendations
    
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
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """生成技术文章"""
        try:
            # 获取技术相关的主题
            topics = self._get_topics_for_technology(technology, difficulty)
            
            if not topics:
                return None
            
            topic = random.choice(topics)
            
            # 生成文章内容
            article_content = self._create_article_content(technology, topic, difficulty)
            
            return {
                'type': 'article',
                'technology': technology,
                'difficulty': difficulty,
                'title': article_content['title'],
                'content': article_content['content'],
                'estimated_reading_time': article_content['estimated_reading_time'],
                'learning_objectives': article_content['learning_objectives'],
                'code_examples': article_content.get('code_examples', []),
                'created_at': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error generating article for {technology}: {str(e)}")
            return None
    
    def _generate_quiz(
        self, 
        technology: str, 
        difficulty: str, 
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """生成选择题测验"""
        try:
            questions_count = self.config.get('content_generation', {}).get('content_types', {}).get('quiz', {}).get('questions_per_quiz', 5)
            
            questions = []
            
            for i in range(questions_count):
                question = self._create_quiz_question(technology, difficulty)
                if question:
                    questions.append(question)
            
            if not questions:
                return None
            
            return {
                'type': 'quiz',
                'technology': technology,
                'difficulty': difficulty,
                'title': f'{technology} {difficulty.title()} 级测验',
                'description': f'测试你对 {technology} 的理解程度',
                'questions': questions,
                'total_questions': len(questions),
                'estimated_time_minutes': len(questions) * 2,  # 每题2分钟
                'passing_score': 70,
                'created_at': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error generating quiz for {technology}: {str(e)}")
            return None
    
    def _generate_exercise(
        self, 
        technology: str, 
        difficulty: str, 
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """生成编程练习"""
        try:
            exercise_content = self._create_exercise_content(technology, difficulty)
            
            if not exercise_content:
                return None
            
            return {
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
        
        except Exception as e:
            self.logger.error(f"Error generating exercise for {technology}: {str(e)}")
            return None
    
    def _get_topics_for_technology(self, technology: str, difficulty: str) -> List[str]:
        """获取技术相关的主题"""
        tech_key = technology.lower()
        
        if tech_key in self.tech_knowledge_base:
            topics = self.tech_knowledge_base[tech_key].get('topics', {}).get(difficulty, [])
            if topics:
                return topics
        
        # 默认主题
        default_topics = {
            'beginner': ['基础概念', '语法入门', '简单示例'],
            'intermediate': ['核心特性', '最佳实践', '常用模式'],
            'advanced': ['高级特性', '性能优化', '架构设计'],
            'expert': ['内部机制', '扩展开发', '系统设计']
        }
        
        return default_topics.get(difficulty, ['基础概念'])
    
    def _create_article_content(
        self, 
        technology: str, 
        topic: str, 
        difficulty: str
    ) -> Dict[str, Any]:
        """创建文章内容"""
        # 这里可以集成AI生成或使用模板
        title = f"{technology} {difficulty.title()}: {topic}"
        
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
        
        return {
            'title': title,
            'content': content,
            'estimated_reading_time': max(5, len(content) // 200),  # 估算阅读时间
            'learning_objectives': [
                f"理解{topic}的核心概念",
                f"掌握{topic}的基本用法",
                f"能够在实际项目中应用{topic}"
            ],
            'code_examples': code_examples
        }
    
    def _create_quiz_question(
        self, 
        technology: str, 
        difficulty: str
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
        difficulty: str
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