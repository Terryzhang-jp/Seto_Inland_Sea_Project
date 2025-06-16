from pydantic import BaseModel, Field
from typing import Optional
from datetime import time

class FerryRoute(BaseModel):
    """船班航线模型"""
    departure_port: str = Field(..., description="出发地")
    arrival_port: str = Field(..., description="到达地")
    departure_time: str = Field(..., description="出发时间")
    arrival_time: str = Field(..., description="到达时间")
    company: str = Field(..., description="运营公司")
    ship_type: str = Field(..., description="船只类型")
    allows_vehicles: bool = Field(..., description="是否允许车辆")
    allows_bicycles: bool = Field(..., description="是否允许自行车")
    adult_fare: str = Field(..., description="大人票价")
    child_fare: str = Field(..., description="小人票价")
    operating_days: str = Field(..., description="运营日期")
    notes: Optional[str] = Field(None, description="备注")

class RouteSearchParams(BaseModel):
    """航线搜索参数"""
    departure: Optional[str] = Field(None, description="出发地")
    arrival: Optional[str] = Field(None, description="到达地")
    company: Optional[str] = Field(None, description="运营公司")
    departure_time_start: Optional[str] = Field(None, description="出发时间开始")
    departure_time_end: Optional[str] = Field(None, description="出发时间结束")
    allows_vehicles: Optional[bool] = Field(None, description="是否允许车辆")
    allows_bicycles: Optional[bool] = Field(None, description="是否允许自行车")
    page: int = Field(1, ge=1, description="页码")
    limit: int = Field(20, ge=1, le=100, description="每页数量")

class RouteResponse(BaseModel):
    """航线响应模型"""
    success: bool = Field(True, description="请求是否成功")
    data: list[FerryRoute] = Field(..., description="航线数据")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    limit: int = Field(..., description="每页数量")
    message: str = Field("Success", description="响应消息")
