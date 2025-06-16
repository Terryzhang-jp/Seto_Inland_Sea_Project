import os
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

class Settings:
    """应用配置"""
    
    # 项目信息
    PROJECT_NAME: str = "瀬户内海船班查询API"
    PROJECT_DESCRIPTION: str = "Setouchi Ferry Timetable API"
    VERSION: str = "1.0.0"
    
    # API配置
    API_V1_STR: str = "/api/v1"
    
    # 数据文件路径
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    
    # CSV文件路径
    TIMETABLE_CSV: Path = DATA_DIR / "setouchi_ferry_timetable.csv"
    COMPANIES_CSV: Path = DATA_DIR / "ferry_companies_info.csv"
    PORTS_CSV: Path = DATA_DIR / "ports_info.csv"
    FARES_CSV: Path = DATA_DIR / "fare_summary.csv"
    
    # CORS设置
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",  # React开发服务器
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

settings = Settings()
