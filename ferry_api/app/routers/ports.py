from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from ..models.port import PortResponse
from ..models.common import APIResponse
from ..services.port_service import port_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ports", tags=["港口"])

@router.get("/", response_model=PortResponse, summary="获取所有港口")
async def get_ports(
    search: Optional[str] = Query(None, description="搜索关键词")
):
    """
    获取瀬户内海所有港口信息
    
    可选参数：
    - search: 搜索关键词，支持港口名称、岛屿名称、地址搜索
    """
    try:
        if search:
            ports = port_service.search_ports(search)
        else:
            ports = port_service.get_all_ports()
        
        return PortResponse(
            success=True,
            data=ports,
            total=len(ports),
            message="获取港口信息成功"
        )
        
    except Exception as e:
        logger.error(f"Error in get_ports: {e}")
        raise HTTPException(status_code=500, detail="获取港口信息时发生错误")

@router.get("/{port_name}", response_model=APIResponse, summary="获取特定港口信息")
async def get_port_by_name(port_name: str):
    """
    根据港口名称获取详细信息
    """
    try:
        port = port_service.get_port_by_name(port_name)
        
        if not port:
            raise HTTPException(status_code=404, detail="港口未找到")
        
        return APIResponse(
            success=True,
            data=port,
            message="获取港口信息成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_port_by_name: {e}")
        raise HTTPException(status_code=500, detail="获取港口信息时发生错误")
