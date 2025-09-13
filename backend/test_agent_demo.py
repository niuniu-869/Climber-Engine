#!/usr/bin/env python3
"""
技术栈总结Agent演示和测试脚本
"""

import sys
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Base
from app.services.tech_stack_summary_agent import TechStackSummaryAgent
from app.services.tech_stack_data_service import TechStackDataService
from tests.test_data_generator import TestDataGenerator


def create_test_database():
    """
    创建测试数据库
    """
    print("Creating test database...")
    engine = create_engine("sqlite:///test_agent.db", echo=False)
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def generate_test_data(db_session):
    """
    生成测试数据
    """
    print("Generating test data...")
    generator = TestDataGenerator(db_session)
    
    # 生成多个用户的数据
    users_data = []
    
    for i in range(3):
        user_data = generator.generate_complete_test_dataset(
            username=f"test_user_{i+1}",
            email=f"test_user_{i+1}@example.com",
            session_count=15 + i * 5,  # 不同用户有不同数量的会话
            asset_count=8 + i * 2,
            debt_count=5 + i
        )
        users_data.append(user_data)
        print(f"  Created user {user_data['username']} with {user_data['total_records']} records")
    
    return users_data


def test_agent_functionality(db_session, users_data):
    """
    测试Agent功能
    """
    print("\nTesting Agent functionality...")
    
    # 创建Agent实例
    agent = TechStackSummaryAgent()
    
    # 测试Agent状态
    print("\n1. Agent Status:")
    status = agent.get_analysis_status()
    print(f"  Enabled: {status['enabled']}")
    print(f"  Should run: {status['should_run']}")
    print(f"  Config: {status['config']}")
    
    # 测试单个用户分析
    print("\n2. Single User Analysis:")
    user_id = users_data[0]['user_id']
    
    # 模拟get_db函数
    def mock_get_db():
        yield db_session
    
    # 临时替换get_db
    import app.services.tech_stack_summary_agent as agent_module
    original_get_db = agent_module.get_db
    agent_module.get_db = mock_get_db
    
    try:
        result = agent.run_analysis(user_id=user_id)
        print(f"  Status: {result['status']}")
        print(f"  Analyzed users: {result.get('analyzed_users', 0)}")
        print(f"  Sessions processed: {result.get('total_sessions_processed', 0)}")
        print(f"  Assets updated: {result.get('total_assets_updated', 0)}")
        print(f"  Debts identified: {result.get('total_debts_identified', 0)}")
        
        if 'user_results' in result and result['user_results']:
            user_result = result['user_results'][0]
            print(f"  User {user_result['user_id']} details:")
            print(f"    Sessions: {user_result['sessions_processed']}")
            print(f"    Assets updated: {user_result['assets_updated']}")
            print(f"    Debts identified: {user_result['debts_identified']}")
            print(f"    Technologies analyzed: {user_result['technologies_analyzed']}")
    
    except Exception as e:
        print(f"  Error during analysis: {e}")
    
    finally:
        # 恢复原始get_db
        agent_module.get_db = original_get_db
    
    # 测试全用户分析
    print("\n3. All Users Analysis:")
    agent_module.get_db = mock_get_db
    
    try:
        result = agent.run_analysis()  # 不指定用户ID
        print(f"  Status: {result['status']}")
        print(f"  Analyzed users: {result.get('analyzed_users', 0)}")
        print(f"  Total sessions processed: {result.get('total_sessions_processed', 0)}")
        print(f"  Total assets updated: {result.get('total_assets_updated', 0)}")
        print(f"  Total debts identified: {result.get('total_debts_identified', 0)}")
    
    except Exception as e:
        print(f"  Error during analysis: {e}")
    
    finally:
        agent_module.get_db = original_get_db


