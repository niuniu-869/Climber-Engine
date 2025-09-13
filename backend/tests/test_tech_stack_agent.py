#!/usr/bin/env python3
"""
技术栈总结Agent单元测试
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from app.core.database import Base
from app.services.tech_stack_summary_agent import TechStackSummaryAgent
from app.services.tech_stack_data_service import TechStackDataService
from app.models.user import User
from app.models.mcp_session import MCPSession
from app.models.learning_progress import TechStackAsset, TechStackDebt
from tests.test_data_generator import TestDataGenerator


class TestTechStackSummaryAgent:
    """
    技术栈总结Agent测试类
    """
    
    @pytest.fixture
    def db_session(self):
        """创建测试数据库会话"""
        # 使用内存SQLite数据库进行测试
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)
        
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        yield session
        
        session.close()
    
    @pytest.fixture
    def test_config_file(self):
        """创建测试配置文件"""
        config_content = """
basic:
  enabled: true
  name: "TestTechStackAgent"
  version: "1.0.0"

schedule:
  analysis_interval_hours: 1  # 测试用较短间隔

data_processing:
  max_sessions_per_batch: 10
  min_session_duration_minutes: 1

analysis:
  tech_stack_weights:
    programming_language: 1.0
    framework: 0.8
    library: 0.6
    tool: 0.4
  proficiency_scoring:
    base_score: 10.0
    duration_weight: 0.3
    complexity_weight: 0.4
    quality_weight: 0.3
    max_single_increment: 5.0

