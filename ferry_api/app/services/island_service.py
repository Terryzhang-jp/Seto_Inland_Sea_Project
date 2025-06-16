import pandas as pd
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging
from ..models.island import (
    IslandTransport, BicycleRental, BusSchedule, OtherTransport,
    IslandTransportSummary, TransportType
)

logger = logging.getLogger(__name__)

class IslandService:
    """岛屿交通信息服务"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "islands"
        self.islands_data = {}
        self.load_all_islands_data()
    
    def load_all_islands_data(self):
        """加载所有岛屿数据"""
        try:
            island_folders = {
                "naoshima": "直岛",
                "shodoshima": "小豆岛", 
                "teshima": "丰岛",
                "megijima": "女木岛",
                "ogijima": "男木岛"
            }
            
            for folder_name, island_name in island_folders.items():
                island_path = self.data_dir / folder_name
                if island_path.exists():
                    self.islands_data[folder_name] = self._load_island_data(island_path, island_name, folder_name)
                    logger.info(f"Loaded data for {island_name}")
                else:
                    logger.warning(f"Island data folder not found: {island_path}")
                    
        except Exception as e:
            logger.error(f"Error loading islands data: {e}")
    
    def _load_island_data(self, island_path: Path, island_name: str, island_name_en: str) -> IslandTransport:
        """加载单个岛屿数据"""
        try:
            # 加载自行车租赁数据
            bicycle_rentals = []
            bicycle_file = island_path / "bicycle_rental.csv"
            if bicycle_file.exists():
                df = pd.read_csv(bicycle_file)
                for _, row in df.iterrows():
                    if row['shop_name'] != 'no_bicycle_rental':  # 排除无租赁服务的记录
                        bicycle_rentals.append(BicycleRental(
                            shop_name=str(row['shop_name']),
                            location=str(row['location']),
                            bicycle_type=str(row['bicycle_type']),
                            price_1day_yen=self._parse_price(
                                row.get('price_1day_yen') or
                                row.get('price_per_day_yen') or
                                row.get('price_day_yen')
                            ),
                            price_4hours_yen=self._parse_price(row.get('price_4hours_yen')),
                            price_overnight_yen=self._parse_price(row.get('price_overnight_yen')),
                            operating_hours=str(row['operating_hours']),
                            contact=str(row['contact']),
                            notes=str(row.get('notes', '')),
                            equipment=str(row.get('equipment', '')),
                            insurance=str(row.get('insurance', ''))
                        ))
            
            # 加载巴士时刻表数据
            bus_schedules = []
            bus_file = island_path / "bus_timetable.csv"
            if bus_file.exists():
                df = pd.read_csv(bus_file)
                for _, row in df.iterrows():
                    # 处理不同的列名格式
                    bus_type = row.get('bus_type') or row.get('bus_line') or row.get('transport_type', '')
                    if bus_type != 'no_bus' and str(bus_type) != 'nan':  # 排除无巴士服务的记录
                        bus_schedules.append(BusSchedule(
                            bus_type=str(bus_type),
                            route=str(row['route']),
                            departure_stop=str(row['departure_stop']),
                            arrival_stop=str(row['arrival_stop']),
                            departure_time=str(row.get('departure_time', '')),
                            arrival_time=str(row.get('arrival_time', '')),
                            fare_adult_yen=self._parse_price(row.get('fare_adult_yen') or row.get('fare_yen')),
                            fare_child_yen=self._parse_price(row.get('fare_child_yen')),
                            operator=str(row['operator']),
                            notes=str(row.get('notes', '')),
                            frequency=str(row.get('frequency', ''))
                        ))
            
            # 加载其他交通方式数据
            other_transports = []
            other_file = island_path / "other_transport.csv"
            if other_file.exists():
                df = pd.read_csv(other_file)
                for _, row in df.iterrows():
                    other_transports.append(OtherTransport(
                        transport_type=str(row['transport_type']),
                        service_name=str(row['service_name']),
                        location=str(row['location']),
                        price_yen=self._parse_price(row.get('price_yen')),
                        operating_hours=str(row['operating_hours']),
                        contact=str(row['contact']),
                        notes=str(row.get('notes', '')),
                        capacity=str(row.get('capacity', '')),
                        requirements=str(row.get('requirements', ''))
                    ))
            
            # 读取总结信息
            summary = ""
            summary_file = island_path / "island_transport_summary.md"
            if summary_file.exists():
                with open(summary_file, 'r', encoding='utf-8') as f:
                    summary = f.read()
            
            return IslandTransport(
                island_name=island_name,
                island_name_en=island_name_en,
                bicycle_rentals=bicycle_rentals,
                bus_schedules=bus_schedules,
                other_transports=other_transports,
                summary=summary
            )
            
        except Exception as e:
            logger.error(f"Error loading data for {island_name}: {e}")
            return IslandTransport(
                island_name=island_name,
                island_name_en=island_name_en,
                bicycle_rentals=[],
                bus_schedules=[],
                other_transports=[],
                summary=""
            )
    
    def _parse_price(self, price_value) -> Optional[int]:
        """解析价格值"""
        if pd.isna(price_value) or price_value == '要確認' or price_value == '-':
            return None
        try:
            # 移除非数字字符并转换为整数
            price_str = str(price_value).replace('円', '').replace(',', '').replace('日元', '')
            if price_str.isdigit():
                return int(price_str)
            return None
        except:
            return None
    
    def get_all_islands(self) -> List[IslandTransport]:
        """获取所有岛屿交通信息"""
        return list(self.islands_data.values())
    
    def get_island_by_name(self, island_name: str) -> Optional[IslandTransport]:
        """根据岛屿名称获取交通信息"""
        # 支持中文名和英文名查询
        for island_data in self.islands_data.values():
            if island_data.island_name == island_name or island_data.island_name_en == island_name:
                return island_data
        return None
    
    def get_islands_summary(self) -> List[IslandTransportSummary]:
        """获取所有岛屿交通信息摘要"""
        summaries = []
        for island_data in self.islands_data.values():
            # 计算最低自行车租金
            min_price = None
            if island_data.bicycle_rentals:
                prices = [rental.price_1day_yen for rental in island_data.bicycle_rentals if rental.price_1day_yen]
                if prices:
                    min_price = min(prices)
            
            # 获取交通类型
            transport_types = set()
            if island_data.bus_schedules:
                transport_types.add("巴士")
            if island_data.bicycle_rentals:
                transport_types.add("自行车租赁")
            
            for transport in island_data.other_transports:
                if transport.transport_type == "taxi":
                    transport_types.add("出租车")
                elif transport.transport_type == "car_rental":
                    transport_types.add("汽车租赁")
                elif transport.transport_type == "walking":
                    transport_types.add("步行")
                elif transport.transport_type == "motorbike_rental":
                    transport_types.add("摩托车租赁")
            
            # 特殊说明
            special_notes = None
            if island_data.island_name_en == "ogijima":
                special_notes = "只能步行，禁止自行车和汽车"
            elif island_data.island_name_en == "megijima":
                special_notes = "禁止汽车乘入"
            
            summaries.append(IslandTransportSummary(
                island_name=island_data.island_name,
                island_name_en=island_data.island_name_en,
                has_bus=len(island_data.bus_schedules) > 0,
                has_bicycle_rental=len(island_data.bicycle_rentals) > 0,
                bicycle_rental_count=len(island_data.bicycle_rentals),
                min_bicycle_price=min_price,
                transport_types=list(transport_types),
                special_notes=special_notes
            ))
        
        return summaries
    
    def search_bicycle_rentals(self, island_name: Optional[str] = None, 
                             max_price: Optional[int] = None,
                             rental_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """搜索自行车租赁信息"""
        results = []
        
        for island_data in self.islands_data.values():
            # 如果指定了岛屿名称，只搜索该岛屿
            if island_name and island_data.island_name != island_name and island_data.island_name_en != island_name:
                continue
                
            for rental in island_data.bicycle_rentals:
                # 价格过滤
                if max_price and rental.price_1day_yen and rental.price_1day_yen > max_price:
                    continue
                
                # 租赁类型过滤
                if rental_type and rental_type.lower() not in rental.bicycle_type.lower():
                    continue
                
                results.append({
                    "island_name": island_data.island_name,
                    "island_name_en": island_data.island_name_en,
                    "rental_info": rental.dict()
                })
        
        return results

# 创建全局服务实例
island_service = IslandService()
