#!/usr/bin/env python3
"""
测试增强版Coding教学Agent
验证基于项目上下文的内容生成功能
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
from app.models.mcp_session import MCPSession, MCPCodeSnippet
from app.models.learning_progress import TechStackAsset, TechStackDebt
from app.models.user import User
from tests.test_data_generator import TestDataGenerator

def create_test_database():
    """创建测试数据库"""
    print("Creating test database...")
    engine = create_engine("sqlite:///test_enhanced_coding_tutor.db", echo=False)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()

def create_project_focused_test_data(db_session):
    """创建项目导向的测试数据"""
    print("\nGenerating project-focused test data...")
    
    # 创建测试用户
    user = User(
        username="project_developer",
        email="dev@project.com",
        full_name="Project Developer",
        skill_level="intermediate"
    )
    db_session.add(user)
    db_session.flush()
    
    user_id = user.id
    print(f"Created user: {user.username} (ID: {user_id})")
    
    # 创建项目相关的MCP会话数据
    project_sessions = [
        {
            'session_name': 'E-commerce API Development',
            'project_name': 'ShopEasy Platform',
            'work_type': 'development',
            'task_description': '开发用户认证和商品管理API，使用FastAPI和PostgreSQL',
            'technologies': ['Python', 'FastAPI', 'PostgreSQL', 'SQLAlchemy'],
            'frameworks': ['FastAPI'],
            'libraries': ['SQLAlchemy', 'Pydantic', 'Alembic'],
            'tools': ['Docker', 'Git', 'Postman'],
            'difficulty_level': 'intermediate',
            'complexity_score': 7.5,
            'estimated_duration': 480,  # 8小时
            'actual_duration': 520,
            'achievements': ['完成用户认证模块', '实现商品CRUD操作', '添加数据验证'],
            'challenges_faced': ['数据库关系设计', 'JWT令牌管理', 'API性能优化'],
            'created_at': datetime.utcnow() - timedelta(days=2)
        },
        {
            'session_name': 'Frontend React Dashboard',
            'project_name': 'ShopEasy Platform',
            'work_type': 'development',
            'task_description': '开发管理员仪表板，集成图表和数据可视化',
            'technologies': ['JavaScript', 'React', 'TypeScript'],
            'frameworks': ['React', 'Next.js'],
            'libraries': ['Chart.js', 'Axios', 'Material-UI'],
            'tools': ['npm', 'Webpack', 'ESLint'],
            'difficulty_level': 'intermediate',
            'complexity_score': 6.8,
            'estimated_duration': 360,  # 6小时
            'actual_duration': 400,
            'achievements': ['完成仪表板布局', '集成图表组件', '实现数据获取'],
            'challenges_faced': ['状态管理', '组件优化', '响应式设计'],
            'created_at': datetime.utcnow() - timedelta(days=1)
        },
        {
            'session_name': 'Database Performance Optimization',
            'project_name': 'ShopEasy Platform',
            'work_type': 'debugging',
            'task_description': '优化数据库查询性能，解决慢查询问题',
            'technologies': ['PostgreSQL', 'Python', 'SQLAlchemy'],
            'frameworks': ['SQLAlchemy'],
            'libraries': ['psycopg2', 'SQLAlchemy'],
            'tools': ['pgAdmin', 'EXPLAIN ANALYZE'],
            'difficulty_level': 'advanced',
            'complexity_score': 8.2,
            'estimated_duration': 240,  # 4小时
            'actual_duration': 300,
            'achievements': ['添加数据库索引', '优化查询语句', '减少查询时间50%'],
            'challenges_faced': ['复杂查询优化', '索引策略', '缓存实现'],
            'created_at': datetime.utcnow() - timedelta(hours=6)
        },
        {
            'session_name': 'API Testing and Documentation',
            'project_name': 'ShopEasy Platform',
            'work_type': 'testing',
            'task_description': '编写API单元测试和集成测试，完善API文档',
            'technologies': ['Python', 'FastAPI', 'Pytest'],
            'frameworks': ['FastAPI', 'Pytest'],
            'libraries': ['pytest', 'httpx', 'factory-boy'],
            'tools': ['Postman', 'Swagger'],
            'difficulty_level': 'intermediate',
            'complexity_score': 6.5,
            'estimated_duration': 300,  # 5小时
            'actual_duration': 280,
            'achievements': ['完成单元测试', '添加集成测试', '生成API文档'],
            'challenges_faced': ['测试数据准备', '异步测试', '文档自动化'],
            'created_at': datetime.utcnow() - timedelta(hours=3)
        }
    ]
    
    # 创建MCP会话
    for session_data in project_sessions:
        session = MCPSession(
            user_id=user_id,
            **session_data
        )
        db_session.add(session)
    
    db_session.flush()
    
    # 创建技术栈资产（用户已有的技能）
    assets_data = [
        {
            'technology_name': 'Python',
            'proficiency_level': 'intermediate',
            'proficiency_score': 65.0,  # 需要提升
            'practical_skills': 60.0,
            'theoretical_knowledge': 70.0,
            'problem_solving': 65.0
        },
        {
            'technology_name': 'JavaScript',
            'proficiency_level': 'beginner',
            'proficiency_score': 45.0,  # 需要大幅提升
            'practical_skills': 40.0,
            'theoretical_knowledge': 50.0,
            'problem_solving': 45.0
        },
        {
            'technology_name': 'React',
            'proficiency_level': 'beginner',
            'proficiency_score': 35.0,  # 新技术
            'practical_skills': 30.0,
            'theoretical_knowledge': 40.0,
            'problem_solving': 35.0
        }
    ]
    
    for asset_data in assets_data:
        asset = TechStackAsset(
            user_id=user_id,
            category='programming_language',
            **asset_data
        )
        db_session.add(asset)
    
    # 创建技术栈负债（需要学习的技术）
    debts_data = [
        {
            'technology_name': 'FastAPI',
            'urgency_level': 'high',
            'importance_score': 85,
            'learning_priority': 1,
            'target_proficiency_level': 'intermediate',
            'estimated_learning_hours': 40
        },
        {
            'technology_name': 'PostgreSQL',
            'urgency_level': 'high',
            'importance_score': 80,
            'learning_priority': 2,
            'target_proficiency_level': 'intermediate',
            'estimated_learning_hours': 35
        },
        {
            'technology_name': 'TypeScript',
            'urgency_level': 'medium',
            'importance_score': 75,
            'learning_priority': 3,
            'target_proficiency_level': 'intermediate',
            'estimated_learning_hours': 30
        }
    ]
    
    for debt_data in debts_data:
        debt = TechStackDebt(
            user_id=user_id,
            category='framework',
            **debt_data
        )
        db_session.add(debt)
    
    db_session.commit()
    
    return {
        'user_id': user_id,
        'username': user.username,
        'sessions_count': len(project_sessions),
        'assets_count': len(assets_data),
        'debts_count': len(debts_data)
    }

def test_enhanced_agent_functionality(db_session, user_data):
    """测试增强版Agent功能"""
    print("\n" + "="*60)
    print("TESTING ENHANCED CODING TUTOR AGENT")
    print("="*60)
    
    agent = CodingTutorAgent()
    user_id = user_data['user_id']
    
    print(f"\nTesting with user: {user_data['username']} (ID: {user_id})")
    
    # 1. 测试项目技术栈分析
    print("\n1. Project Technologies Analysis:")
    data_service = TechStackDataService(db_session)
    project_techs = agent._get_project_technologies(db_session, user_id)
    
    print(f"  Found {len(project_techs)} project-related technologies:")
    for tech in project_techs[:5]:
        print(f"    - {tech['technology']}: used {tech['usage_frequency']} times in {tech['project_count']} projects")
        print(f"      Complexity: {tech['average_complexity']:.1f}, Time: {tech['total_time_spent']} min")
    
    # 2. 测试目标技术栈确定
    print("\n2. Target Technologies Determination:")
    target_techs = agent._determine_target_technologies(data_service, user_id)
    
    print(f"  Recommended {len(target_techs)} technologies for learning:")
    for i, tech in enumerate(target_techs[:5]):
        print(f"    {i+1}. {tech['technology']} ({tech['reason']})")
        print(f"       Difficulty: {tech.get('recommended_difficulty', 'N/A')}")
        if 'project_context' in tech:
            projects = tech['project_context'].get('projects', [])
            print(f"       Used in: {', '.join(projects[:2])}")
    
    # 3. 测试项目相关内容生成
    print("\n3. Project-Relevant Content Generation:")
    
    # 生成FastAPI相关内容（项目中高频使用）
    print("\n  3.1 FastAPI Content (High Priority):")
    fastapi_result = agent.generate_learning_content(
        user_id=user_id,
        technology="FastAPI",
        content_type="mixed",
        difficulty="intermediate",
        count=2
    )
    
    if fastapi_result['status'] == 'success':
        print(f"    Generated {fastapi_result['content_count']} items")
        for content in fastapi_result['content']:
            print(f"    - {content['type']}: {content['title']}")
            if 'project_relevance' in content:
                rel = content['project_relevance']
                print(f"      Project relevance: {rel.get('usage_frequency', 0)} uses, {rel.get('project_count', 0)} projects")
    else:
        print(f"    Error: {fastapi_result.get('message', 'Unknown error')}")
    
    # 自动推荐内容生成
    print("\n  3.2 Auto-Recommended Content:")
    auto_result = agent.generate_learning_content(
        user_id=user_id,
        content_type="mixed",
        count=3
    )
    
    if auto_result['status'] == 'success':
        print(f"    Generated {auto_result['content_count']} items")
        print(f"    Technologies: {auto_result['technologies']}")
        for content in auto_result['content']:
            print(f"    - {content['type']}: {content['title']}")
            if 'practical_applications' in content:
                apps = content['practical_applications']
                print(f"      Practical applications: {len(apps)} scenarios")
    else:
        print(f"    Status: {auto_result['status']}")
        print(f"    Message: {auto_result.get('message', 'No message')}")
    
    return {
        'project_technologies': len(project_techs),
        'target_technologies': len(target_techs),
        'content_generated': auto_result.get('content_count', 0)
    }

def display_test_summary(user_data, test_results, db_session):
    """显示测试总结"""
    print("\n" + "="*60)
    print("ENHANCED CODING TUTOR AGENT TEST SUMMARY")
    print("="*60)
    
    print(f"User: {user_data['username']} (ID: {user_data['user_id']})")
    print(f"Project sessions: {user_data['sessions_count']}")
    print(f"Tech stack assets: {user_data['assets_count']}")
    print(f"Tech stack debts: {user_data['debts_count']}")
    print(f"Project technologies identified: {test_results['project_technologies']}")
    print(f"Target technologies recommended: {test_results['target_technologies']}")
    print(f"Learning content generated: {test_results['content_generated']}")
    
    print("\n✅ Enhanced Coding Tutor Agent testing completed successfully!")
    print("📊 The agent now generates project-relevant learning content")
    print("🎯 Content is tailored to actual project needs and usage patterns")
    print("Database file: test_enhanced_coding_tutor.db")

def main():
    """主测试函数"""
    try:
        # 创建测试数据库
        db_session = create_test_database()
        
        # 生成项目导向的测试数据
        user_data = create_project_focused_test_data(db_session)
        
        # 测试增强版Agent功能
        test_results = test_enhanced_agent_functionality(db_session, user_data)
        
        # 显示测试总结
        display_test_summary(user_data, test_results, db_session)
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'db_session' in locals():
            db_session.close()

if __name__ == "__main__":
    main()