#!/usr/bin/env python3
"""
AI服务层 - 集成多个LLM API
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import openai
from openai import AsyncOpenAI
import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logger import get_logger
from app.models.user import User
from app.models.coding_session import CodingSession
from app.models.code_record import CodeRecord

logger = get_logger(__name__)


class AIService:
    """AI服务类 - 统一管理多个LLM API调用"""
    
    def __init__(self, db: Session):
        self.db = db
        self.clients = self._initialize_clients()
    
    def _initialize_clients(self) -> Dict[str, Any]:
        """初始化各个LLM客户端"""
        clients = {}
        
        # OpenAI客户端
        if settings.openai_api_key:
            clients['openai'] = AsyncOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url
            )
            logger.info("OpenAI客户端初始化成功")
        
        # Qwen客户端
        if settings.qwen_api_key:
            clients['qwen'] = AsyncOpenAI(
                api_key=settings.qwen_api_key,
                base_url=settings.qwen_base_url
            )
            logger.info("Qwen客户端初始化成功")
        
        # Kimi客户端
        if settings.kimi_api_key:
            clients['kimi'] = AsyncOpenAI(
                api_key=settings.kimi_api_key,
                base_url=settings.kimi_base_url
            )
            logger.info("Kimi客户端初始化成功")
        
        # DeepSeek客户端
        if settings.deepseek_api_key:
            clients['deepseek'] = AsyncOpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url
            )
            logger.info("DeepSeek客户端初始化成功")
        
        return clients
    
    async def call_llm(
        self,
        messages: List[Dict[str, str]],
        model_provider: str = "openai",
        model_name: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """统一的LLM调用接口"""
        
        if model_provider not in self.clients:
            raise ValueError(f"不支持的模型提供商: {model_provider}")
        
        client = self.clients[model_provider]
        
        try:
            # 根据不同提供商调整模型名称
            if model_provider == "qwen":
                model_name = model_name.replace("gpt-4", "qwen-max")
            elif model_provider == "kimi":
                model_name = model_name.replace("gpt-4", "moonshot-v1-8k")
            elif model_provider == "deepseek":
                model_name = model_name.replace("gpt-4", "deepseek-chat")
            
            response = await client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            result = {
                "success": True,
                "content": response.choices[0].message.content,
                "model": model_name,
                "provider": model_provider,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"LLM调用成功 - {model_provider}/{model_name}")
            return result
            
        except Exception as e:
            logger.error(f"LLM调用失败 - {model_provider}/{model_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "model": model_name,
                "provider": model_provider,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def analyze_technical_debt(
        self,
        code_content: str,
        file_path: str,
        language: str = "python"
    ) -> Dict[str, Any]:
        """技术债务分析 - 总结Agent核心功能"""
        
        system_prompt = """
你是一个专业的代码质量分析专家。请分析提供的代码，识别技术债务并提供改进建议。

分析维度：
1. 代码复杂度和可读性
2. 潜在的性能问题
3. 安全漏洞
4. 代码异味（重复代码、长函数、大类等）
5. 最佳实践违反
6. 可维护性问题

请以JSON格式返回分析结果，包含：
- debt_score: 技术债务评分（0-100，越高越严重）
- issues: 发现的问题列表
- recommendations: 改进建议
- priority: 优先级（high/medium/low）
- estimated_fix_time: 预估修复时间（小时）
"""
        
        user_prompt = f"""
请分析以下{language}代码的技术债务：

文件路径: {file_path}

