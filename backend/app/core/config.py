#!/usr/bin/env python3
"""
应用配置管理
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    project_name: str = "登攀引擎"
    app_name: str = "登攀引擎"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 数据库配置
    database_url: str = "sqlite:///./climber_engine.db"
    
    # API 配置
    api_v1_str: str = "/api/v1"
    api_v1_prefix: str = "/api/v1"
    
    # CORS 配置
    backend_cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"]
    allowed_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:5174"
    
    @property
    def allowed_origins_list(self) -> list[str]:
        """将逗号分隔的字符串转换为列表"""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
    
    # AI 模型配置
    openai_api_key: Optional[str] = None
    openai_base_url: str = "https://api.openai.com/v1"
    
    qwen_api_key: Optional[str] = None
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    kimi_api_key: Optional[str] = None
    kimi_base_url: str = "https://api.moonshot.cn/v1"
    
    deepseek_api_key: Optional[str] = None
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    
    # MCP 配置
    mcp_server_port: int = 8001
    
    # 安全配置
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    email_reset_token_expire_hours: int = 48
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # 忽略额外的环境变量


# 全局配置实例
settings = Settings()