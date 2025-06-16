from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class TransportType(str, Enum):
    """交通类型枚举"""
    BUS = "bus"
    BICYCLE = "bicycle"
    CAR = "car"
    MOTORBIKE = "motorbike"
    TAXI = "taxi"
    WALKING = "walking"
    FERRY = "ferry"
    OTHER = "other"

class BicycleRental(BaseModel):
    """自行车租赁信息模型"""
    shop_name: str = Field(..., description="租赁店名称")
    location: str = Field(..., description="位置")
    bicycle_type: str = Field(..., description="自行车类型")
    price_1day_yen: Optional[int] = Field(None, description="1日租金（日元）")
    price_4hours_yen: Optional[int] = Field(None, description="4小时租金（日元）")
    price_overnight_yen: Optional[int] = Field(None, description="过夜租金（日元）")
    operating_hours: str = Field(..., description="营业时间")
    contact: str = Field(..., description="联系方式")
    notes: Optional[str] = Field(None, description="备注")
    equipment: Optional[str] = Field(None, description="设备")
    insurance: Optional[str] = Field(None, description="保险")

class BusSchedule(BaseModel):
    """巴士时刻表模型"""
    bus_type: str = Field(..., description="巴士类型")
    route: str = Field(..., description="路线")
    departure_stop: str = Field(..., description="出发站")
    arrival_stop: str = Field(..., description="到达站")
    departure_time: Optional[str] = Field(None, description="出发时间")
    arrival_time: Optional[str] = Field(None, description="到达时间")
    fare_adult_yen: Optional[int] = Field(None, description="成人票价（日元）")
    fare_child_yen: Optional[int] = Field(None, description="儿童票价（日元）")
    operator: str = Field(..., description="运营商")
    notes: Optional[str] = Field(None, description="备注")
    frequency: Optional[str] = Field(None, description="班次频率")

class OtherTransport(BaseModel):
    """其他交通方式模型"""
    transport_type: str = Field(..., description="交通类型")
    service_name: str = Field(..., description="服务名称")
    location: str = Field(..., description="位置")
    price_yen: Optional[int] = Field(None, description="价格（日元）")
    operating_hours: str = Field(..., description="营业时间")
    contact: str = Field(..., description="联系方式")
    notes: Optional[str] = Field(None, description="备注")
    capacity: Optional[str] = Field(None, description="容量")
    requirements: Optional[str] = Field(None, description="要求")

class IslandTransport(BaseModel):
    """岛屿交通信息模型"""
    island_name: str = Field(..., description="岛屿名称")
    island_name_en: str = Field(..., description="岛屿英文名称")
    bicycle_rentals: List[BicycleRental] = Field(default=[], description="自行车租赁信息")
    bus_schedules: List[BusSchedule] = Field(default=[], description="巴士时刻表")
    other_transports: List[OtherTransport] = Field(default=[], description="其他交通方式")
    summary: Optional[str] = Field(None, description="交通信息总结")

class IslandTransportSummary(BaseModel):
    """岛屿交通信息摘要"""
    island_name: str = Field(..., description="岛屿名称")
    island_name_en: str = Field(..., description="岛屿英文名称")
    has_bus: bool = Field(..., description="是否有巴士")
    has_bicycle_rental: bool = Field(..., description="是否有自行车租赁")
    bicycle_rental_count: int = Field(..., description="自行车租赁店数量")
    min_bicycle_price: Optional[int] = Field(None, description="最低自行车租金")
    transport_types: List[str] = Field(..., description="可用交通类型")
    special_notes: Optional[str] = Field(None, description="特殊说明")

class RentalSearchRequest(BaseModel):
    """租赁搜索请求模型"""
    island_name: Optional[str] = Field(None, description="岛屿名称")
    transport_type: Optional[TransportType] = Field(None, description="交通类型")
    max_price: Optional[int] = Field(None, description="最大价格")
    rental_type: Optional[str] = Field(None, description="租赁类型（如：电动自行车、普通自行车）")
