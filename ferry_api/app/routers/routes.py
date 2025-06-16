from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from ..models.route import RouteSearchParams, RouteResponse
from ..models.common import APIResponse
from ..services.route_service import route_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/routes", tags=["航线"])

@router.get("/", response_model=RouteResponse, summary="搜索航线")
async def search_routes(
    departure: Optional[str] = Query(None, description="出发地"),
    arrival: Optional[str] = Query(None, description="到达地"),
    company: Optional[str] = Query(None, description="运营公司"),
    departure_time_start: Optional[str] = Query(None, description="出发时间开始 (HH:MM)"),
    departure_time_end: Optional[str] = Query(None, description="出发时间结束 (HH:MM)"),
    allows_vehicles: Optional[bool] = Query(None, description="是否允许车辆"),
    allows_bicycles: Optional[bool] = Query(None, description="是否允许自行车"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量")
):
    """
    搜索船班航线
    
    支持多条件组合搜索：
    - 出发地和到达地支持模糊匹配
    - 可按运营公司筛选
    - 可按时间范围筛选
    - 可按车辆/自行车载运能力筛选
    - 支持分页查询
    """
    try:
        # 创建搜索参数
        search_params = RouteSearchParams(
            departure=departure,
            arrival=arrival,
            company=company,
            departure_time_start=departure_time_start,
            departure_time_end=departure_time_end,
            allows_vehicles=allows_vehicles,
            allows_bicycles=allows_bicycles,
            page=page,
            limit=limit
        )
        
        # 执行搜索
        routes, total = route_service.search_routes(search_params)
        
        return RouteResponse(
            success=True,
            data=routes,
            total=total,
            page=page,
            limit=limit,
            message="搜索成功"
        )
        
    except Exception as e:
        logger.error(f"Error in search_routes: {e}")
        raise HTTPException(status_code=500, detail="搜索航线时发生错误")

@router.get("/popular", response_model=APIResponse, summary="获取热门路线")
async def get_popular_routes():
    """
    获取热门跳岛路线推荐
    
    返回瀬户内海最受欢迎的岛屿间航线
    """
    try:
        popular_routes = route_service.get_popular_routes()
        
        return APIResponse(
            success=True,
            data=popular_routes,
            message="获取热门路线成功"
        )
        
    except Exception as e:
        logger.error(f"Error in get_popular_routes: {e}")
        raise HTTPException(status_code=500, detail="获取热门路线时发生错误")
