#!/usr/bin/env python3
"""
测试数据生成器
用于生成技术栈总结Agent的测试数据
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.mcp_session import MCPSession, MCPCodeSnippet
from app.models.learning_progress import TechStackAsset, TechStackDebt


class TestDataGenerator:
    """
    测试数据生成器
    
    生成用于测试技术栈总结Agent的模拟数据
    """
    
    def __init__(self, db: Session):
        self.db = db
        
        # 技术栈数据
        self.technologies = {
            'programming_language': ['Python', 'JavaScript', 'Java', 'TypeScript', 'Go', 'Rust'],
            'framework': ['React', 'Vue.js', 'Django', 'Flask', 'Spring Boot', 'Express.js', 'FastAPI'],
            'library': ['NumPy', 'Pandas', 'Lodash', 'Axios', 'SQLAlchemy', 'Pydantic'],
            'tool': ['Docker', 'Git', 'VS Code', 'Postman', 'Jenkins', 'Kubernetes'],
            'database': ['PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'SQLite']
        }
        
        self.work_types = ['development', 'debugging', 'refactoring', 'testing', 'documentation', 'analysis']
        self.difficulty_levels = ['beginner', 'intermediate', 'advanced', 'expert']
        self.project_names = [
            'E-commerce Platform', 'Blog System', 'Task Manager', 'Chat Application',
            'Data Analytics Dashboard', 'API Gateway', 'Mobile App Backend', 'ML Pipeline'
        ]
    
    def create_test_user(self, username: str = "test_user", email: str = "test@example.com") -> User:
        """
        创建测试用户
        
        Args:
            username: 用户名
            email: 邮箱
        
        Returns:
            创建的用户对象
        """
        # 检查用户是否已存在
        existing_user = self.db.query(User).filter(User.email == email).first()
        if existing_user:
            return existing_user
        
        user = User(
            username=username,
            email=email,
            full_name=f"Test User - {username}",
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        self.db.add(user)
        self.db.flush()
        return user
    
    def generate_mcp_sessions(
        self, 
        user_id: int, 
        count: int = 20,
        days_back: int = 30
    ) -> List[MCPSession]:
        """
        生成MCP会话数据
        
        Args:
            user_id: 用户ID
            count: 生成数量
            days_back: 回溯天数
        
        Returns:
            生成的MCP会话列表
        """
        sessions = []
        
        for i in range(count):
            # 随机时间
            created_time = datetime.utcnow() - timedelta(
                days=random.randint(0, days_back),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # 随机选择技术栈
            primary_language = random.choice(self.technologies['programming_language'])
            frameworks = random.sample(self.technologies['framework'], random.randint(0, 2))
            libraries = random.sample(self.technologies['library'], random.randint(0, 3))
            tools = random.sample(self.technologies['tool'], random.randint(1, 3))
            
            # 合并所有技术
            all_technologies = [primary_language] + frameworks + libraries + tools
            
            # 随机会话属性
            work_type = random.choice(self.work_types)
            difficulty_level = random.choice(self.difficulty_levels)
            project_name = random.choice(self.project_names)
            
            # 基于难度级别调整各种分数
            difficulty_multiplier = {
                'beginner': 0.5,
                'intermediate': 0.7,
                'advanced': 0.85,
                'expert': 1.0
            }[difficulty_level]
            
            session = MCPSession(
                user_id=user_id,
                session_name=f"Session {i+1}: {work_type.title()} on {project_name}",
                project_name=project_name,
                work_type=work_type,
                task_description=f"Working on {work_type} tasks for {project_name} using {primary_language}",
                technologies=all_technologies,
                primary_language=primary_language,
                frameworks=frameworks,
                libraries=libraries,
                tools=tools,
                difficulty_level=difficulty_level,
                complexity_score=random.uniform(3.0, 9.0) * difficulty_multiplier,
                estimated_duration=random.randint(30, 240),
                actual_duration=random.randint(20, 300),
                files_modified=random.randint(1, 15),
                lines_added=random.randint(10, 500),
                lines_deleted=random.randint(0, 200),
                commits_count=random.randint(1, 8),
                code_quality_score=random.uniform(60.0, 95.0) * difficulty_multiplier,
                test_coverage=random.uniform(40.0, 90.0),
                documentation_quality=random.uniform(50.0, 85.0),
                mcp_call_count=random.randint(5, 50),
                status='completed',
                is_successful=random.choice([True, True, True, False]),  # 75% 成功率
                started_at=created_time,
                ended_at=created_time + timedelta(minutes=random.randint(20, 300)),
                created_at=created_time,
                updated_at=created_time
            )
            
            # 添加一些成就和挑战
            if session.is_successful:
                session.achievements = self._generate_achievements(work_type, difficulty_level)
                session.lessons_learned = self._generate_lessons_learned(all_technologies)
            else:
                session.challenges_faced = self._generate_challenges(work_type, difficulty_level)
            
            session.solutions_applied = self._generate_solutions(all_technologies)
            
            sessions.append(session)
            self.db.add(session)
        
        self.db.flush()
        return sessions
    
    def generate_code_snippets(
        self, 
        sessions: List[MCPSession], 
        snippets_per_session: int = 3
    ) -> List[MCPCodeSnippet]:
        """
        为MCP会话生成代码片段
        
        Args:
            sessions: MCP会话列表
            snippets_per_session: 每个会话的代码片段数量
        
        Returns:
            生成的代码片段列表
        """
        snippets = []
        
        for session in sessions:
            for i in range(random.randint(1, snippets_per_session)):
                snippet = MCPCodeSnippet(
                    mcp_session_id=session.id,
                    title=f"Code snippet {i+1} for {session.primary_language}",
                    description=f"Example {session.primary_language} code from {session.work_type} work",
                    file_path=f"/src/{session.project_name.lower().replace(' ', '_')}/main.{self._get_file_extension(session.primary_language)}",
                    file_name=f"main.{self._get_file_extension(session.primary_language)}",
                    code_content=self._generate_code_content(session.primary_language, session.work_type),
                    language=session.primary_language,
                    framework=random.choice(session.frameworks) if session.frameworks else None,
                    snippet_type=random.choice(['function', 'class', 'module', 'config']),
                    purpose=f"Demonstrates {session.work_type} patterns",
                    complexity_level=random.choice(['simple', 'medium', 'complex']),
                    related_technologies=session.technologies[:3],
                    concepts_demonstrated=self._generate_concepts(session.primary_language),
                    quality_score=random.uniform(60.0, 95.0),
                    readability_score=random.uniform(70.0, 95.0),
                    maintainability_score=random.uniform(65.0, 90.0),
                    learning_value=random.uniform(60.0, 90.0),
                    difficulty_rating=random.randint(2, 5),
                    educational_notes=f"This snippet shows how to implement {session.work_type} in {session.primary_language}",
                    created_at=session.created_at
                )
                
                snippets.append(snippet)
                self.db.add(snippet)
        
        self.db.flush()
        return snippets
    
    def generate_existing_assets(
        self, 
        user_id: int, 
        count: int = 10
    ) -> List[TechStackAsset]:
        """
        生成现有的技术栈资产
        
        Args:
            user_id: 用户ID
            count: 生成数量
        
        Returns:
            生成的技术栈资产列表
        """
        assets = []
        used_techs = set()
        
        for category, tech_list in self.technologies.items():
            # 每个分类选择一些技术作为已掌握的
            selected_count = min(random.randint(1, 3), len(tech_list))
            selected_techs = random.sample(tech_list, selected_count)
            
            for tech in selected_techs:
                if tech in used_techs:
                    continue
                used_techs.add(tech)
                
                proficiency_score = random.uniform(30.0, 95.0)
                proficiency_level = self._score_to_level(proficiency_score)
                
                asset = TechStackAsset(
                    user_id=user_id,
                    technology_name=tech,
                    category=category,
                    proficiency_level=proficiency_level,
                    proficiency_score=proficiency_score,
                    confidence_level=min(1.0, proficiency_score / 100.0),
                    first_learned_date=datetime.utcnow() - timedelta(days=random.randint(30, 365)),
                    last_practiced_date=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                    total_practice_hours=random.uniform(10.0, 200.0),
                    project_count=random.randint(1, 10),
                    theoretical_knowledge=random.uniform(40.0, 90.0),
                    practical_skills=random.uniform(50.0, 95.0),
                    problem_solving=random.uniform(45.0, 85.0),
                    best_practices=random.uniform(40.0, 80.0),
                    advanced_features=random.uniform(20.0, 70.0),
                    market_demand=random.uniform(60.0, 95.0),
                    salary_impact=random.uniform(50.0, 90.0),
                    career_relevance=random.uniform(70.0, 95.0),
                    is_active=random.choice([True, True, True, False]),  # 75% 活跃
                    created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365))
                )
                
                assets.append(asset)
                self.db.add(asset)
                
                if len(assets) >= count:
                    break
            
            if len(assets) >= count:
                break
        
        self.db.flush()
        return assets
    
    def generate_tech_debts(
        self, 
        user_id: int, 
        count: int = 8
    ) -> List[TechStackDebt]:
        """
        生成技术栈负债
        
        Args:
            user_id: 用户ID
            count: 生成数量
        
        Returns:
            生成的技术栈负债列表
        """
        debts = []
        
        # 获取用户已有的资产，避免重复
        existing_assets = self.db.query(TechStackAsset).filter(
            TechStackAsset.user_id == user_id
        ).all()
        existing_tech_names = {asset.technology_name.lower() for asset in existing_assets}
        
        # 从所有技术中选择一些作为负债
        all_techs = []
        for tech_list in self.technologies.values():
            all_techs.extend(tech_list)
        
        available_techs = [tech for tech in all_techs if tech.lower() not in existing_tech_names]
        
        if len(available_techs) < count:
            # 如果可用技术不够，添加一些新的
            additional_techs = ['Kubernetes', 'GraphQL', 'Redis', 'Elasticsearch', 'TensorFlow', 'PyTorch']
            available_techs.extend([tech for tech in additional_techs if tech.lower() not in existing_tech_names])
        
        selected_techs = random.sample(available_techs, min(count, len(available_techs)))
        
        for tech in selected_techs:
            category = self._determine_tech_category(tech)
            urgency_level = random.choice(['low', 'medium', 'high', 'critical'])
            
            debt = TechStackDebt(
                user_id=user_id,
                technology_name=tech,
                category=category,
                urgency_level=urgency_level,
                importance_score=random.uniform(50.0, 95.0),
                career_impact=random.uniform(60.0, 90.0),
                project_relevance=random.uniform(40.0, 85.0),
                target_proficiency_level=random.choice(['intermediate', 'advanced']),
                estimated_learning_hours=random.uniform(20.0, 100.0),
                learning_priority=random.randint(2, 5),
                planned_start_date=datetime.utcnow() + timedelta(days=random.randint(1, 30)),
                target_completion_date=datetime.utcnow() + timedelta(days=random.randint(30, 180)),
                learning_progress=random.uniform(0.0, 30.0),  # 大部分还没开始学习
                time_invested=random.uniform(0.0, 10.0),
                status=random.choice(['identified', 'planned', 'learning']),
                is_active=True,
                auto_generated=random.choice([True, False]),
                market_demand=random.uniform(70.0, 95.0),
                salary_potential=random.uniform(60.0, 90.0),
                job_opportunities=random.uniform(65.0, 85.0),
                learning_motivation=f"Need to learn {tech} for career advancement and project requirements",
                identified_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            
            debts.append(debt)
            self.db.add(debt)
        
        self.db.flush()
        return debts
    
    def _generate_achievements(self, work_type: str, difficulty_level: str) -> List[str]:
        """生成成就列表"""
        base_achievements = {
            'development': ['Implemented new feature', 'Optimized performance', 'Added unit tests'],
            'debugging': ['Fixed critical bug', 'Improved error handling', 'Enhanced logging'],
            'refactoring': ['Improved code structure', 'Reduced complexity', 'Enhanced maintainability'],
            'testing': ['Increased test coverage', 'Added integration tests', 'Automated testing'],
            'documentation': ['Updated API docs', 'Added code comments', 'Created user guide'],
            'analysis': ['Identified bottlenecks', 'Analyzed user behavior', 'Generated insights']
        }
        
        achievements = base_achievements.get(work_type, ['Completed task successfully'])
        return random.sample(achievements, random.randint(1, len(achievements)))
    
    def _generate_lessons_learned(self, technologies: List[str]) -> List[str]:
        """生成学习经验"""
        lessons = [
            f"Better understanding of {random.choice(technologies)} best practices",
            "Improved debugging techniques",
            "Learned new design patterns",
            "Enhanced problem-solving skills",
            "Better code organization strategies"
        ]
        return random.sample(lessons, random.randint(1, 3))
    
    def _generate_challenges(self, work_type: str, difficulty_level: str) -> List[str]:
        """生成挑战列表"""
        challenges = [
            "Complex algorithm implementation",
            "Integration with third-party APIs",
            "Performance optimization issues",
            "Debugging race conditions",
            "Handling edge cases",
            "Memory management problems"
        ]
        return random.sample(challenges, random.randint(1, 3))
    
    def _generate_solutions(self, technologies: List[str]) -> List[str]:
        """生成解决方案"""
        solutions = [
            f"Used {random.choice(technologies)} built-in functions",
            "Applied design patterns",
            "Implemented caching strategy",
            "Added error handling",
            "Optimized database queries",
            "Refactored code structure"
        ]
        return random.sample(solutions, random.randint(1, 2))
    
    def _get_file_extension(self, language: str) -> str:
        """获取文件扩展名"""
        extensions = {
            'Python': 'py',
            'JavaScript': 'js',
            'TypeScript': 'ts',
            'Java': 'java',
            'Go': 'go',
            'Rust': 'rs'
        }
        return extensions.get(language, 'txt')
    
    def _generate_code_content(self, language: str, work_type: str) -> str:
        """生成代码内容"""
        templates = {
            'Python': '''
def process_data(data):
    """Process input data and return results"""
    result = []
    for item in data:
        if item.is_valid():
            result.append(item.transform())
    return result
''',
            'JavaScript': '''
function processData(data) {
    // Process input data and return results
    return data
        .filter(item => item.isValid())
        .map(item => item.transform());
}
''',
            'Java': '''
public class DataProcessor {
    public List<ProcessedItem> processData(List<DataItem> data) {
        return data.stream()
            .filter(DataItem::isValid)
            .map(DataItem::transform)
            .collect(Collectors.toList());
    }
}
'''
        }
        return templates.get(language, f'// {language} code for {work_type}')
    
    def _generate_concepts(self, language: str) -> List[str]:
        """生成概念列表"""
        concepts_map = {
            'Python': ['List comprehension', 'Decorators', 'Context managers'],
            'JavaScript': ['Async/await', 'Closures', 'Promises'],
            'Java': ['Streams', 'Generics', 'Annotations'],
            'TypeScript': ['Interfaces', 'Generics', 'Type guards']
        }
        concepts = concepts_map.get(language, ['Basic syntax', 'Functions', 'Variables'])
        return random.sample(concepts, random.randint(1, len(concepts)))
    
    def _score_to_level(self, score: float) -> str:
        """将分数转换为熟练度级别"""
        if score >= 80:
            return "expert"
        elif score >= 60:
            return "advanced"
        elif score >= 30:
            return "intermediate"
        else:
            return "beginner"
    
    def _determine_tech_category(self, tech_name: str) -> str:
        """确定技术分类"""
        for category, tech_list in self.technologies.items():
            if tech_name in tech_list:
                return category
        return 'general'
    
    def generate_complete_test_dataset(
        self, 
        username: str = "test_user",
        email: str = "test@example.com",
        session_count: int = 25,
        asset_count: int = 12,
        debt_count: int = 8
    ) -> Dict[str, Any]:
        """
        生成完整的测试数据集
        
        Args:
            username: 用户名
            email: 邮箱
            session_count: MCP会话数量
            asset_count: 技术栈资产数量
            debt_count: 技术栈负债数量
        
        Returns:
            生成的数据统计
        """
        # 创建用户
        user = self.create_test_user(username, email)
        
        # 生成MCP会话
        sessions = self.generate_mcp_sessions(user.id, session_count)
        
        # 生成代码片段
        snippets = self.generate_code_snippets(sessions)
        
        # 生成现有资产
        assets = self.generate_existing_assets(user.id, asset_count)
        
        # 生成技术栈负债
        debts = self.generate_tech_debts(user.id, debt_count)
        
        # 提交所有更改
        self.db.commit()
        
        return {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'sessions_created': len(sessions),
            'snippets_created': len(snippets),
            'assets_created': len(assets),
            'debts_created': len(debts),
            'total_records': len(sessions) + len(snippets) + len(assets) + len(debts) + 1
        }