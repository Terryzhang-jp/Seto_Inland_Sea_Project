from pydantic import BaseModel, Field
from typing import Optional

class Company(BaseModel):
    """船运公司模型"""
    name: str = Field(..., description="公司名称")
    phone: str = Field(..., description="联系电话")
    website: str = Field(..., description="网站")
    main_routes: str = Field(..., description="主要航线")
    notes: str = Field(..., description="备注")

class CompanyResponse(BaseModel):
    """公司响应模型"""
    success: bool = Field(True, description="请求是否成功")
    data: list[Company] = Field(..., description="公司数据")
    total: int = Field(..., description="总数量")
    message: str = Field("Success", description="响应消息")