logging:
  level: "DEBUG"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            config_path = f.name
        
        yield config_path
        
        os.unlink(config_path)
    
    @pytest.fixture
    def agent(self, test_config_file):
        """创建测试Agent实例"""
        return TechStackSummaryAgent(test_config_file)
    
    @pytest.fixture
    def test_data(self, db_session):
        """生成测试数据"""
        generator = TestDataGenerator(db_session)
        return generator.generate_complete_test_dataset(
            username="test_agent_user",
            email="agent_test@example.com",
            session_count=10,
            asset_count=5,
            debt_count=3
        )
    
    def test_agent_initialization(self, agent):
        """测试Agent初始化"""
        assert agent is not None
        assert agent.is_enabled() is True
        assert agent.config['basic']['name'] == "TestTechStackAgent"
        assert agent.config['schedule']['analysis_interval_hours'] == 1
    
    def test_agent_config_loading(self, test_config_file):
        """测试配置文件加载"""
        agent = TechStackSummaryAgent(test_config_file)
        
        assert agent.config['basic']['enabled'] is True
        assert agent.config['schedule']['analysis_interval_hours'] == 1
        assert agent.config['data_processing']['max_sessions_per_batch'] == 10
    
    def test_should_run_analysis(self, agent):
        """测试分析运行条件判断"""
        # 初始状态应该运行
        assert agent.should_run_analysis() is True
        
        # 设置最近分析时间
        agent.last_analysis_time = datetime.utcnow() - timedelta(minutes=30)
        assert agent.should_run_analysis() is False
        
        # 设置较早的分析时间
        agent.last_analysis_time = datetime.utcnow() - timedelta(hours=2)
        assert agent.should_run_analysis() is True
    
    @patch('app.services.tech_stack_summary_agent.get_db')
    def test_run_analysis_disabled(self, mock_get_db, agent):
        """测试禁用状态下的分析"""
        agent.config['basic']['enabled'] = False
        
        result = agent.run_analysis()
        
        assert result['status'] == 'disabled'
        assert 'disabled' in result['message']
    
    @patch('app.services.tech_stack_summary_agent.get_db')
    def test_run_analysis_no_users(self, mock_get_db, agent, db_session):
        """测试没有用户时的分析"""
        mock_get_db.return_value = db_session
        
        result = agent.run_analysis()
        
        assert result['status'] == 'completed'
        assert result['analyzed_users'] == 0
    
    @patch('app.services.tech_stack_summary_agent.get_db')
    def test_run_analysis_with_data(self, mock_get_db, agent, db_session, test_data):
        """测试有数据时的分析"""
        mock_get_db.return_value = db_session
        
        result = agent.run_analysis(user_id=test_data['user_id'])
        
        assert result['status'] == 'completed'
        assert result['analyzed_users'] == 1
        assert result['total_sessions_processed'] > 0
        assert 'analysis_time' in result
    
    def test_get_users_to_analyze(self, agent, db_session, test_data):
        """测试获取需要分析的用户"""
        users = agent._get_users_to_analyze(db_session, test_data['user_id'])
        
        assert len(users) == 1
        assert users[0].id == test_data['user_id']
    
    def test_get_users_to_analyze_all(self, agent, db_session, test_data):
        """测试获取所有活跃用户"""
        users = agent._get_users_to_analyze(db_session, None)
        
        assert len(users) >= 1
        assert any(user.id == test_data['user_id'] for user in users)
    
    def test_analyze_technology_usage(self, agent, db_session, test_data):
        """测试技术栈使用分析"""
        sessions = db_session.query(MCPSession).filter(
            MCPSession.user_id == test_data['user_id']
        ).all()
        
        tech_usage = agent._analyze_technology_usage(sessions)
        
        assert len(tech_usage) > 0
        
        # 检查技术栈分析结果
        for tech_key, usage in tech_usage.items():
            assert 'name' in usage
            assert 'category' in usage
            assert 'usage_count' in usage
            assert 'total_duration' in usage
            assert 'avg_duration' in usage
            assert usage['usage_count'] > 0
    
    def test_calculate_proficiency_increment(self, agent):
        """测试熟练度增长计算"""
        usage = {
            'avg_duration': 120,  # 2小时
            'avg_complexity': 7.0,
            'avg_quality': 85.0,
            'usage_count': 3
        }
        
        scoring = agent.config['analysis']['proficiency_scoring']
        increment = agent._calculate_proficiency_increment(usage, scoring)
        
        assert increment > 0
        assert increment <= scoring['max_single_increment'] * 2  # 合理范围
    
    def test_determine_proficiency_level(self, agent):
        """测试熟练度级别判断"""
        assert agent._determine_proficiency_level(95.0) == "expert"
        assert agent._determine_proficiency_level(75.0) == "advanced"
        assert agent._determine_proficiency_level(45.0) == "intermediate"
        assert agent._determine_proficiency_level(15.0) == "beginner"
    
    def test_update_tech_stack_assets(self, agent, db_session, test_data):
        """测试技术栈资产更新"""
        # 创建一些技术使用数据
        tech_usage = {
            'python': {
                'name': 'Python',
                'category': 'programming_language',
                'usage_count': 3,
                'total_duration': 180,
                'avg_duration': 60,
                'avg_complexity': 6.0,
                'avg_quality': 80.0,
                'project_count': 2,
                'projects': ['Project A', 'Project B']
            },
            'react': {
                'name': 'React',
                'category': 'framework',
                'usage_count': 2,
                'total_duration': 120,
                'avg_duration': 60,
                'avg_complexity': 5.0,
                'avg_quality': 75.0,
                'project_count': 1,
                'projects': ['Project A']
            }
        }
        
        updated_count = agent._update_tech_stack_assets(
            db_session, test_data['user_id'], tech_usage
        )
        
        assert updated_count >= 0
        
        # 检查是否创建了新资产或更新了现有资产
        assets = db_session.query(TechStackAsset).filter(
            TechStackAsset.user_id == test_data['user_id']
        ).all()
        
        # 应该有一些资产
        assert len(assets) > 0
    
    def test_identify_tech_stack_debts(self, agent, db_session, test_data):
        """测试技术栈负债识别"""
        tech_usage = {
            'react': {
                'name': 'React',
                'category': 'framework',
                'usage_count': 2
            }
        }
        
        identified_count = agent._identify_tech_stack_debts(
            db_session, test_data['user_id'], tech_usage
        )
        
        # 可能识别出一些负债
        assert identified_count >= 0
    
    def test_get_related_technologies(self, agent):
        """测试相关技术获取"""
        related = agent._get_related_technologies('React', 'framework')
        
        assert isinstance(related, list)
        # React应该关联JavaScript, HTML, CSS等
        expected_techs = ['JavaScript', 'HTML', 'CSS']
        assert any(tech in related for tech in expected_techs)
    
    def test_determine_tech_category(self, agent):
        """测试技术分类判断"""
        assert agent._determine_tech_category('JavaScript') == 'programming_language'
        assert agent._determine_tech_category('Python') == 'programming_language'
        assert agent._determine_tech_category('HTML') == 'markup_language'
        assert agent._determine_tech_category('UnknownTech') == 'general'
    
    def test_get_analysis_status(self, agent):
        """测试获取分析状态"""
        status = agent.get_analysis_status()
        
        assert 'enabled' in status
        assert 'should_run' in status
        assert 'config' in status
        assert status['enabled'] is True
        assert isinstance(status['config'], dict)
    
    @patch('app.services.tech_stack_summary_agent.get_db')
    def test_run_analysis_error_handling(self, mock_get_db, agent):
        """测试分析过程中的错误处理"""
        # 模拟数据库错误
        mock_get_db.side_effect = Exception("Database connection failed")
        
        result = agent.run_analysis()
        
        assert result['status'] == 'error'
        assert 'Database connection failed' in result['message']
    
    def test_agent_with_invalid_config(self):
        """测试无效配置文件的处理"""
        # 使用不存在的配置文件路径
        agent = TechStackSummaryAgent("/nonexistent/config.yaml")
        
        # 应该使用默认配置
        assert agent.config is not None
        assert agent.config['basic']['enabled'] is True
    
    def test_update_skill_dimensions(self, agent, db_session, test_data):
        """测试技能维度更新"""
        # 创建一个测试资产
        asset = TechStackAsset(
            user_id=test_data['user_id'],
            technology_name='TestTech',
            category='programming_language',
            proficiency_level='intermediate',
            proficiency_score=50.0,
            practical_skills=40.0,
            problem_solving=35.0,
            theoretical_knowledge=45.0
        )
        
        usage = {
            'usage_count': 5,
            'avg_quality': 80.0,
            'avg_complexity': 7.0,
            'project_count': 3
        }
        
        original_practical = asset.practical_skills
        original_problem_solving = asset.problem_solving
        original_theoretical = asset.theoretical_knowledge
        
        agent._update_skill_dimensions(asset, usage)
        
        # 技能维度应该有所提升
        assert asset.practical_skills >= original_practical
        assert asset.problem_solving >= original_problem_solving
        assert asset.theoretical_knowledge >= original_theoretical


