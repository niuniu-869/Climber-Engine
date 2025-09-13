#!/usr/bin/env python3
"""
调试Coding教学Agent
"""

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Base
from app.services.coding_tutor_agent import CodingTutorAgent
from app.services.tech_stack_data_service import TechStackDataService
from tests.test_data_generator import TestDataGenerator

def main():
    print("Debug Coding Tutor Agent")
    print("=" * 30)
    
    # 创建数据库
    engine = create_engine("sqlite:///debug_agent.db", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()
    
    try:
        # 生成测试数据
        generator = TestDataGenerator(db_session)
        user_data = generator.generate_complete_test_dataset(
            username="debug_user",
            email="debug@example.com",
            session_count=10,
            asset_count=5,
            debt_count=3
        )
        
        print(f"Created user: {user_data['username']} (ID: {user_data['user_id']})")
        
        # 创建Agent
        agent = CodingTutorAgent()
        data_service = TechStackDataService(db_session)
        
        user_id = user_data['user_id']
        
        # 检查用户的技术栈负债
        print("\n1. User Tech Stack Debts:")
        debts = data_service.get_tech_stack_debts(user_id, is_active=True)
        for debt in debts:
            print(f"  - {debt.technology_name}: {debt.urgency_level} urgency, target: {debt.target_proficiency_level}")
        
        # 检查推荐算法
        print("\n2. Target Technologies Determination:")
        target_techs = agent._determine_target_technologies(data_service, user_id)
        print(f"  Found {len(target_techs)} target technologies:")
        for tech in target_techs:
            print(f"    - {tech['technology']}: {tech['reason']}, difficulty: {tech.get('recommended_difficulty', 'N/A')}")
        
        # 测试指定技术生成
        print("\n3. Testing Specific Technology Generation:")
        if target_techs:
            test_tech = target_techs[0]['technology']
            print(f"  Testing with: {test_tech}")
            
            # 测试文章生成
            print("\n  3.1 Article Generation:")
            article = agent._generate_article(test_tech, 'intermediate', user_id)
            if article:
                print(f"    ✓ Article generated: {article['title']}")
            else:
                print(f"    ✗ Article generation failed")
            
            # 测试问题生成
            print("\n  3.2 Quiz Generation:")
            quiz = agent._generate_quiz(test_tech, 'intermediate', user_id)
            if quiz:
                print(f"    ✓ Quiz generated: {quiz['title']} with {quiz['total_questions']} questions")
                if quiz['questions']:
                    print(f"    Sample question: {quiz['questions'][0]['question']}")
            else:
                print(f"    ✗ Quiz generation failed")
        
        # 测试完整内容生成
        print("\n4. Testing Complete Content Generation:")
        result = agent.generate_learning_content(
            user_id=user_id,
            technology="Java",  # 直接指定一个我们知道存在的技术
            content_type="mixed",
            difficulty="intermediate",
            count=2
        )
        
        print(f"  Status: {result['status']}")
        if result['status'] == 'success':
            print(f"  Generated {result['content_count']} items")
            print(f"  Technologies: {result['technologies']}")
            for i, content in enumerate(result['content']):
                print(f"    {i+1}. {content['type']}: {content['title']}")
        elif result['status'] == 'no_content':
            print(f"  Message: {result['message']}")
        else:
            print(f"  Error: {result.get('message', 'Unknown error')}")
        
        # 测试自动推荐
        print("\n5. Testing Auto Recommendation:")
        auto_result = agent.generate_learning_content(
            user_id=user_id,
            content_type="quiz",
            count=1
        )
        
        print(f"  Status: {auto_result['status']}")
        if auto_result['status'] == 'success':
            print(f"  Auto-selected technologies: {auto_result['technologies']}")
            print(f"  Generated {auto_result['content_count']} items")
        else:
            print(f"  Message: {auto_result.get('message', 'Unknown error')}")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db_session.close()

if __name__ == "__main__":
    main()