代码内容:
```{language}
{code_content}
```
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 优先使用DeepSeek进行代码分析
        result = await self.call_llm(
            messages=messages,
            model_provider="deepseek",
            model_name="deepseek-chat",
            temperature=0.3,
            max_tokens=2000
        )
        
        if result["success"]:
            try:
                # 尝试解析JSON响应
                analysis = json.loads(result["content"])
                return {
                    "success": True,
                    "analysis": analysis,
                    "model_info": {
                        "provider": result["provider"],
                        "model": result["model"],
                        "usage": result["usage"]
                    }
                }
            except json.JSONDecodeError:
                # 如果不是JSON格式，返回原始文本
                return {
                    "success": True,
                    "analysis": {
                        "raw_analysis": result["content"],
                        "debt_score": 50,  # 默认中等评分
                        "issues": ["AI分析结果格式异常，需要人工审查"],
                        "recommendations": ["请检查代码分析结果的格式"]
                    },
                    "model_info": {
                        "provider": result["provider"],
                        "model": result["model"],
                        "usage": result["usage"]
                    }
                }
        else:
            return {
                "success": False,
                "error": result["error"],
                "model_info": {
                    "provider": result["provider"],
                    "model": result["model"]
                }
            }
    
    async def generate_learning_tasks(
        self,
        user_skills: Dict[str, Any],
        focus_areas: List[str],
        difficulty_level: str = "intermediate",
        count: int = 5
    ) -> Dict[str, Any]:
        """生成个性化学习任务 - 培训Agent核心功能"""
        
        system_prompt = """
你是一个专业的编程教育专家。基于用户的技能水平和学习目标，生成个性化的编程学习任务。

任务设计原则：
1. 循序渐进，符合用户当前技能水平
2. 实践导向，包含具体的编程练习
3. 目标明确，每个任务都有清晰的学习目标
4. 可衡量，包含明确的完成标准
5. 有趣且有挑战性

请以JSON格式返回学习任务，包含：
- tasks: 任务列表，每个任务包含：
  - title: 任务标题
  - description: 详细描述
  - objectives: 学习目标列表
  - difficulty: 难度级别
  - estimated_hours: 预估完成时间
  - prerequisites: 前置技能要求
  - deliverables: 交付物要求
  - evaluation_criteria: 评估标准
"""
        
        user_prompt = f"""
请为以下用户生成{count}个个性化学习任务：

用户技能水平:
{json.dumps(user_skills, indent=2, ensure_ascii=False)}

重点学习领域: {', '.join(focus_areas)}
难度级别: {difficulty_level}

请确保任务既有挑战性又符合用户当前水平。
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 使用Qwen进行学习任务生成
        result = await self.call_llm(
            messages=messages,
            model_provider="qwen",
            model_name="qwen-max",
            temperature=0.8,
            max_tokens=3000
        )
        
        if result["success"]:
            try:
                tasks_data = json.loads(result["content"])
                return {
                    "success": True,
                    "tasks": tasks_data.get("tasks", []),
                    "generation_info": {
                        "focus_areas": focus_areas,
                        "difficulty_level": difficulty_level,
                        "requested_count": count,
                        "generated_count": len(tasks_data.get("tasks", []))
                    },
                    "model_info": {
                        "provider": result["provider"],
                        "model": result["model"],
                        "usage": result["usage"]
                    }
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "tasks": [{
                        "title": "AI生成的学习任务",
                        "description": result["content"],
                        "objectives": ["根据AI建议进行学习"],
                        "difficulty": difficulty_level,
                        "estimated_hours": 2
                    }],
                    "generation_info": {
                        "focus_areas": focus_areas,
                        "difficulty_level": difficulty_level,
                        "note": "AI响应格式异常，已转换为文本任务"
                    },
                    "model_info": {
                        "provider": result["provider"],
                        "model": result["model"],
                        "usage": result["usage"]
                    }
                }
        else:
            return {
                "success": False,
                "error": result["error"],
                "model_info": {
                    "provider": result["provider"],
                    "model": result["model"]
                }
            }
    
    async def get_coding_insights(
        self,
        session_data: Dict[str, Any],
        analysis_type: str = "performance"
    ) -> Dict[str, Any]:
        """获取编程洞察和建议"""
        
        system_prompt = """
你是一个专业的编程导师和性能分析专家。基于用户的编程会话数据，提供深入的洞察和改进建议。

分析维度：
1. 编程效率和生产力
2. 代码质量趋势
3. 学习进度和技能发展
4. 常见错误模式
5. 最佳实践应用

请以JSON格式返回分析结果。
"""
        
        user_prompt = f"""
请分析以下编程会话数据，重点关注{analysis_type}方面：

