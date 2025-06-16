#!/usr/bin/env python3
"""
瀬户内海船班查询API启动脚本
"""

import uvicorn
import sys
from pathlib import Path

# 添加app目录到Python路径
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
