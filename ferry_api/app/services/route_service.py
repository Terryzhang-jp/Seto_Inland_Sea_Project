import pandas as pd
from typing import List, Optional, Tuple
from ..models.route import FerryRoute, RouteSearchParams
from ..core.data_loader import data_loader
import logging

logger = logging.getLogger(__name__)

class RouteService:
    """航线服务"""
    
    def __init__(self):
        self.data_loader = data_loader
    
    def search_routes(self, params: RouteSearchParams) -> Tuple[List[FerryRoute], int]:
        """搜索航线"""
        try:
            df = self.data_loader.get_timetable_data()
            
            if df.empty:
                return [], 0
            
            # 应用搜索过滤器
            filtered_df = self._apply_filters(df, params)
            
            # 计算总数
            total = len(filtered_df)
            
            # 应用分页
            start_idx = (params.page - 1) * params.limit
            end_idx = start_idx + params.limit
            paginated_df = filtered_df.iloc[start_idx:end_idx]
            
            # 转换为模型
            routes = self._dataframe_to_routes(paginated_df)
            
            return routes, total
            
        except Exception as e:
            logger.error(f"Error searching routes: {e}")
            return [], 0
    
    def _apply_filters(self, df: pd.DataFrame, params: RouteSearchParams) -> pd.DataFrame:
        """应用搜索过滤器"""
        filtered_df = df.copy()
        
        # 出发地过滤
        if params.departure:
            filtered_df = filtered_df[
                filtered_df['出发地'].str.contains(params.departure, na=False, case=False)
            ]
        
        # 到达地过滤
        if params.arrival:
            filtered_df = filtered_df[
                filtered_df['到达地'].str.contains(params.arrival, na=False, case=False)
            ]
        
        # 公司过滤
        if params.company:
            filtered_df = filtered_df[
                filtered_df['运营公司'].str.contains(params.company, na=False, case=False)
            ]
        
        # 时间范围过滤
        if params.departure_time_start:
            filtered_df = filtered_df[
                filtered_df['出发时间'] >= params.departure_time_start
            ]
        
        if params.departure_time_end:
            filtered_df = filtered_df[
                filtered_df['出发时间'] <= params.departure_time_end
            ]
        
        # 车辆过滤
        if params.allows_vehicles is not None:
            vehicle_filter = "是" if params.allows_vehicles else "否"
            filtered_df = filtered_df[
                filtered_df['允许车辆'] == vehicle_filter
            ]
        
        # 自行车过滤
        if params.allows_bicycles is not None:
            bicycle_filter = "是" if params.allows_bicycles else "否"
            filtered_df = filtered_df[
                filtered_df['允许自行车'] == bicycle_filter
            ]
        
        return filtered_df
    
    def _dataframe_to_routes(self, df: pd.DataFrame) -> List[FerryRoute]:
        """将DataFrame转换为FerryRoute列表"""
        routes = []
        
        for _, row in df.iterrows():
            try:
                route = FerryRoute(
                    departure_port=str(row['出发地']),
                    arrival_port=str(row['到达地']),
                    departure_time=str(row['出发时间']),
                    arrival_time=str(row['到达时间']),
                    company=str(row['运营公司']),
                    ship_type=str(row['船只类型']),
                    allows_vehicles=row['允许车辆'] == "是",
                    allows_bicycles=row['允许自行车'] == "是",
                    adult_fare=str(row['大人票价']),
                    child_fare=str(row['小人票价']),
                    operating_days=str(row['运营日期']),
                    notes=str(row['备注']) if pd.notna(row['备注']) else None
                )
                routes.append(route)
            except Exception as e:
                logger.warning(f"Error converting row to route: {e}")
                continue
        
        return routes
    
    def get_popular_routes(self) -> List[dict]:
        """获取热门路线"""
        popular_routes = [
            {"departure": "高松", "arrival": "直島", "description": "高松到直島 - 艺术之岛"},
            {"departure": "宇野", "arrival": "直島", "description": "宇野到直島 - 最便捷路线"},
            {"departure": "高松", "arrival": "小豆島", "description": "高松到小豆島 - 橄榄之岛"},
            {"departure": "宇野", "arrival": "豊島", "description": "宇野到豊島 - 美术馆之岛"},
            {"departure": "直島", "arrival": "豊島", "description": "直島到豊島 - 艺术跳岛"},
            {"departure": "豊島", "arrival": "犬島", "description": "豊島到犬島 - 精炼所美术馆"},
        ]
        
        return popular_routes

# 全局服务实例
route_service = RouteService()
