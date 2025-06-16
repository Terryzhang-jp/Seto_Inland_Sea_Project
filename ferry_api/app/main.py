from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from .core.config import settings
from .routers import routes, ports, companies, islands
from .models.common import APIResponse

# AI功能已移除

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
# 在生产环境中，我们需要更灵活的CORS处理
import os
if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("VERCEL"):
    # 生产环境：允许所有Vercel域名
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
else:
    # 开发环境：使用配置的域名列表
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 注册路由
app.include_router(routes.router, prefix=settings.API_V1_STR)
app.include_router(ports.router, prefix=settings.API_V1_STR)
app.include_router(companies.router, prefix=settings.API_V1_STR)
app.include_router(islands.router, prefix=settings.API_V1_STR)

# AI路由已移除

@app.get("/", response_model=APIResponse, summary="API根路径")
async def root():
    """
    API根路径，返回基本信息
    """
    return APIResponse(
        success=True,
        data={
            "name": settings.PROJECT_NAME,
            "description": settings.PROJECT_DESCRIPTION,
            "version": settings.VERSION,
            "docs_url": "/docs",
            "redoc_url": "/redoc"
        },
        message="瀬户内海船班查询API正在运行"
    )

@app.get("/health", response_model=APIResponse, summary="健康检查")
async def health_check():
    """
    健康检查端点
    """
    try:
        # 这里可以添加数据库连接检查等
        return APIResponse(
            success=True,
            data={"status": "healthy"},
            message="服务运行正常"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="服务不可用")

@app.get("/debug/data-status", response_model=APIResponse, summary="数据加载状态调试")
async def debug_data_status():
    """
    调试端点：检查数据加载状态
    """
    from .core.data_loader import data_loader
    import os

    status = {
        "current_working_directory": os.getcwd(),
        "base_dir": str(settings.BASE_DIR),
        "data_dir": str(settings.DATA_DIR),
        "data_dir_exists": settings.DATA_DIR.exists(),
        "timetable_loaded": data_loader.timetable_df is not None,
        "companies_loaded": data_loader.companies_df is not None,
        "ports_loaded": data_loader.ports_df is not None,
        "fares_loaded": data_loader.fares_df is not None,
    }

    if data_loader.timetable_df is not None:
        status["timetable_records"] = len(data_loader.timetable_df)
    if data_loader.companies_df is not None:
        status["companies_records"] = len(data_loader.companies_df)
    if data_loader.ports_df is not None:
        status["ports_records"] = len(data_loader.ports_df)
    if data_loader.fares_df is not None:
        status["fares_records"] = len(data_loader.fares_df)

    # 列出数据目录中的文件
    if settings.DATA_DIR.exists():
        status["csv_files"] = [f.name for f in settings.DATA_DIR.glob("*.csv")]

    return APIResponse(
        success=True,
        data=status,
        message="数据状态检查完成"
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    全局异常处理器
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "服务器内部错误"
            },
            "message": "请求处理失败"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
