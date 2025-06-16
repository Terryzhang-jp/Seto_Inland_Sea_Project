import pandas as pd
from typing import Dict, List
from pathlib import Path
import logging
from .config import settings

logger = logging.getLogger(__name__)

class DataLoader:
    """数据加载器"""
    
    def __init__(self):
        self.timetable_df: pd.DataFrame = None
        self.companies_df: pd.DataFrame = None
        self.ports_df: pd.DataFrame = None
        self.fares_df: pd.DataFrame = None
        self._load_all_data()
    
    def _load_all_data(self):
        """加载所有CSV数据"""
        try:
            # 加载时间表数据
            if settings.TIMETABLE_CSV.exists():
                self.timetable_df = pd.read_csv(settings.TIMETABLE_CSV)
                logger.info(f"Loaded {len(self.timetable_df)} timetable records")
            else:
                logger.error(f"Timetable CSV not found: {settings.TIMETABLE_CSV}")
            
            # 加载公司数据
            if settings.COMPANIES_CSV.exists():
                self.companies_df = pd.read_csv(settings.COMPANIES_CSV)
                logger.info(f"Loaded {len(self.companies_df)} company records")
            else:
                logger.error(f"Companies CSV not found: {settings.COMPANIES_CSV}")
            
            # 加载港口数据
            if settings.PORTS_CSV.exists():
                self.ports_df = pd.read_csv(settings.PORTS_CSV)
                logger.info(f"Loaded {len(self.ports_df)} port records")
            else:
                logger.error(f"Ports CSV not found: {settings.PORTS_CSV}")
            
            # 加载票价数据
            if settings.FARES_CSV.exists():
                self.fares_df = pd.read_csv(settings.FARES_CSV)
                logger.info(f"Loaded {len(self.fares_df)} fare records")
            else:
                logger.error(f"Fares CSV not found: {settings.FARES_CSV}")
                
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def get_timetable_data(self) -> pd.DataFrame:
        """获取时间表数据"""
        return self.timetable_df.copy() if self.timetable_df is not None else pd.DataFrame()
    
    def get_companies_data(self) -> pd.DataFrame:
        """获取公司数据"""
        return self.companies_df.copy() if self.companies_df is not None else pd.DataFrame()
    
    def get_ports_data(self) -> pd.DataFrame:
        """获取港口数据"""
        return self.ports_df.copy() if self.ports_df is not None else pd.DataFrame()
    
    def get_fares_data(self) -> pd.DataFrame:
        """获取票价数据"""
        return self.fares_df.copy() if self.fares_df is not None else pd.DataFrame()
    
    def reload_data(self):
        """重新加载数据"""
        self._load_all_data()

# 全局数据加载器实例
data_loader = DataLoader()
