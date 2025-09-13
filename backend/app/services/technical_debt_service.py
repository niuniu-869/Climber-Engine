#!/usr/bin/env python3
"""
技术债务服务层
处理技术债务分析和管理的业务逻辑
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
import json
import re

from ..models.technical_debt import TechnicalDebt
from ..models.user import User
from ..models.coding_session import CodingSession
from ..models.code_record import CodeRecord
from ..schemas.technical_debt import TechnicalDebtCreate, TechnicalDebtUpdate
from ..core.exceptions import TechnicalDebtNotFoundError, InvalidOperationError
from ..core.logger import get_logger

logger = get_logger(__name__)


class TechnicalDebtService:
    """技术债务服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_technical_debts(self, skip: int = 0, limit: int = 100,
                          user_id: Optional[int] = None,
                          status: Optional[str] = None,
                          severity: Optional[str] = None,
                          debt_type: Optional[str] = None) -> List[TechnicalDebt]:
        """获取技术债务列表"""
        query = self.db.query(TechnicalDebt)
        
        if user_id:
            query = query.filter(TechnicalDebt.user_id == user_id)
        
        if status:
            query = query.filter(TechnicalDebt.status == status)
        
        if severity:
            query = query.filter(TechnicalDebt.severity == severity)
        
        if debt_type:
            query = query.filter(TechnicalDebt.debt_type == debt_type)
        
        return query.order_by(desc(TechnicalDebt.created_at)).offset(skip).limit(limit).all()
    
    def get_technical_debt_by_id(self, debt_id: int) -> TechnicalDebt:
        """根据ID获取技术债务"""
        debt = self.db.query(TechnicalDebt).filter(TechnicalDebt.id == debt_id).first()
        if not debt:
            raise TechnicalDebtNotFoundError(f"Technical debt with id {debt_id} not found")
        return debt
    
    def create_technical_debt(self, debt_data: TechnicalDebtCreate) -> TechnicalDebt:
        """创建技术债务记录"""
        # 验证用户存在
        user = self.db.query(User).filter(User.id == debt_data.user_id).first()
        if not user:
            raise InvalidOperationError(f"User with id {debt_data.user_id} not found")
        
        # 创建技术债务记录
        db_debt = TechnicalDebt(
            user_id=debt_data.user_id,
            title=debt_data.title,
            description=debt_data.description,
            debt_type=debt_data.debt_type,
            severity=debt_data.severity,
            file_path=debt_data.file_path,
            line_number=debt_data.line_number,
            code_snippet=debt_data.code_snippet,
            suggested_fix=debt_data.suggested_fix,
            estimated_effort=debt_data.estimated_effort,
            impact_score=debt_data.impact_score,
            tags=debt_data.tags or [],
            metadata=debt_data.metadata or {},
            status='open'
        )
        
        self.db.add(db_debt)
        self.db.commit()
        self.db.refresh(db_debt)
        
        logger.info(f"Created technical debt: {db_debt.title} (ID: {db_debt.id})")
        return db_debt
    
    def update_technical_debt(self, debt_id: int, debt_data: TechnicalDebtUpdate) -> TechnicalDebt:
        """更新技术债务"""
        debt = self.get_technical_debt_by_id(debt_id)
        
        # 更新字段
        update_data = debt_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(debt, field, value)
        
        debt.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(debt)
        
        logger.info(f"Updated technical debt: {debt.title} (ID: {debt.id})")
        return debt
    
    def delete_technical_debt(self, debt_id: int) -> bool:
        """删除技术债务"""
        debt = self.get_technical_debt_by_id(debt_id)
        
        self.db.delete(debt)
        self.db.commit()
        
        logger.info(f"Deleted technical debt: {debt.title} (ID: {debt.id})")
        return True
    
    def resolve_technical_debt(self, debt_id: int, resolution_notes: str) -> TechnicalDebt:
        """解决技术债务"""
        debt = self.get_technical_debt_by_id(debt_id)
        
        if debt.status == 'resolved':
            raise InvalidOperationError("Technical debt is already resolved")
        
        debt.status = 'resolved'
        debt.resolved_at = datetime.utcnow()
        debt.resolution_notes = resolution_notes
        debt.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(debt)
        
        logger.info(f"Resolved technical debt: {debt.title} (ID: {debt.id})")
        return debt
    
    def analyze_code_for_debt(self, user_id: int, code_content: str, 
                            file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """分析代码中的技术债务"""
        detected_debts = []
        
        # 代码复杂度分析
        complexity_issues = self._analyze_complexity(code_content, file_path)
        detected_debts.extend(complexity_issues)
        
        # 代码重复分析
        duplication_issues = self._analyze_duplication(code_content, file_path)
        detected_debts.extend(duplication_issues)
        
        # 代码风格分析
        style_issues = self._analyze_style(code_content, file_path)
        detected_debts.extend(style_issues)
        
        # 安全问题分析
        security_issues = self._analyze_security(code_content, file_path)
        detected_debts.extend(security_issues)
        
        # 性能问题分析
        performance_issues = self._analyze_performance(code_content, file_path)
        detected_debts.extend(performance_issues)
        
        # 自动创建技术债务记录
        created_debts = []
        for issue in detected_debts:
            if issue['severity'] in ['high', 'critical']:  # 只自动创建高严重性问题
                debt_data = TechnicalDebtCreate(
                    user_id=user_id,
                    title=issue['title'],
                    description=issue['description'],
                    debt_type=issue['type'],
                    severity=issue['severity'],
                    file_path=file_path,
                    line_number=issue.get('line_number'),
                    code_snippet=issue.get('code_snippet'),
                    suggested_fix=issue.get('suggested_fix'),
                    estimated_effort=issue.get('estimated_effort', 60),
                    impact_score=issue.get('impact_score', 5),
                    metadata={'auto_detected': True, 'analysis_timestamp': datetime.utcnow().isoformat()}
                )
                
                debt = self.create_technical_debt(debt_data)
                created_debts.append(debt)
        
        logger.info(f"Analyzed code and detected {len(detected_debts)} issues, created {len(created_debts)} debt records")
        return {
            'detected_issues': detected_debts,
            'created_debts': created_debts,
            'analysis_summary': {
                'total_issues': len(detected_debts),
                'critical_issues': len([i for i in detected_debts if i['severity'] == 'critical']),
                'high_issues': len([i for i in detected_debts if i['severity'] == 'high']),
                'medium_issues': len([i for i in detected_debts if i['severity'] == 'medium']),
                'low_issues': len([i for i in detected_debts if i['severity'] == 'low'])
            }
        }
    
    def _analyze_complexity(self, code: str, file_path: Optional[str]) -> List[Dict[str, Any]]:
        """分析代码复杂度"""
        issues = []
        lines = code.split('\n')
        
        # 检查函数长度
        current_function = None
        function_start = 0
        indent_level = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # 检测函数定义
            if re.match(r'^\s*def\s+\w+', line) or re.match(r'^\s*function\s+\w+', line):
                if current_function:
                    # 检查前一个函数的长度
                    function_length = i - function_start
                    if function_length > 50:
                        issues.append({
                            'title': f'Long Function: {current_function}',
                            'description': f'Function {current_function} is {function_length} lines long, consider breaking it down',
                            'type': 'complexity',
                            'severity': 'high' if function_length > 100 else 'medium',
                            'line_number': function_start,
                            'code_snippet': '\n'.join(lines[function_start-1:i-1]),
                            'suggested_fix': 'Break down into smaller functions with single responsibilities',
                            'estimated_effort': 120,
                            'impact_score': 7
                        })
                
                current_function = re.search(r'\b(\w+)\s*\(', line).group(1) if re.search(r'\b(\w+)\s*\(', line) else 'unknown'
                function_start = i
                indent_level = len(line) - len(line.lstrip())
            
            # 检查嵌套深度
            current_indent = len(line) - len(line.lstrip())
            if current_indent > 20:  # 超过5层嵌套
                issues.append({
                    'title': 'Deep Nesting Detected',
                    'description': f'Code has deep nesting at line {i}, consider refactoring',
                    'type': 'complexity',
                    'severity': 'medium',
                    'line_number': i,
                    'code_snippet': line,
                    'suggested_fix': 'Extract nested logic into separate functions or use early returns',
                    'estimated_effort': 60,
                    'impact_score': 5
                })
        
        # 检查最后一个函数
        if current_function:
            function_length = len(lines) - function_start + 1
            if function_length > 50:
                issues.append({
                    'title': f'Long Function: {current_function}',
                    'description': f'Function {current_function} is {function_length} lines long, consider breaking it down',
                    'type': 'complexity',
                    'severity': 'high' if function_length > 100 else 'medium',
                    'line_number': function_start,
                    'suggested_fix': 'Break down into smaller functions with single responsibilities',
                    'estimated_effort': 120,
                    'impact_score': 7
                })
        
        return issues
    
    def _analyze_duplication(self, code: str, file_path: Optional[str]) -> List[Dict[str, Any]]:
        """分析代码重复"""
        issues = []
        lines = code.split('\n')
        
        # 简单的重复行检测
        line_counts = {}
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if len(stripped) > 10 and not stripped.startswith('#') and not stripped.startswith('//'):
                if stripped in line_counts:
                    line_counts[stripped].append(i)
                else:
                    line_counts[stripped] = [i]
        
        for line_content, line_numbers in line_counts.items():
            if len(line_numbers) > 2:  # 出现3次以上
                issues.append({
                    'title': 'Duplicate Code Detected',
                    'description': f'Line "{line_content[:50]}..." appears {len(line_numbers)} times',
                    'type': 'duplication',
                    'severity': 'medium',
                    'line_number': line_numbers[0],
                    'code_snippet': line_content,
                    'suggested_fix': 'Extract common code into a reusable function or constant',
                    'estimated_effort': 90,
                    'impact_score': 6,
                    'metadata': {'duplicate_lines': line_numbers}
                })
        
        return issues
    
    def _analyze_style(self, code: str, file_path: Optional[str]) -> List[Dict[str, Any]]:
        """分析代码风格"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 检查行长度
            if len(line) > 120:
                issues.append({
                    'title': 'Long Line',
                    'description': f'Line {i} is {len(line)} characters long, exceeds recommended 120 characters',
                    'type': 'style',
                    'severity': 'low',
                    'line_number': i,
                    'code_snippet': line,
                    'suggested_fix': 'Break long line into multiple lines or extract to variables',
                    'estimated_effort': 15,
                    'impact_score': 2
                })
            
            # 检查TODO/FIXME注释
            if re.search(r'\b(TODO|FIXME|HACK|XXX)\b', line, re.IGNORECASE):
                issues.append({
                    'title': 'TODO/FIXME Comment',
                    'description': f'Found TODO/FIXME comment at line {i}',
                    'type': 'maintenance',
                    'severity': 'low',
                    'line_number': i,
                    'code_snippet': line.strip(),
                    'suggested_fix': 'Address the TODO/FIXME or create a proper issue',
                    'estimated_effort': 30,
                    'impact_score': 3
                })
        
        return issues
    
    def _analyze_security(self, code: str, file_path: Optional[str]) -> List[Dict[str, Any]]:
        """分析安全问题"""
        issues = []
        lines = code.split('\n')
        
        security_patterns = [
            (r'password\s*=\s*["\'][^"\'\']+["\']', 'Hardcoded Password', 'critical'),
            (r'api_key\s*=\s*["\'][^"\'\']+["\']', 'Hardcoded API Key', 'critical'),
            (r'secret\s*=\s*["\'][^"\'\']+["\']', 'Hardcoded Secret', 'critical'),
            (r'eval\s*\(', 'Use of eval()', 'high'),
            (r'exec\s*\(', 'Use of exec()', 'high'),
            (r'shell=True', 'Shell Injection Risk', 'high'),
            (r'sql\s*=.*\+.*', 'Potential SQL Injection', 'high')
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, title, severity in security_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'title': title,
                        'description': f'Potential security issue detected at line {i}',
                        'type': 'security',
                        'severity': severity,
                        'line_number': i,
                        'code_snippet': line.strip(),
                        'suggested_fix': self._get_security_fix_suggestion(title),
                        'estimated_effort': 60,
                        'impact_score': 9 if severity == 'critical' else 7
                    })
        
        return issues
    
    def _analyze_performance(self, code: str, file_path: Optional[str]) -> List[Dict[str, Any]]:
        """分析性能问题"""
        issues = []
        lines = code.split('\n')
        
        performance_patterns = [
            (r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(', 'Inefficient Loop Pattern', 'medium'),
            (r'\.append\s*\(.*\)\s*$', 'List Append in Loop', 'low'),
            (r'\+\s*=.*\[.*\]', 'String Concatenation in Loop', 'medium'),
            (r'time\.sleep\s*\(', 'Blocking Sleep', 'low')
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, title, severity in performance_patterns:
                if re.search(pattern, line):
                    issues.append({
                        'title': title,
                        'description': f'Potential performance issue at line {i}',
                        'type': 'performance',
                        'severity': severity,
                        'line_number': i,
                        'code_snippet': line.strip(),
                        'suggested_fix': self._get_performance_fix_suggestion(title),
                        'estimated_effort': 45,
                        'impact_score': 4
                    })
        
        return issues
    
    def _get_security_fix_suggestion(self, issue_type: str) -> str:
        """获取安全问题修复建议"""
        suggestions = {
            'Hardcoded Password': 'Use environment variables or secure configuration management',
            'Hardcoded API Key': 'Store API keys in environment variables or secure vaults',
            'Hardcoded Secret': 'Use secure secret management systems',
            'Use of eval()': 'Avoid eval(), use safer alternatives like ast.literal_eval()',
            'Use of exec()': 'Avoid exec(), redesign to use safer code execution patterns',
            'Shell Injection Risk': 'Use shell=False and validate inputs, or use subprocess with list arguments',
            'Potential SQL Injection': 'Use parameterized queries or ORM methods'
        }
        return suggestions.get(issue_type, 'Review and apply security best practices')
    
    def _get_performance_fix_suggestion(self, issue_type: str) -> str:
        """获取性能问题修复建议"""
        suggestions = {
            'Inefficient Loop Pattern': 'Use enumerate() instead of range(len())',
            'List Append in Loop': 'Consider list comprehension or pre-allocate list size',
            'String Concatenation in Loop': 'Use join() method or f-strings for better performance',
            'Blocking Sleep': 'Consider async/await or non-blocking alternatives'
        }
        return suggestions.get(issue_type, 'Review for performance optimization opportunities')
    
    def get_user_debt_summary(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """获取用户技术债务汇总"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 基础统计 - 通过CodeRecord和CodingSession关联用户
        total_debts = self.db.query(func.count(TechnicalDebt.id)).join(
            CodeRecord, TechnicalDebt.code_record_id == CodeRecord.id
        ).join(
            CodingSession, CodeRecord.coding_session_id == CodingSession.id
        ).filter(
            CodingSession.user_id == user_id
        ).scalar() or 0
        
        open_debts = self.db.query(func.count(TechnicalDebt.id)).join(
            CodeRecord, TechnicalDebt.code_record_id == CodeRecord.id
        ).join(
            CodingSession, CodeRecord.coding_session_id == CodingSession.id
        ).filter(
            and_(
                CodingSession.user_id == user_id,
                TechnicalDebt.status == 'open'
            )
        ).scalar() or 0
        
        resolved_debts = self.db.query(func.count(TechnicalDebt.id)).join(
            CodeRecord, TechnicalDebt.code_record_id == CodeRecord.id
        ).join(
            CodingSession, CodeRecord.coding_session_id == CodingSession.id
        ).filter(
            and_(
                CodingSession.user_id == user_id,
                TechnicalDebt.status == 'resolved'
            )
        ).scalar() or 0
        
        # 严重性分布
        severity_distribution = (self.db.query(
                TechnicalDebt.severity,
                func.count(TechnicalDebt.id).label('count')
            )
            .join(CodeRecord, TechnicalDebt.code_record_id == CodeRecord.id)
            .join(CodingSession, CodeRecord.coding_session_id == CodingSession.id)
            .filter(CodingSession.user_id == user_id)
            .group_by(TechnicalDebt.severity)
            .all())
        
        # 类型分布
        type_distribution = (self.db.query(
                TechnicalDebt.debt_type,
                func.count(TechnicalDebt.id).label('count')
            )
            .join(CodeRecord, TechnicalDebt.code_record_id == CodeRecord.id)
            .join(CodingSession, CodeRecord.coding_session_id == CodingSession.id)
            .filter(CodingSession.user_id == user_id)
            .group_by(TechnicalDebt.debt_type)
            .all())
        
        # 总影响分数
        total_impact = self.db.query(func.sum(TechnicalDebt.impact_score)).join(
            CodeRecord, TechnicalDebt.code_record_id == CodeRecord.id
        ).join(
            CodingSession, CodeRecord.coding_session_id == CodingSession.id
        ).filter(
            and_(
                CodingSession.user_id == user_id,
                TechnicalDebt.status == 'open'
            )
        ).scalar() or 0
        
        # 估计总工作量
        total_effort = self.db.query(func.sum(TechnicalDebt.effort_estimate)).join(
            CodeRecord, TechnicalDebt.code_record_id == CodeRecord.id
        ).join(
            CodingSession, CodeRecord.coding_session_id == CodingSession.id
        ).filter(
            and_(
                CodingSession.user_id == user_id,
                TechnicalDebt.status == 'open'
            )
        ).scalar() or 0
        
        return {
            'summary': {
                'total_debts': total_debts,
                'open_debts': open_debts,
                'resolved_debts': resolved_debts,
                'resolution_rate': round(resolved_debts / total_debts * 100, 2) if total_debts > 0 else 0,
                'total_impact_score': total_impact,
                'total_estimated_effort_minutes': total_effort,
                'total_estimated_effort_hours': round(total_effort / 60, 2)
            },
            'severity_distribution': [{
                'severity': severity,
                'count': count
            } for severity, count in severity_distribution],
            'type_distribution': [{
                'debt_type': debt_type,
                'count': count
            } for debt_type, count in type_distribution]
        }
    
    def get_debt_trends(self, user_id: int, days: int = 90) -> Dict[str, Any]:
        """获取技术债务趋势"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 每日新增债务
        daily_created = (self.db.query(
                func.date(TechnicalDebt.created_at).label('date'),
                func.count(TechnicalDebt.id).label('created')
            )
            .filter(
                and_(
                    TechnicalDebt.user_id == user_id,
                    TechnicalDebt.created_at >= start_date
                )
            )
            .group_by(func.date(TechnicalDebt.created_at))
            .all())
        
        # 每日解决债务
        daily_resolved = (self.db.query(
                func.date(TechnicalDebt.resolved_at).label('date'),
                func.count(TechnicalDebt.id).label('resolved')
            )
            .filter(
                and_(
                    TechnicalDebt.user_id == user_id,
                    TechnicalDebt.resolved_at >= start_date
                )
            )
            .group_by(func.date(TechnicalDebt.resolved_at))
            .all())
        
        # 计算净增长
        date_data = {}
        for date, created in daily_created:
            date_data[date] = {'created': created, 'resolved': 0}
        
        for date, resolved in daily_resolved:
            if date in date_data:
                date_data[date]['resolved'] = resolved
            else:
                date_data[date] = {'created': 0, 'resolved': resolved}
        
        trend_data = []
        for date in sorted(date_data.keys()):
            data = date_data[date]
            net_change = data['created'] - data['resolved']
            trend_data.append({
                'date': date.isoformat(),
                'created': data['created'],
                'resolved': data['resolved'],
                'net_change': net_change
            })
        
        return {
            'period_days': days,
            'daily_trends': trend_data,
            'summary': {
                'total_created': sum(d['created'] for d in trend_data),
                'total_resolved': sum(d['resolved'] for d in trend_data),
                'net_change': sum(d['net_change'] for d in trend_data)
            }
        }
    
    def get_improvement_suggestions(self, user_id: int) -> List[Dict[str, Any]]:
        """获取改进建议"""
        # 获取用户的技术债务统计
        summary = self.get_user_debt_summary(user_id)
        
        suggestions = []
        
        # 基于严重性分布的建议
        severity_counts = {item['severity']: item['count'] for item in summary['severity_distribution']}
        
        if severity_counts.get('critical', 0) > 0:
            suggestions.append({
                'type': 'urgent_action',
                'priority': 'high',
                'title': 'Address Critical Issues',
                'description': f"You have {severity_counts['critical']} critical technical debt issues that need immediate attention.",
                'action_items': [
                    'Review all critical security vulnerabilities',
                    'Fix hardcoded secrets and credentials',
                    'Address critical performance bottlenecks'
                ]
            })
        
        if severity_counts.get('high', 0) > 5:
            suggestions.append({
                'type': 'code_quality',
                'priority': 'medium',
                'title': 'Improve Code Quality',
                'description': f"You have {severity_counts['high']} high-severity issues affecting code quality.",
                'action_items': [
                    'Refactor complex functions',
                    'Reduce code duplication',
                    'Improve error handling'
                ]
            })
        
        # 基于类型分布的建议
        type_counts = {item['debt_type']: item['count'] for item in summary['type_distribution']}
        
        if type_counts.get('security', 0) > 0:
            suggestions.append({
                'type': 'security',
                'priority': 'high',
                'title': 'Security Review Required',
                'description': f"Found {type_counts['security']} security-related issues.",
                'action_items': [
                    'Conduct security code review',
                    'Implement secure coding practices',
                    'Use security scanning tools'
                ]
            })
        
        if type_counts.get('performance', 0) > 3:
            suggestions.append({
                'type': 'performance',
                'priority': 'medium',
                'title': 'Performance Optimization',
                'description': f"Multiple performance issues detected ({type_counts['performance']} issues).",
                'action_items': [
                    'Profile application performance',
                    'Optimize database queries',
                    'Implement caching strategies'
                ]
            })
        
        # 基于总体情况的建议
        if summary['summary']['total_debts'] > 20:
            suggestions.append({
                'type': 'process',
                'priority': 'medium',
                'title': 'Establish Debt Management Process',
                'description': 'High volume of technical debt suggests need for better processes.',
                'action_items': [
                    'Implement regular code reviews',
                    'Set up automated code quality checks',
                    'Allocate time for debt reduction in sprints'
                ]
            })
        
        if summary['summary']['resolution_rate'] < 50:
            suggestions.append({
                'type': 'workflow',
                'priority': 'low',
                'title': 'Improve Debt Resolution Rate',
                'description': f"Current resolution rate is {summary['summary']['resolution_rate']:.1f}%.",
                'action_items': [
                    'Prioritize debt resolution tasks',
                    'Break down large debt items',
                    'Track resolution progress regularly'
                ]
            })
        
        return suggestions
    
    def get_debt_metrics_overview(self, user_id: int) -> Dict[str, Any]:
        """获取技术债务指标概览"""
        # 获取基础数据
        summary = self.get_user_debt_summary(user_id)
        trends = self.get_debt_trends(user_id, days=30)
        
        # 计算关键指标
        debt_velocity = trends['summary']['net_change'] / 30  # 每日净增长
        
        # 债务密度（每个编程会话的平均债务数）
        recent_sessions = (self.db.query(func.count(CodingSession.id))
                          .filter(
                              and_(
                                  CodingSession.user_id == user_id,
                                  CodingSession.created_at >= datetime.utcnow() - timedelta(days=30)
                              )
                          )
                          .scalar())
        
        debt_density = summary['summary']['total_debts'] / max(recent_sessions, 1)
        
        # 债务年龄（平均未解决时间）
        open_debts = self.get_technical_debts(user_id=user_id, status='open')
        if open_debts:
            avg_age_days = sum(
                (datetime.utcnow() - debt.created_at).days for debt in open_debts
            ) / len(open_debts)
        else:
            avg_age_days = 0
        
        # 健康评分（0-100）
        health_score = self._calculate_debt_health_score(summary, debt_velocity, avg_age_days)
        
        return {
            'health_score': health_score,
            'key_metrics': {
                'total_open_debts': summary['summary']['open_debts'],
                'debt_velocity_per_day': round(debt_velocity, 2),
                'debt_density': round(debt_density, 2),
                'average_age_days': round(avg_age_days, 1),
                'total_impact_score': summary['summary']['total_impact_score'],
                'estimated_resolution_hours': summary['summary']['total_estimated_effort_hours']
            },
            'health_indicators': {
                'critical_issues': len([d for d in summary['severity_distribution'] if d['severity'] == 'critical']),
                'security_issues': len([d for d in summary['type_distribution'] if d['debt_type'] == 'security']),
                'resolution_rate': summary['summary']['resolution_rate'],
                'trend_direction': 'improving' if debt_velocity < 0 else 'worsening' if debt_velocity > 0 else 'stable'
            }
        }
    
    def _calculate_debt_health_score(self, summary: Dict, velocity: float, avg_age: float) -> int:
        """计算技术债务健康评分"""
        score = 100
        
        # 基于开放债务数量扣分
        open_debts = summary['summary']['open_debts']
        if open_debts > 50:
            score -= 30
        elif open_debts > 20:
            score -= 20
        elif open_debts > 10:
            score -= 10
        
        # 基于严重性分布扣分
        for item in summary['severity_distribution']:
            if item['severity'] == 'critical':
                score -= item['count'] * 10
            elif item['severity'] == 'high':
                score -= item['count'] * 5
        
        # 基于债务增长速度扣分
        if velocity > 2:
            score -= 20
        elif velocity > 1:
            score -= 10
        elif velocity > 0.5:
            score -= 5
        
        # 基于平均年龄扣分
        if avg_age > 90:
            score -= 15
        elif avg_age > 30:
            score -= 10
        elif avg_age > 14:
            score -= 5
        
        # 基于解决率加分
        resolution_rate = summary['summary']['resolution_rate']
        if resolution_rate > 80:
            score += 10
        elif resolution_rate > 60:
            score += 5
        
        return max(0, min(100, score))