def test_data_service(db_session, users_data):
    """
    测试数据服务
    """
    print("\n4. Data Service Testing:")
    
    data_service = TechStackDataService(db_session)
    user_id = users_data[0]['user_id']
    
    # 测试MCP会话统计
    print("\n  MCP Session Statistics:")
    stats = data_service.get_mcp_session_statistics(user_id)
    print(f"    Total sessions: {stats['total_sessions']}")
    print(f"    Total duration: {stats['total_duration_hours']:.2f} hours")
    print(f"    Average quality: {stats['average_quality_score']:.2f}")
    print(f"    Technologies used: {len(stats['technologies_used'])}")
    print(f"    Projects: {len(stats['projects_worked_on'])}")
    
    # 测试技术栈资产
    print("\n  Tech Stack Assets:")
    assets = data_service.get_tech_stack_assets(user_id)
    print(f"    Total assets: {len(assets)}")
    
    if assets:
        print("    Top 3 assets:")
        for i, asset in enumerate(assets[:3]):
            print(f"      {i+1}. {asset.technology_name} ({asset.category}) - {asset.proficiency_score:.1f}")
    
    # 测试技术栈负债
    print("\n  Tech Stack Debts:")
    debts = data_service.get_tech_stack_debts(user_id, is_active=True)
    print(f"    Total active debts: {len(debts)}")
    
    if debts:
        print("    Top 3 debts:")
        for i, debt in enumerate(debts[:3]):
            print(f"      {i+1}. {debt.technology_name} ({debt.urgency_level}) - {debt.importance_score:.1f}")
    
    # 测试资产统计
    print("\n  Asset Statistics:")
    asset_stats = data_service.get_tech_stack_asset_statistics(user_id)
    print(f"    Total assets: {asset_stats['total_assets']}")
    print(f"    Active assets: {asset_stats['active_assets']}")
    print(f"    Average proficiency: {asset_stats['average_proficiency']:.2f}")
    print(f"    Categories: {list(asset_stats['category_distribution'].keys())}")


def test_technology_analysis(db_session, users_data):
    """
    测试技术栈分析功能
    """
    print("\n5. Technology Analysis Testing:")
    
    agent = TechStackSummaryAgent()
    data_service = TechStackDataService(db_session)
    user_id = users_data[0]['user_id']
    
    # 获取用户的MCP会话
    sessions = data_service.get_recent_mcp_sessions(user_id=user_id, limit=10)
    print(f"\n  Analyzing {len(sessions)} sessions...")
    
    if sessions:
        # 分析技术栈使用情况
        tech_usage = agent._analyze_technology_usage(sessions)
        print(f"  Found {len(tech_usage)} technologies:")
        
        # 显示前5个技术栈
        sorted_techs = sorted(
            tech_usage.items(), 
            key=lambda x: x[1]['usage_count'], 
            reverse=True
        )
        
        for i, (tech_key, usage) in enumerate(sorted_techs[:5]):
            print(f"    {i+1}. {usage['name']} ({usage['category']})")
            print(f"       Usage count: {usage['usage_count']}")
            print(f"       Avg duration: {usage.get('avg_duration', 0):.1f} min")
            print(f"       Avg complexity: {usage.get('avg_complexity', 0):.1f}")
            print(f"       Avg quality: {usage.get('avg_quality', 0):.1f}")
            print(f"       Projects: {usage.get('project_count', 0)}")


def display_summary(users_data):
    """
    显示测试总结
    """
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total_sessions = sum(data['sessions_created'] for data in users_data)
    total_assets = sum(data['assets_created'] for data in users_data)
    total_debts = sum(data['debts_created'] for data in users_data)
    total_snippets = sum(data['snippets_created'] for data in users_data)
    
    print(f"Users created: {len(users_data)}")
    print(f"Total MCP sessions: {total_sessions}")
    print(f"Total code snippets: {total_snippets}")
    print(f"Total tech assets: {total_assets}")
    print(f"Total tech debts: {total_debts}")
    print(f"Total records: {sum(data['total_records'] for data in users_data)}")
    
    print("\nUser details:")
    for data in users_data:
        print(f"  {data['username']} (ID: {data['user_id']}):")
        print(f"    Sessions: {data['sessions_created']}")
        print(f"    Assets: {data['assets_created']}")
        print(f"    Debts: {data['debts_created']}")
    
    print("\nAgent testing completed successfully!")
    print("Database file: test_agent.db")


def main():
    """
    主函数
    """
    print("Tech Stack Summary Agent Demo")
    print("=" * 40)
    
    try:
        # 创建数据库
        db_session = create_test_database()
        
        # 生成测试数据
        users_data = generate_test_data(db_session)
        
        # 测试Agent功能
        test_agent_functionality(db_session, users_data)
        
        # 测试数据服务
        test_data_service(db_session, users_data)
        
        # 测试技术栈分析
        test_technology_analysis(db_session, users_data)
        
        # 显示总结
        display_summary(users_data)
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'db_session' in locals():
            db_session.close()


if __name__ == "__main__":
    main()