会话数据:
{json.dumps(session_data, indent=2, ensure_ascii=False)}

请提供具体的洞察和可操作的改进建议。
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 使用Kimi进行洞察分析
        result = await self.call_llm(
            messages=messages,
            model_provider="kimi",
            model_name="moonshot-v1-8k",
            temperature=0.6,
            max_tokens=2000
        )
        
        return result
    
    async def suggest_code_improvements(
        self,
        code: str,
        language: str,
        focus_areas: List[str] = None
    ) -> Dict[str, Any]:
        """代码改进建议"""
        
        focus_text = f"，重点关注：{', '.join(focus_areas)}" if focus_areas else ""
        
        system_prompt = f"""
你是一个资深的{language}开发专家。请分析提供的代码并给出具体的改进建议。

分析重点：
1. 代码结构和设计模式
2. 性能优化机会
3. 可读性和可维护性
4. 错误处理和边界情况
5. 最佳实践应用
{focus_text}

请提供具体的代码改进建议，包括修改后的代码示例。
"""
        
        user_prompt = f"""
请分析以下{language}代码并提供改进建议：

```{language}
{code}
```
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 使用OpenAI进行代码改进建议
        result = await self.call_llm(
            messages=messages,
            model_provider="openai",
            model_name="gpt-4",
            temperature=0.4,
            max_tokens=3000
        )
        
        return result
    
    async def assess_programming_skills(
        self,
        code_samples: List[str],
        skill_type: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """编程技能评估"""
        
        system_prompt = """
你是一个专业的编程技能评估专家。基于提供的代码样本，评估用户在特定技能领域的水平。

评估维度：
1. 语法掌握程度
2. 算法和数据结构理解
3. 设计模式应用
4. 代码组织和架构能力
5. 错误处理和边界情况考虑
6. 性能意识
7. 可读性和文档

请以JSON格式返回评估结果，包含：
- overall_score: 总体评分（0-100）
- skill_breakdown: 各维度详细评分
- strengths: 优势领域
- weaknesses: 需要改进的领域
- recommendations: 具体学习建议
- next_steps: 下一步学习计划
"""
        
        code_samples_text = "\n\n".join([
            f"代码样本 {i+1}:\n```\n{sample}\n```" 
            for i, sample in enumerate(code_samples)
        ])
        
        user_prompt = f"""
请评估用户在{skill_type}方面的编程技能：

{f"评估背景: {context}" if context else ""}

{code_samples_text}

请提供详细的技能评估和学习建议。
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 使用OpenAI进行技能评估
        result = await self.call_llm(
            messages=messages,
            model_provider="openai",
            model_name="gpt-4",
            temperature=0.5,
            max_tokens=2500
        )
        
        return result
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """获取可用的模型列表"""
        models = {}
        
        if "openai" in self.clients:
            models["openai"] = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
        
        if "qwen" in self.clients:
            models["qwen"] = ["qwen-max", "qwen-plus", "qwen-turbo"]
        
        if "kimi" in self.clients:
            models["kimi"] = ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]
        
        if "deepseek" in self.clients:
            models["deepseek"] = ["deepseek-chat", "deepseek-coder"]
        
        return models
    
    async def health_check(self) -> Dict[str, Any]:
        """AI服务健康检查"""
        health_status = {
            "service": "ai_service",
            "status": "healthy",
            "providers": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # 检查各个提供商的连接状态
        for provider, client in self.clients.items():
            try:
                # 发送简单的测试请求
                test_result = await self.call_llm(
                    messages=[{"role": "user", "content": "Hello"}],
                    model_provider=provider,
                    max_tokens=10
                )
                
                health_status["providers"][provider] = {
                    "status": "healthy" if test_result["success"] else "error",
                    "error": test_result.get("error") if not test_result["success"] else None
                }
            except Exception as e:
                health_status["providers"][provider] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # 如果所有提供商都有问题，标记整体状态为不健康
        if all(p["status"] == "error" for p in health_status["providers"].values()):
            health_status["status"] = "unhealthy"
        
        return health_status