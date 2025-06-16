import pandas as pd
from typing import List, Optional
from ..models.company import Company
from ..core.data_loader import data_loader
import logging

logger = logging.getLogger(__name__)

class CompanyService:
    """船运公司服务"""
    
    def __init__(self):
        self.data_loader = data_loader
    
    def get_all_companies(self) -> List[Company]:
        """获取所有船运公司"""
        try:
            df = self.data_loader.get_companies_data()
            
            if df.empty:
                return []
            
            companies = []
            for _, row in df.iterrows():
                try:
                    company = Company(
                        name=str(row['公司名称']),
                        phone=str(row['联系电话']),
                        website=str(row['网站']),
                        main_routes=str(row['主要航线']),
                        notes=str(row['备注'])
                    )
                    companies.append(company)
                except Exception as e:
                    logger.warning(f"Error converting row to company: {e}")
                    continue
            
            return companies
            
        except Exception as e:
            logger.error(f"Error getting companies: {e}")
            return []
    
    def search_companies(self, query: Optional[str] = None) -> List[Company]:
        """搜索船运公司"""
        companies = self.get_all_companies()
        
        if not query:
            return companies
        
        # 简单的文本搜索
        filtered_companies = []
        for company in companies:
            if (query.lower() in company.name.lower() or 
                query.lower() in company.main_routes.lower()):
                filtered_companies.append(company)
        
        return filtered_companies
    
    def get_company_by_name(self, name: str) -> Optional[Company]:
        """根据名称获取公司"""
        companies = self.get_all_companies()
        
        for company in companies:
            if company.name == name:
                return company
        
        return None

# 全局服务实例
company_service = CompanyService()