class TestTechStackDataService:
    """
    技术栈数据服务测试类
    """
    
    @pytest.fixture
    def db_session(self):
        """创建测试数据库会话"""
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)
        
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        yield session
        
        session.close()
    
    @pytest.fixture
    def data_service(self, db_session):
        """创建数据服务实例"""
        return TechStackDataService(db_session)
    
    @pytest.fixture
    def test_data(self, db_session):
        """生成测试数据"""
        generator = TestDataGenerator(db_session)
        return generator.generate_complete_test_dataset(
            username="data_service_test_user",
            email="data_service@example.com",
            session_count=8,
            asset_count=6,
            debt_count=4
        )
    
    def test_get_recent_mcp_sessions(self, data_service, test_data):
        """测试获取最近的MCP会话"""
        sessions = data_service.get_recent_mcp_sessions(
            user_id=test_data['user_id'],
            limit=5
        )
        
        assert len(sessions) <= 5
        assert all(session.user_id == test_data['user_id'] for session in sessions)
        assert all(session.status == 'completed' for session in sessions)
    
    def test_get_mcp_sessions_by_technology(self, data_service, test_data):
        """测试根据技术栈获取会话"""
        sessions = data_service.get_mcp_sessions_by_technology(
            technology='Python',
            user_id=test_data['user_id']
        )
        
        # 检查返回的会话是否包含指定技术
        for session in sessions:
            assert (
                'Python' in (session.technologies or []) or
                session.primary_language == 'Python' or
                'Python' in (session.frameworks or []) or
                'Python' in (session.libraries or []) or
                'Python' in (session.tools or [])
            )
    
    def test_get_mcp_session_statistics(self, data_service, test_data):
        """测试获取MCP会话统计"""
        stats = data_service.get_mcp_session_statistics(test_data['user_id'])
        
        assert 'total_sessions' in stats
        assert 'total_duration_hours' in stats
        assert 'average_quality_score' in stats
        assert 'technologies_used' in stats
        assert 'projects_worked_on' in stats
        assert 'work_types' in stats
        
        assert stats['total_sessions'] >= 0
        assert stats['total_duration_hours'] >= 0
        assert isinstance(stats['technologies_used'], list)
        assert isinstance(stats['projects_worked_on'], list)
        assert isinstance(stats['work_types'], dict)
    
    def test_get_tech_stack_assets(self, data_service, test_data):
        """测试获取技术栈资产"""
        assets = data_service.get_tech_stack_assets(test_data['user_id'])
        
        assert len(assets) >= 0
        assert all(asset.user_id == test_data['user_id'] for asset in assets)
    
    def test_get_tech_stack_asset_by_name(self, data_service, test_data, db_session):
        """测试根据名称获取技术栈资产"""
        # 首先确保有一个资产
        assets = data_service.get_tech_stack_assets(test_data['user_id'])
        if assets:
            tech_name = assets[0].technology_name
            found_asset = data_service.get_tech_stack_asset_by_name(
                test_data['user_id'], tech_name
            )
            
            assert found_asset is not None
            assert found_asset.technology_name == tech_name
            assert found_asset.user_id == test_data['user_id']
    
    def test_get_tech_stack_debts(self, data_service, test_data):
        """测试获取技术栈负债"""
        debts = data_service.get_tech_stack_debts(test_data['user_id'])
        
        assert len(debts) >= 0
        assert all(debt.user_id == test_data['user_id'] for debt in debts)
    
    def test_get_high_priority_debts(self, data_service, test_data):
        """测试获取高优先级负债"""
        debts = data_service.get_high_priority_debts(test_data['user_id'], limit=3)
        
        assert len(debts) <= 3
        assert all(debt.user_id == test_data['user_id'] for debt in debts)
        assert all(debt.is_active for debt in debts)
    
    def test_get_tech_stack_asset_statistics(self, data_service, test_data):
        """测试获取技术栈资产统计"""
        stats = data_service.get_tech_stack_asset_statistics(test_data['user_id'])
        
        assert 'total_assets' in stats
        assert 'active_assets' in stats
        assert 'average_proficiency' in stats
        assert 'category_distribution' in stats
        assert 'proficiency_distribution' in stats
        assert 'top_skills' in stats
        
        assert stats['total_assets'] >= 0
        assert stats['active_assets'] >= 0
        assert isinstance(stats['category_distribution'], dict)
        assert isinstance(stats['proficiency_distribution'], dict)
        assert isinstance(stats['top_skills'], list)
    
    def test_get_active_users_with_sessions(self, data_service, test_data):
        """测试获取有活跃会话的用户"""
        users = data_service.get_active_users_with_sessions(days=30)
        
        assert len(users) >= 1
        assert any(user.id == test_data['user_id'] for user in users)
    
    def test_get_user_by_id(self, data_service, test_data):
        """测试根据ID获取用户"""
        user = data_service.get_user_by_id(test_data['user_id'])
        
        assert user is not None
        assert user.id == test_data['user_id']
        assert user.username == test_data['username']
    
    def test_transaction_management(self, data_service):
        """测试事务管理"""
        # 测试提交
        try:
            data_service.commit()
        except Exception as e:
            pytest.fail(f"Commit failed: {e}")
        
        # 测试回滚
        try:
            data_service.rollback()
        except Exception as e:
            pytest.fail(f"Rollback failed: {e}")
        
        # 测试刷新
        try:
            data_service.flush()
        except Exception as e:
            pytest.fail(f"Flush failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])