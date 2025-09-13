#!/usr/bin/env python3
"""
登攀引擎 FastAPI 应用入口
"""

import uvicorn
from app.core.app import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
