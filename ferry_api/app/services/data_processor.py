import pandas as pd
import json
import logging
from typing import List, Dict, Any, Tuple
from .vector_store import vector_store

logger = logging.getLogger(__name__)

class DataProcessor:
    """数据预处理服务"""
    
    def __init__(self):
        self.routes_data = None
        self.ports_data = None
        self.companies_data = None
        self.popular_routes_data = None
    
    def load_data(self):
        """加载所有数据"""
        try:
            # 加载船班数据
            self.routes_data = pd.read_csv('data/ferry_routes.csv')
            logger.info(f"Loaded {len(self.routes_data)} ferry routes")
            
            # 加载港口数据
            self.ports_data = pd.read_csv('data/ports.csv')
            logger.info(f"Loaded {len(self.ports_data)} ports")
            
            # 加载公司数据
            self.companies_data = pd.read_csv('data/companies.csv')
            logger.info(f"Loaded {len(self.companies_data)} companies")
            
            # 加载热门路线数据
            with open('data/popular_routes.json', 'r', encoding='utf-8') as f:
                self.popular_routes_data = json.load(f)
            logger.info(f"Loaded {len(self.popular_routes_data)} popular routes")
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def create_route_documents(self) -> Tuple[List[str], List[Dict[str, Any]]]:
        """创建船班路线文档"""
        documents = []
        metadatas = []
        
        for _, route in self.routes_data.iterrows():
            # 创建详细的文档描述
            doc = f"""
船班路线：{route['departure_port']} 到 {route['arrival_port']}
出发时间：{route['departure_time']}
到达时间：{route['arrival_time']}
船运公司：{route['company']}
船只类型：{route['ship_type']}
大人票价：{route['adult_fare']}
小人票价：{route['child_fare']}
运营日期：{route['operating_days']}
车辆载运：{'允许' if route['allows_vehicles'] else '不允许'}
自行车载运：{'允许' if route['allows_bicycles'] else '不允许'}
备注：{route.get('notes', '无')}
            """.strip()
            
            metadata = {
                'type': 'route',
                'departure_port': route['departure_port'],
                'arrival_port': route['arrival_port'],
                'company': route['company'],
                'departure_time': route['departure_time'],
                'arrival_time': route['arrival_time'],
                'allows_vehicles': route['allows_vehicles'],
                'allows_bicycles': route['allows_bicycles'],
                'adult_fare': route['adult_fare'],
                'ship_type': route['ship_type']
            }
            
            documents.append(doc)
            metadatas.append(metadata)
        
        return documents, metadatas
    
    def create_port_documents(self) -> Tuple[List[str], List[Dict[str, Any]]]:
        """创建港口信息文档"""
        documents = []
        metadatas = []
        
        for _, port in self.ports_data.iterrows():
            doc = f"""
港口名称：{port['name']}
所属岛屿：{port['island']}
地址：{port['address']}
港口特色：{port['features']}
连接岛屿：{port['connections']}
            """.strip()
            
            metadata = {
                'type': 'port',
                'name': port['name'],
                'island': port['island'],
                'address': port['address'],
                'features': port['features'],
                'connections': port['connections']
            }
            
            documents.append(doc)
            metadatas.append(metadata)
        
        return documents, metadatas
    
    def create_company_documents(self) -> Tuple[List[str], List[Dict[str, Any]]]:
        """创建公司信息文档"""
        documents = []
        metadatas = []
        
        for _, company in self.companies_data.iterrows():
            doc = f"""
船运公司：{company['name']}
联系电话：{company['phone']}
官方网站：{company['website']}
主要航线：{company['main_routes']}
备注信息：{company['notes']}
            """.strip()
            
            metadata = {
                'type': 'company',
                'name': company['name'],
                'phone': company['phone'],
                'website': company['website'],
                'main_routes': company['main_routes']
            }
            
            documents.append(doc)
            metadatas.append(metadata)
        
        return documents, metadatas
    
    def create_popular_route_documents(self) -> Tuple[List[str], List[Dict[str, Any]]]:
        """创建热门路线文档"""
        documents = []
        metadatas = []
        
        for route in self.popular_routes_data:
            doc = f"""
热门跳岛路线：{route['departure']} 到 {route['arrival']}
路线描述：{route['description']}
推荐理由：这是一条受欢迎的跳岛路线，适合游客体验瀬户内海的魅力。
            """.strip()
            
            metadata = {
                'type': 'popular_route',
                'departure': route['departure'],
                'arrival': route['arrival'],
                'description': route['description']
            }
            
            documents.append(doc)
            metadatas.append(metadata)
        
        return documents, metadatas
    
    def create_general_info_documents(self) -> Tuple[List[str], List[Dict[str, Any]]]:
        """创建通用信息文档"""
        documents = []
        metadatas = []
        
        # 添加系统介绍
        system_info = """
瀬户内海船班查询系统提供以下服务：
1. 船班时间查询：查询各岛屿间的船班时间表
2. 票价信息：提供大人和小人的票价信息
3. 载运服务：查询是否可以载运车辆和自行车
4. 跳岛规划：帮助规划多岛屿的旅行路线
5. 公司信息：提供各船运公司的联系方式和服务信息

主要覆盖岛屿：
- 艺术岛屿：直島（现代艺术）、豊島（豊島美术馆）、犬島（犬島精炼所美术馆）
- 自然岛屿：小豆島（橄榄之岛）、女木島（鬼岛传说）、男木島（猫咪天堂）
- 本州港口：高松、宇野、神戸、新岡山港

主要船运公司：四国汽船、ジャンボフェリー、国際両備フェリー、四国フェリー、雌雄島海運、豊島フェリー、小豆島豊島フェリー
        """.strip()
        
        documents.append(system_info)
        metadatas.append({
            'type': 'system_info',
            'category': 'general'
        })
        
        return documents, metadatas
    
    async def process_and_store_all_data(self):
        """处理并存储所有数据到向量数据库"""
        try:
            # 加载数据
            self.load_data()
            
            all_documents = []
            all_metadatas = []
            
            # 处理各类数据
            route_docs, route_metas = self.create_route_documents()
            all_documents.extend(route_docs)
            all_metadatas.extend(route_metas)
            
            port_docs, port_metas = self.create_port_documents()
            all_documents.extend(port_docs)
            all_metadatas.extend(port_metas)
            
            company_docs, company_metas = self.create_company_documents()
            all_documents.extend(company_docs)
            all_metadatas.extend(company_metas)
            
            popular_docs, popular_metas = self.create_popular_route_documents()
            all_documents.extend(popular_docs)
            all_metadatas.extend(popular_metas)
            
            general_docs, general_metas = self.create_general_info_documents()
            all_documents.extend(general_docs)
            all_metadatas.extend(general_metas)
            
            # 存储到向量数据库
            await vector_store.add_documents(all_documents, all_metadatas)
            
            logger.info(f"Successfully processed and stored {len(all_documents)} documents")
            
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            raise

# 全局实例
data_processor = DataProcessor()
