#!/usr/bin/env python3
"""
为前端生成示例学习内容数据
"""

import sys
import os
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Base
from app.services.coding_tutor_agent import CodingTutorAgent
from app.services.tech_stack_data_service import TechStackDataService
from app.models.mcp_session import MCPSession
from app.models.learning_progress import TechStackAsset, TechStackDebt
from app.models.user import User

def create_sample_database():
    """创建示例数据库"""
    print("Creating sample learning content database...")
    engine = create_engine("sqlite:///sample_learning_content.db", echo=False)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()

def create_sample_users_and_projects(db_session):
    """创建示例用户和项目数据"""
    print("\nCreating sample users and project data...")
    
    users_data = [
        {
            'username': 'frontend_dev',
            'email': 'frontend@example.com',
            'full_name': 'Frontend Developer',
            'skill_level': 'intermediate',
            'projects': [
                {
                    'name': 'E-commerce Dashboard',
                    'technologies': ['React', 'TypeScript', 'Material-UI'],
                    'work_types': ['development', 'debugging'],
                    'complexity': 7.0
                },
                {
                    'name': 'Mobile App UI',
                    'technologies': ['React Native', 'JavaScript', 'Redux'],
                    'work_types': ['development', 'testing'],
                    'complexity': 6.5
                }
            ],
            'assets': [
                {'tech': 'React', 'level': 'intermediate', 'score': 75},
                {'tech': 'JavaScript', 'level': 'advanced', 'score': 85},
                {'tech': 'CSS', 'level': 'intermediate', 'score': 70}
            ],
            'debts': [
                {'tech': 'TypeScript', 'urgency': 'high', 'priority': 1},
                {'tech': 'Redux', 'urgency': 'medium', 'priority': 2}
            ]
        },
        {
            'username': 'backend_dev',
            'email': 'backend@example.com',
            'full_name': 'Backend Developer',
            'skill_level': 'advanced',
            'projects': [
                {
                    'name': 'Microservices API',
                    'technologies': ['Python', 'FastAPI', 'PostgreSQL', 'Docker'],
                    'work_types': ['development', 'refactoring'],
                    'complexity': 8.5
                },
                {
                    'name': 'Data Pipeline',
                    'technologies': ['Python', 'Apache Kafka', 'Redis'],
                    'work_types': ['development', 'analysis'],
                    'complexity': 9.0
                }
            ],
            'assets': [
                {'tech': 'Python', 'level': 'expert', 'score': 95},
                {'tech': 'PostgreSQL', 'level': 'advanced', 'score': 80},
                {'tech': 'Docker', 'level': 'intermediate', 'score': 65}
            ],
            'debts': [
                {'tech': 'Kubernetes', 'urgency': 'high', 'priority': 1},
                {'tech': 'Apache Kafka', 'urgency': 'medium', 'priority': 2}
            ]
        },
        {
            'username': 'fullstack_dev',
            'email': 'fullstack@example.com',
            'full_name': 'Full Stack Developer',
            'skill_level': 'intermediate',
            'projects': [
                {
                    'name': 'Social Media Platform',
                    'technologies': ['Vue.js', 'Node.js', 'MongoDB', 'Express'],
                    'work_types': ['development', 'testing', 'debugging'],
                    'complexity': 7.8
                }
            ],
            'assets': [
                {'tech': 'Vue.js', 'level': 'intermediate', 'score': 70},
                {'tech': 'Node.js', 'level': 'intermediate', 'score': 68},
                {'tech': 'MongoDB', 'level': 'beginner', 'score': 45}
            ],
            'debts': [
                {'tech': 'Express', 'urgency': 'medium', 'priority': 1},
                {'tech': 'GraphQL', 'urgency': 'low', 'priority': 3}
            ]
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        # 创建用户
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            full_name=user_data['full_name'],
            skill_level=user_data['skill_level']
        )
        db_session.add(user)
        db_session.flush()
        
        user_id = user.id
        
        # 创建项目会话
        for project in user_data['projects']:
            for i, work_type in enumerate(project['work_types']):
                session = MCPSession(
                    user_id=user_id,
                    session_name=f"{project['name']} - {work_type.title()}",
                    project_name=project['name'],
                    work_type=work_type,
                    task_description=f"{work_type.title()} work on {project['name']} using {', '.join(project['technologies'][:2])}",
                    technologies=project['technologies'],
                    frameworks=[tech for tech in project['technologies'] if tech in ['React', 'Vue.js', 'FastAPI', 'Express']],
                    libraries=[tech for tech in project['technologies'] if tech in ['Material-UI', 'Redux', 'PostgreSQL', 'MongoDB']],
                    tools=['Git', 'VS Code', 'Docker'],
                    difficulty_level='intermediate',
                    complexity_score=project['complexity'],
                    estimated_duration=360,
                    actual_duration=380 + i * 20,
                    created_at=datetime.utcnow() - timedelta(days=i+1)
                )
                db_session.add(session)
        
        # 创建技术栈资产
        for asset_data in user_data['assets']:
            asset = TechStackAsset(
                user_id=user_id,
                technology_name=asset_data['tech'],
                category='programming_language',
                proficiency_level=asset_data['level'],
                proficiency_score=asset_data['score'],
                practical_skills=asset_data['score'] - 5,
                theoretical_knowledge=asset_data['score'] + 5,
                problem_solving=asset_data['score']
            )
            db_session.add(asset)
        
        # 创建技术栈负债
        for debt_data in user_data['debts']:
            debt = TechStackDebt(
                user_id=user_id,
                technology_name=debt_data['tech'],
                category='framework',
                urgency_level=debt_data['urgency'],
                importance_score=90 - debt_data['priority'] * 10,
                learning_priority=debt_data['priority'],
                target_proficiency_level='intermediate',
                estimated_learning_hours=40
            )
            db_session.add(debt)
        
        created_users.append({
            'user_id': user_id,
            'username': user.username,
            'projects': len(user_data['projects']),
            'assets': len(user_data['assets']),
            'debts': len(user_data['debts'])
        })
    
    db_session.commit()
    return created_users

def generate_diverse_learning_content(db_session, users):
    """为每个用户生成多样化的学习内容"""
    print("\nGenerating diverse learning content...")
    
    agent = CodingTutorAgent()
    generated_content = []
    
    # 为每个用户生成不同类型的内容
    content_scenarios = [
        {'type': 'mixed', 'count': 3, 'description': '混合内容'},
        {'type': 'article', 'count': 2, 'description': '技术文章'},
        {'type': 'quiz', 'count': 2, 'description': '选择题测验'},
        {'type': 'exercise', 'count': 1, 'description': '编程练习'}
    ]
    
    technologies = ['React', 'Python', 'JavaScript', 'TypeScript', 'FastAPI', 'Vue.js', 'Node.js', 'PostgreSQL']
    difficulties = ['beginner', 'intermediate', 'advanced']
    
    for user in users:
        user_id = user['user_id']
        username = user['username']
        
        print(f"  Generating content for {username}...")
        
        # 生成自动推荐内容
        auto_result = agent.generate_learning_content(
            user_id=user_id,
            content_type='mixed',
            count=4
        )
        
        if auto_result['status'] == 'success':
            generated_content.extend(auto_result['content'])
            print(f"    Auto-generated: {auto_result['content_count']} items")
        
        # 生成指定技术的内容
        for tech in technologies[:3]:  # 为每个用户生成3个技术的内容
            for difficulty in difficulties[:2]:  # 两个难度级别
                result = agent.generate_learning_content(
                    user_id=user_id,
                    technology=tech,
                    content_type='mixed',
                    difficulty=difficulty,
                    count=2
                )
                
                if result['status'] == 'success':
                    generated_content.extend(result['content'])
    
    print(f"  Total content generated: {len(generated_content)} items")
    return generated_content

def display_content_summary(db_session):
    """显示生成的内容摘要"""
    print("\n" + "="*60)
    print("SAMPLE LEARNING CONTENT SUMMARY")
    print("="*60)
    
    from app.services.learning_content_data_service import LearningContentDataService
    data_service = LearningContentDataService(db_session)
    
    # 统计文章
    articles = data_service.get_learning_articles(limit=1000)
    print(f"\n📚 Articles Generated: {len(articles)}")
    
    article_by_tech = {}
    for article in articles:
        techs = article.target_technologies or ['Unknown']
        for tech in techs:
            article_by_tech[tech] = article_by_tech.get(tech, 0) + 1
    
    for tech, count in sorted(article_by_tech.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {tech}: {count} articles")
    
    # 统计问题
    questions = data_service.get_learning_questions(limit=1000)
    print(f"\n❓ Questions Generated: {len(questions)}")
    
    question_by_tech = {}
    for question in questions:
        techs = question.target_technologies or ['Unknown']
        for tech in techs:
            question_by_tech[tech] = question_by_tech.get(tech, 0) + 1
    
    for tech, count in sorted(question_by_tech.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {tech}: {count} questions")
    
    # 显示示例内容
    print("\n📖 Sample Articles:")
    for article in articles[:3]:
        print(f"  - {article.title}")
        print(f"    Technologies: {article.target_technologies}")
        print(f"    Difficulty: {article.difficulty_level}")
        print(f"    Reading time: {article.estimated_reading_time} min")
    
    print("\n🧩 Sample Quizzes:")
    for question in questions[:3]:
        print(f"  - {question.title}")
        print(f"    Technologies: {question.target_technologies}")
        print(f"    Difficulty: {question.difficulty_level}")
        print(f"    Type: {question.question_type}")
    
    print("\n✅ Sample learning content database created successfully!")
    print("📁 Database file: sample_learning_content.db")
    print("🎯 Ready for frontend integration and testing")

def main():
    """主函数"""
    try:
        # 创建示例数据库
        db_session = create_sample_database()
        
        # 创建示例用户和项目数据
        users = create_sample_users_and_projects(db_session)
        
        # 生成多样化的学习内容
        content = generate_diverse_learning_content(db_session, users)
        
        # 显示内容摘要
        display_content_summary(db_session)
        
    except Exception as e:
        print(f"Error generating sample content: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'db_session' in locals():
            db_session.close()

if __name__ == "__main__":
    main()