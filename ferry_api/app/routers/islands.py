from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging

from ..models.common import APIResponse
from ..models.island import (
    IslandTransport, IslandTransportSummary, BicycleRental,
    RentalSearchRequest, TransportType
)
from ..services.island_service import island_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/islands",
    tags=["islands"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=APIResponse, summary="获取所有岛屿交通信息")
async def get_all_islands():
    """
    获取所有岛屿的交通信息，包括巴士、自行车租赁和其他交通方式
    """
    try:
        islands = island_service.get_all_islands()
        return APIResponse(
            success=True,
            data=islands,
            message=f"成功获取{len(islands)}个岛屿的交通信息",
            total=len(islands)
        )
    except Exception as e:
        logger.error(f"Error getting all islands: {e}")
        raise HTTPException(status_code=500, detail="获取岛屿信息失败")

@router.get("/summary", response_model=APIResponse, summary="获取岛屿交通信息摘要")
async def get_islands_summary():
    """
    获取所有岛屿的交通信息摘要，包括基本统计和特色信息
    """
    try:
        summaries = island_service.get_islands_summary()
        return APIResponse(
            success=True,
            data=summaries,
            message=f"成功获取{len(summaries)}个岛屿的交通摘要",
            total=len(summaries)
        )
    except Exception as e:
        logger.error(f"Error getting islands summary: {e}")
        raise HTTPException(status_code=500, detail="获取岛屿摘要失败")

@router.get("/{island_name}", response_model=APIResponse, summary="获取特定岛屿交通信息")
async def get_island_by_name(island_name: str):
    """
    根据岛屿名称获取详细的交通信息
    
    - **island_name**: 岛屿名称（支持中文名或英文名，如：直岛、naoshima）
    """
    try:
        island = island_service.get_island_by_name(island_name)
        if not island:
            raise HTTPException(status_code=404, detail=f"未找到岛屿: {island_name}")
        
        return APIResponse(
            success=True,
            data=island,
            message=f"成功获取{island.island_name}的交通信息"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting island {island_name}: {e}")
        raise HTTPException(status_code=500, detail="获取岛屿信息失败")

@router.get("/rentals/bicycle", response_model=APIResponse, summary="搜索自行车租赁信息")
async def search_bicycle_rentals(
    island_name: Optional[str] = Query(None, description="岛屿名称"),
    max_price: Optional[int] = Query(None, description="最大价格（日元）"),
    rental_type: Optional[str] = Query(None, description="租赁类型（如：电动自行车、普通自行车）")
):
    """
    搜索自行车租赁信息
    
    - **island_name**: 可选，指定岛屿名称
    - **max_price**: 可选，最大价格过滤
    - **rental_type**: 可选，租赁类型过滤
    """
    try:
        results = island_service.search_bicycle_rentals(
            island_name=island_name,
            max_price=max_price,
            rental_type=rental_type
        )
        
        return APIResponse(
            success=True,
            data=results,
            message=f"找到{len(results)}个自行车租赁选项",
            total=len(results)
        )
    except Exception as e:
        logger.error(f"Error searching bicycle rentals: {e}")
        raise HTTPException(status_code=500, detail="搜索自行车租赁信息失败")

@router.get("/{island_name}/rentals/bicycle", response_model=APIResponse, summary="获取特定岛屿的自行车租赁信息")
async def get_island_bicycle_rentals(island_name: str):
    """
    获取特定岛屿的所有自行车租赁信息
    
    - **island_name**: 岛屿名称（支持中文名或英文名）
    """
    try:
        island = island_service.get_island_by_name(island_name)
        if not island:
            raise HTTPException(status_code=404, detail=f"未找到岛屿: {island_name}")
        
        return APIResponse(
            success=True,
            data={
                "island_name": island.island_name,
                "island_name_en": island.island_name_en,
                "bicycle_rentals": island.bicycle_rentals
            },
            message=f"成功获取{island.island_name}的自行车租赁信息",
            total=len(island.bicycle_rentals)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting bicycle rentals for {island_name}: {e}")
        raise HTTPException(status_code=500, detail="获取自行车租赁信息失败")

@router.get("/{island_name}/bus", response_model=APIResponse, summary="获取特定岛屿的巴士时刻表")
async def get_island_bus_schedule(island_name: str):
    """
    获取特定岛屿的巴士时刻表信息
    
    - **island_name**: 岛屿名称（支持中文名或英文名）
    """
    try:
        island = island_service.get_island_by_name(island_name)
        if not island:
            raise HTTPException(status_code=404, detail=f"未找到岛屿: {island_name}")
        
        return APIResponse(
            success=True,
            data={
                "island_name": island.island_name,
                "island_name_en": island.island_name_en,
                "bus_schedules": island.bus_schedules
            },
            message=f"成功获取{island.island_name}的巴士时刻表",
            total=len(island.bus_schedules)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting bus schedule for {island_name}: {e}")
        raise HTTPException(status_code=500, detail="获取巴士时刻表失败")

@router.get("/{island_name}/transport/other", response_model=APIResponse, summary="获取特定岛屿的其他交通方式")
async def get_island_other_transport(island_name: str):
    """
    获取特定岛屿的其他交通方式信息（出租车、汽车租赁等）
    
    - **island_name**: 岛屿名称（支持中文名或英文名）
    """
    try:
        island = island_service.get_island_by_name(island_name)
        if not island:
            raise HTTPException(status_code=404, detail=f"未找到岛屿: {island_name}")
        
        return APIResponse(
            success=True,
            data={
                "island_name": island.island_name,
                "island_name_en": island.island_name_en,
                "other_transports": island.other_transports
            },
            message=f"成功获取{island.island_name}的其他交通方式信息",
            total=len(island.other_transports)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting other transport for {island_name}: {e}")
        raise HTTPException(status_code=500, detail="获取其他交通方式信息失败")
