import pandas as pd
from typing import List, Optional
from ..models.port import Port
from ..core.data_loader import data_loader
import logging

logger = logging.getLogger(__name__)

class PortService:
    """港口服务"""
    
    def __init__(self):
        self.data_loader = data_loader
    
    def get_all_ports(self) -> List[Port]:
        """获取所有港口"""
        try:
            df = self.data_loader.get_ports_data()
            
            if df.empty:
                return []
            
            ports = []
            for _, row in df.iterrows():
                try:
                    port = Port(
                        name=str(row['港口名称']),
                        island=str(row['所在岛屿']),
                        address=str(row['地址']),
                        features=str(row['特点']),
                        connections=str(row['连接岛屿'])
                    )
                    ports.append(port)
                except Exception as e:
                    logger.warning(f"Error converting row to port: {e}")
                    continue
            
            return ports
            
        except Exception as e:
            logger.error(f"Error getting ports: {e}")
            return []
    
    def search_ports(self, query: Optional[str] = None) -> List[Port]:
        """搜索港口"""
        ports = self.get_all_ports()
        
        if not query:
            return ports
        
        # 简单的文本搜索
        filtered_ports = []
        for port in ports:
            if (query.lower() in port.name.lower() or 
                query.lower() in port.island.lower() or
                query.lower() in port.address.lower()):
                filtered_ports.append(port)
        
        return filtered_ports
    
    def get_port_by_name(self, name: str) -> Optional[Port]:
        """根据名称获取港口"""
        ports = self.get_all_ports()
        
        for port in ports:
            if port.name == name:
                return port
        
        return None

# 全局服务实例
port_service = PortService()
