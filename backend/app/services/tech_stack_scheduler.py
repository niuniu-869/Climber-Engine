#!/usr/bin/env python3
"""
技术栈总结Agent定时任务调度器
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.tech_stack_summary_agent import TechStackSummaryAgent
from app.services.tech_stack_data_service import TechStackDataService


class TechStackScheduler:
    """
    技术栈总结Agent定时任务调度器
    
    负责管理和执行技术栈分析的定时任务
    """
    
    def __init__(self, config_path: str = "app/config/tech_stack_agent_config.yaml"):
        """初始化调度器"""
        self.agent = TechStackSummaryAgent(config_path)
        self.scheduler = None
        self.logger = self._setup_logger()
        self.is_running = False
        self.job_stats = {
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0,
            'last_run_time': None,
            'last_run_status': None,
            'next_run_time': None
        }
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('TechStackScheduler')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _create_scheduler(self) -> AsyncIOScheduler:
        """创建调度器实例"""
        jobstores = {
            'default': MemoryJobStore()
        }
        
        executors = {
            'default': AsyncIOExecutor()
        }
        
        job_defaults = {
            'coalesce': True,  # 合并多个相同的任务
            'max_instances': 1,  # 同时只运行一个实例
            'misfire_grace_time': 300  # 错过执行时间的宽限期（秒）
        }
        
        scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
        
        return scheduler
    
    async def start(self):
        """启动调度器"""
        if self.is_running:
            self.logger.warning("Scheduler is already running")
            return
        
        try:
            self.scheduler = self._create_scheduler()
            
            # 添加定时任务
            await self._add_scheduled_jobs()
            
            # 启动调度器
            self.scheduler.start()
            self.is_running = True
            
            self.logger.info("TechStack Scheduler started successfully")
            
            # 记录下次运行时间
            self._update_next_run_time()
            
        except Exception as e:
            self.logger.error(f"Failed to start scheduler: {e}")
            raise
    
    async def stop(self):
        """停止调度器"""
        if not self.is_running:
            self.logger.warning("Scheduler is not running")
            return
        
        try:
            if self.scheduler:
                self.scheduler.shutdown(wait=True)
                self.scheduler = None
            
            self.is_running = False
            self.logger.info("TechStack Scheduler stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping scheduler: {e}")
    
    async def _add_scheduled_jobs(self):
        """添加定时任务"""
        config = self.agent.config
        
        # 主要分析任务
        analysis_interval = config.get('schedule', {}).get('analysis_interval_hours', 24)
        self.scheduler.add_job(
            self._run_analysis_job,
            trigger=IntervalTrigger(hours=analysis_interval),
            id='tech_stack_analysis',
            name='Tech Stack Analysis',
            replace_existing=True
        )
        
        # 深度分析任务（如果配置了）
        deep_analysis_interval = config.get('schedule', {}).get('deep_analysis_interval_days')
        if deep_analysis_interval:
            self.scheduler.add_job(
                self._run_deep_analysis_job,
                trigger=IntervalTrigger(days=deep_analysis_interval),
                id='tech_stack_deep_analysis',
                name='Tech Stack Deep Analysis',
                replace_existing=True
            )
        
        # 月度总结任务
        monthly_interval = config.get('schedule', {}).get('monthly_summary_interval_days', 30)
        self.scheduler.add_job(
            self._run_monthly_summary_job,
            trigger=IntervalTrigger(days=monthly_interval),
            id='tech_stack_monthly_summary',
            name='Tech Stack Monthly Summary',
            replace_existing=True
        )
        
        # 季度报告任务
        quarterly_interval = config.get('schedule', {}).get('quarterly_report_interval_days', 90)
        self.scheduler.add_job(
            self._run_quarterly_report_job,
            trigger=IntervalTrigger(days=quarterly_interval),
            id='tech_stack_quarterly_report',
            name='Tech Stack Quarterly Report',
            replace_existing=True
        )
        
        # 健康检查任务（每小时）
        self.scheduler.add_job(
            self._health_check_job,
            trigger=IntervalTrigger(hours=1),
            id='scheduler_health_check',
            name='Scheduler Health Check',
            replace_existing=True
        )
        
        self.logger.info(f"Added {len(self.scheduler.get_jobs())} scheduled jobs")
    
    async def _run_analysis_job(self):
        """运行分析任务"""
        job_name = "Tech Stack Analysis"
        self.logger.info(f"Starting {job_name}")
        
        start_time = datetime.utcnow()
        self.job_stats['total_runs'] += 1
        self.job_stats['last_run_time'] = start_time
        
        try:
            # 检查Agent是否应该运行
            if not self.agent.should_run_analysis():
                self.logger.info(f"{job_name} skipped - not needed at this time")
                self.job_stats['last_run_status'] = 'skipped'
                return
            
            # 运行分析
            result = self.agent.run_analysis()
            
            if result['status'] == 'completed':
                self.job_stats['successful_runs'] += 1
                self.job_stats['last_run_status'] = 'success'
                
                duration = (datetime.utcnow() - start_time).total_seconds()
                self.logger.info(
                    f"{job_name} completed successfully in {duration:.2f}s. "
                    f"Analyzed {result.get('analyzed_users', 0)} users, "
                    f"processed {result.get('total_sessions_processed', 0)} sessions"
                )
            else:
                self.job_stats['failed_runs'] += 1
                self.job_stats['last_run_status'] = 'failed'
                self.logger.error(f"{job_name} failed: {result.get('message', 'Unknown error')}")
        
        except Exception as e:
            self.job_stats['failed_runs'] += 1
            self.job_stats['last_run_status'] = 'error'
            self.logger.error(f"Error in {job_name}: {e}")
        
        finally:
            self._update_next_run_time()
    
    async def _run_deep_analysis_job(self):
        """运行深度分析任务"""
        job_name = "Tech Stack Deep Analysis"
        self.logger.info(f"Starting {job_name}")
        
        try:
            # 深度分析可以包含更复杂的逻辑
            # 例如：分析技能趋势、市场需求变化等
            
            # 获取所有活跃用户
            db = next(get_db())
            data_service = TechStackDataService(db)
            
            try:
                active_users = data_service.get_active_users_with_sessions(days=30)
                
                self.logger.info(f"Running deep analysis for {len(active_users)} active users")
                
                for user in active_users:
                    # 为每个用户运行详细分析
                    result = self.agent.run_analysis(user_id=user.id)
                    
                    if result['status'] != 'completed':
                        self.logger.warning(
                            f"Deep analysis failed for user {user.id}: {result.get('message')}"
                        )
                
                self.logger.info(f"{job_name} completed for {len(active_users)} users")
            
            finally:
                db.close()
        
        except Exception as e:
            self.logger.error(f"Error in {job_name}: {e}")
    
    async def _run_monthly_summary_job(self):
        """运行月度总结任务"""
        job_name = "Tech Stack Monthly Summary"
        self.logger.info(f"Starting {job_name}")
        
        try:
            # 生成月度总结报告
            # 这里可以实现更复杂的报告生成逻辑
            
            db = next(get_db())
            data_service = TechStackDataService(db)
            
            try:
                active_users = data_service.get_active_users_with_sessions(days=30)
                
                monthly_stats = {
                    'period': datetime.utcnow().strftime('%Y-%m'),
                    'active_users': len(active_users),
                    'total_sessions': 0,
                    'total_learning_hours': 0,
                    'top_technologies': {},
                    'generated_at': datetime.utcnow().isoformat()
                }
                
                for user in active_users:
                    user_stats = data_service.get_mcp_session_statistics(user.id)
                    monthly_stats['total_sessions'] += user_stats['total_sessions']
                    monthly_stats['total_learning_hours'] += user_stats['total_duration_hours']
                    
                    # 统计技术使用情况
                    for tech, count in user_stats['technologies_used']:
                        if tech in monthly_stats['top_technologies']:
                            monthly_stats['top_technologies'][tech] += count
                        else:
                            monthly_stats['top_technologies'][tech] = count
                
                self.logger.info(
                    f"{job_name} completed. "
                    f"Active users: {monthly_stats['active_users']}, "
                    f"Total sessions: {monthly_stats['total_sessions']}, "
                    f"Learning hours: {monthly_stats['total_learning_hours']:.1f}"
                )
            
            finally:
                db.close()
        
        except Exception as e:
            self.logger.error(f"Error in {job_name}: {e}")
    
    async def _run_quarterly_report_job(self):
        """运行季度报告任务"""
        job_name = "Tech Stack Quarterly Report"
        self.logger.info(f"Starting {job_name}")
        
        try:
            # 生成季度报告
            # 包含更长期的趋势分析
            
            db = next(get_db())
            data_service = TechStackDataService(db)
            
            try:
                active_users = data_service.get_active_users_with_sessions(days=90)
                
                quarterly_stats = {
                    'period': f"Q{(datetime.utcnow().month - 1) // 3 + 1}-{datetime.utcnow().year}",
                    'active_users': len(active_users),
                    'skill_growth_trends': {},
                    'technology_adoption': {},
                    'learning_velocity': {},
                    'generated_at': datetime.utcnow().isoformat()
                }
                
                # 分析每个用户的季度进展
                for user in active_users:
                    assets = data_service.get_tech_stack_assets(user.id, is_active=True)
                    debts = data_service.get_tech_stack_debts(user.id, is_active=True)
                    
                    # 计算技能增长
                    total_proficiency = sum(asset.proficiency_score for asset in assets)
                    avg_proficiency = total_proficiency / len(assets) if assets else 0
                    
                    quarterly_stats['skill_growth_trends'][user.id] = {
                        'avg_proficiency': avg_proficiency,
                        'total_assets': len(assets),
                        'active_debts': len(debts)
                    }
                
                self.logger.info(
                    f"{job_name} completed for {len(active_users)} users"
                )
            
            finally:
                db.close()
        
        except Exception as e:
            self.logger.error(f"Error in {job_name}: {e}")
    
    async def _health_check_job(self):
        """健康检查任务"""
        try:
            # 检查Agent状态
            status = self.agent.get_analysis_status()
            
            if not status['enabled']:
                self.logger.warning("TechStack Agent is disabled")
            
            # 检查数据库连接
            db = next(get_db())
            try:
                # 简单的数据库查询测试
                data_service = TechStackDataService(db)
                active_users = data_service.get_active_users_with_sessions(days=1)
                
                self.logger.debug(
                    f"Health check passed. Agent enabled: {status['enabled']}, "
                    f"Active users (24h): {len(active_users)}"
                )
            finally:
                db.close()
        
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
    
    def _update_next_run_time(self):
        """更新下次运行时间"""
        try:
            if self.scheduler:
                jobs = self.scheduler.get_jobs()
                if jobs:
                    # 找到最近的下次运行时间
                    next_times = [job.next_run_time for job in jobs if job.next_run_time]
                    if next_times:
                        self.job_stats['next_run_time'] = min(next_times)
        except Exception as e:
            self.logger.error(f"Error updating next run time: {e}")
    
    async def trigger_manual_analysis(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """手动触发分析"""
        self.logger.info(f"Manual analysis triggered for user_id: {user_id}")
        
        try:
            result = self.agent.run_analysis(user_id=user_id)
            self.logger.info(f"Manual analysis completed: {result['status']}")
            return result
        except Exception as e:
            self.logger.error(f"Manual analysis failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        jobs_info = []
        
        if self.scheduler:
            for job in self.scheduler.get_jobs():
                jobs_info.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                })
        
        return {
            'is_running': self.is_running,
            'agent_enabled': self.agent.is_enabled(),
            'job_stats': self.job_stats.copy(),
            'scheduled_jobs': jobs_info,
            'scheduler_state': self.scheduler.state if self.scheduler else None
        }
    
    async def reschedule_jobs(self):
        """重新调度任务（重新加载配置）"""
        if not self.is_running:
            self.logger.warning("Cannot reschedule jobs - scheduler is not running")
            return
        
        try:
            # 重新加载Agent配置
            self.agent = TechStackSummaryAgent()
            
            # 移除现有任务
            for job in self.scheduler.get_jobs():
                self.scheduler.remove_job(job.id)
            
            # 重新添加任务
            await self._add_scheduled_jobs()
            
            self.logger.info("Jobs rescheduled successfully")
            self._update_next_run_time()
            
        except Exception as e:
            self.logger.error(f"Error rescheduling jobs: {e}")
            raise


# 全局调度器实例
_scheduler_instance: Optional[TechStackScheduler] = None


def get_scheduler() -> TechStackScheduler:
    """获取全局调度器实例"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = TechStackScheduler()
    return _scheduler_instance


async def start_scheduler():
    """启动全局调度器"""
    scheduler = get_scheduler()
    await scheduler.start()


async def stop_scheduler():
    """停止全局调度器"""
    global _scheduler_instance
    if _scheduler_instance:
        await _scheduler_instance.stop()
        _scheduler_instance = None