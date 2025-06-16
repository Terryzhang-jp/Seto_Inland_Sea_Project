from pydantic import BaseModel, Field
from typing import Optional

class Port(BaseModel):
    """港口模型"""
    name: str = Field(..., description="港口名称")
    island: str = Field(..., description="所在岛屿")
    address: str = Field(..., description="地址")
    features: str = Field(..., description="特点")
    connections: str = Field(..., description="连接岛屿")

class PortResponse(BaseModel):
    """港口响应模型"""
    success: bool = Field(True, description="请求是否成功")
    data: list[Port] = Field(..., description="港口数据")
    total: int = Field(..., description="总数量")
    message: str = Field("Success", description="响应消息")
