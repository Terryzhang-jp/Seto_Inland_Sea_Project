from pydantic import BaseModel, Field
from typing import Any, Optional

class APIResponse(BaseModel):
    """通用API响应模型"""
    success: bool = Field(True, description="请求是否成功")
    data: Any = Field(None, description="响应数据")
    message: str = Field("Success", description="响应消息")
    total: Optional[int] = Field(None, description="总数量")
    page: Optional[int] = Field(None, description="当前页码")
    limit: Optional[int] = Field(None, description="每页数量")

class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = Field(False, description="请求是否成功")
    error: dict = Field(..., description="错误信息")
    message: str = Field("Error", description="响应消息")
