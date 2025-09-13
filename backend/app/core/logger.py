#!/usr/bin/env python3
"""
日志配置模块
"""

import logging
import sys
from typing import Optional
from pathlib import Path

from .config import settings


def setup_logging() -> None:
    """设置日志配置"""
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 配置日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # 设置根日志级别
    log_level = logging.DEBUG if settings.debug else logging.INFO
    
    # 配置根日志器
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # 控制台处理器
            logging.StreamHandler(sys.stdout),
            # 文件处理器
            logging.FileHandler(
                log_dir / "climber_engine.log",
                encoding="utf-8"
            )
        ]
    )
    
    # 设置第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """获取日志器"""
    if name is None:
        name = __name__
    return logging.getLogger(name)


# 初始化日志配置
setup_logging()

# 默认日志器
logger = get_logger(__name__)