from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from ..models.company import CompanyResponse
from ..models.common import APIResponse
from ..services.company_service import company_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/companies", tags=["船运公司"])

@router.get("/", response_model=CompanyResponse, summary="获取所有船运公司")
async def get_companies(
    search: Optional[str] = Query(None, description="搜索关键词")
):
    """
    获取瀬户内海所有船运公司信息
    
    可选参数：
    - search: 搜索关键词，支持公司名称、主要航线搜索
    """
    try:
        if search:
            companies = company_service.search_companies(search)
        else:
            companies = company_service.get_all_companies()
        
        return CompanyResponse(
            success=True,
            data=companies,
            total=len(companies),
            message="获取公司信息成功"
        )
        
    except Exception as e:
        logger.error(f"Error in get_companies: {e}")
        raise HTTPException(status_code=500, detail="获取公司信息时发生错误")

@router.get("/{company_name}", response_model=APIResponse, summary="获取特定公司信息")
async def get_company_by_name(company_name: str):
    """
    根据公司名称获取详细信息
    """
    try:
        company = company_service.get_company_by_name(company_name)
        
        if not company:
            raise HTTPException(status_code=404, detail="公司未找到")
        
        return APIResponse(
            success=True,
            data=company,
            message="获取公司信息成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_company_by_name: {e}")
        raise HTTPException(status_code=500, detail="获取公司信息时发生错误")
