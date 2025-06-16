#!/usr/bin/env python3
"""
AI回复验证服务 - 验证AI回复中的具体信息是否准确
"""

import re
import logging
from typing import Dict, List, Any, Tuple
from .data_processor import data_processor

logger = logging.getLogger(__name__)

class ResponseVerifier:
    """AI回复验证器"""
    
    def __init__(self):
        self.routes_data = None
        self.ports_data = None
        self.companies_data = None
        self.load_data()
    
    def load_data(self):
        """加载验证数据"""
        try:
            self.routes_data = data_processor.load_ferry_routes()
            self.ports_data = data_processor.load_ports()
            self.companies_data = data_processor.load_companies()
            logger.info(f"Loaded verification data: {len(self.routes_data)} routes, {len(self.ports_data)} ports, {len(self.companies_data)} companies")
        except Exception as e:
            logger.error(f"Failed to load verification data: {e}")
            self.routes_data = []
            self.ports_data = []
            self.companies_data = []
    
    def extract_time_info(self, text: str) -> List[str]:
        """提取文本中的时间信息"""
        # 匹配时间格式：HH:MM
        time_pattern = r'\b\d{1,2}:\d{2}\b'
        times = re.findall(time_pattern, text)
        return times
    
    def extract_price_info(self, text: str) -> List[str]:
        """提取文本中的价格信息"""
        # 匹配价格格式：数字+円
        price_pattern = r'\d+円'
        prices = re.findall(price_pattern, text)
        return prices
    
    def extract_company_info(self, text: str) -> List[str]:
        """提取文本中的公司信息"""
        companies = []
        company_keywords = ['四国汽船', '豊島フェリー', '小豆島豊島フェリー', 'ジャンボフェリー', '四国フェリー', '国際両備フェリー', '雌雄島海運']
        
        for company in company_keywords:
            if company in text:
                companies.append(company)
        
        return companies
    
    def extract_route_info(self, text: str) -> List[Dict[str, str]]:
        """提取文本中的路线信息"""
        routes = []
        
        # 匹配路线格式：地点→地点 时间-时间
        route_pattern = r'([^→\s]+)→([^→\s]+)\s*(\d{1,2}:\d{2})-(\d{1,2}:\d{2})'
        matches = re.findall(route_pattern, text)
        
        for match in matches:
            routes.append({
                'departure': match[0].strip(),
                'arrival': match[1].strip(),
                'departure_time': match[2],
                'arrival_time': match[3]
            })
        
        # 也匹配其他格式
        route_pattern2 = r'([^→\s]+).*?(\d{1,2}:\d{2}).*?([^→\s]+).*?(\d{1,2}:\d{2})'
        
        return routes
    
    def verify_time_info(self, times: List[str]) -> Dict[str, Any]:
        """验证时间信息"""
        verified_times = []
        unverified_times = []
        
        for time_str in times:
            found = False
            for route in self.routes_data:
                if (route.get('departure_time') == time_str or 
                    route.get('arrival_time') == time_str):
                    verified_times.append({
                        'time': time_str,
                        'route': f"{route.get('departure_port')} → {route.get('arrival_port')}",
                        'company': route.get('company')
                    })
                    found = True
                    break
            
            if not found:
                unverified_times.append(time_str)
        
        return {
            'verified': verified_times,
            'unverified': unverified_times,
            'accuracy_rate': len(verified_times) / len(times) if times else 0
        }
    
    def verify_price_info(self, prices: List[str]) -> Dict[str, Any]:
        """验证价格信息"""
        verified_prices = []
        unverified_prices = []
        
        for price_str in prices:
            found = False
            for route in self.routes_data:
                if (route.get('adult_fare') == price_str or 
                    route.get('child_fare') == price_str):
                    verified_prices.append({
                        'price': price_str,
                        'route': f"{route.get('departure_port')} → {route.get('arrival_port')}",
                        'company': route.get('company')
                    })
                    found = True
                    break
            
            if not found:
                unverified_prices.append(price_str)
        
        return {
            'verified': verified_prices,
            'unverified': unverified_prices,
            'accuracy_rate': len(verified_prices) / len(prices) if prices else 0
        }
    
    def verify_company_info(self, companies: List[str]) -> Dict[str, Any]:
        """验证公司信息"""
        verified_companies = []
        unverified_companies = []
        
        # 获取数据库中的所有公司
        db_companies = set()
        for route in self.routes_data:
            company = route.get('company', '')
            if company:
                db_companies.add(company)
        
        for company in companies:
            if company in db_companies:
                # 统计该公司的路线数量
                route_count = sum(1 for route in self.routes_data if route.get('company') == company)
                verified_companies.append({
                    'company': company,
                    'route_count': route_count
                })
            else:
                unverified_companies.append(company)
        
        return {
            'verified': verified_companies,
            'unverified': unverified_companies,
            'accuracy_rate': len(verified_companies) / len(companies) if companies else 0
        }
    
    def verify_specific_route(self, departure: str, arrival: str, dep_time: str = None, arr_time: str = None) -> Dict[str, Any]:
        """验证具体路线信息"""
        matching_routes = []
        
        for route in self.routes_data:
            dep_port = route.get('departure_port', '')
            arr_port = route.get('arrival_port', '')
            
            # 检查港口匹配（支持部分匹配）
            dep_match = departure in dep_port or dep_port in departure
            arr_match = arrival in arr_port or arr_port in arrival
            
            if dep_match and arr_match:
                route_match = {
                    'departure_port': dep_port,
                    'arrival_port': arr_port,
                    'departure_time': route.get('departure_time'),
                    'arrival_time': route.get('arrival_time'),
                    'company': route.get('company'),
                    'adult_fare': route.get('adult_fare'),
                    'time_match': True
                }
                
                # 如果指定了时间，检查时间匹配
                if dep_time:
                    route_match['time_match'] = route.get('departure_time') == dep_time
                if arr_time and route_match['time_match']:
                    route_match['time_match'] = route.get('arrival_time') == arr_time
                
                matching_routes.append(route_match)
        
        return {
            'found_routes': matching_routes,
            'exact_match': any(route['time_match'] for route in matching_routes) if dep_time or arr_time else len(matching_routes) > 0,
            'route_count': len(matching_routes)
        }
    
    def verify_response(self, ai_response: str) -> Dict[str, Any]:
        """验证AI回复的完整性和准确性"""
        verification_result = {
            'original_response': ai_response,
            'verification_summary': {},
            'detailed_verification': {},
            'overall_accuracy': 0,
            'verified_info_count': 0,
            'total_info_count': 0
        }
        
        try:
            # 提取各类信息
            times = self.extract_time_info(ai_response)
            prices = self.extract_price_info(ai_response)
            companies = self.extract_company_info(ai_response)
            
            # 验证各类信息
            time_verification = self.verify_time_info(times)
            price_verification = self.verify_price_info(prices)
            company_verification = self.verify_company_info(companies)
            
            # 统计验证结果
            verified_count = (len(time_verification['verified']) + 
                            len(price_verification['verified']) + 
                            len(company_verification['verified']))
            
            total_count = len(times) + len(prices) + len(companies)
            
            verification_result.update({
                'detailed_verification': {
                    'times': time_verification,
                    'prices': price_verification,
                    'companies': company_verification
                },
                'verification_summary': {
                    'times_accuracy': time_verification['accuracy_rate'],
                    'prices_accuracy': price_verification['accuracy_rate'],
                    'companies_accuracy': company_verification['accuracy_rate']
                },
                'verified_info_count': verified_count,
                'total_info_count': total_count,
                'overall_accuracy': verified_count / total_count if total_count > 0 else 1.0
            })
            
        except Exception as e:
            logger.error(f"Error during response verification: {e}")
            verification_result['error'] = str(e)
        
        return verification_result
    
    def format_verification_message(self, verification_result: Dict[str, Any]) -> str:
        """格式化验证结果为用户友好的消息"""
        if verification_result['total_info_count'] == 0:
            return "\n\n📋 信息验证：本回复未包含具体的船班时间、票价或公司信息。"
        
        accuracy = verification_result['overall_accuracy']
        verified_count = verification_result['verified_info_count']
        total_count = verification_result['total_info_count']
        
        message = f"\n\n📋 信息验证结果：{verified_count}/{total_count} 项信息已验证 (准确率: {accuracy*100:.1f}%)"
        
        # 详细验证信息
        details = verification_result['detailed_verification']
        
        if details['times']['verified']:
            message += f"\n✅ 已验证时间: {', '.join([t['time'] for t in details['times']['verified']])}"
        
        if details['times']['unverified']:
            message += f"\n⚠️  未验证时间: {', '.join(details['times']['unverified'])}"
        
        if details['prices']['verified']:
            message += f"\n✅ 已验证票价: {', '.join([p['price'] for p in details['prices']['verified']])}"
        
        if details['prices']['unverified']:
            message += f"\n⚠️  未验证票价: {', '.join(details['prices']['unverified'])}"
        
        if details['companies']['verified']:
            message += f"\n✅ 已验证公司: {', '.join([c['company'] for c in details['companies']['verified']])}"
        
        if details['companies']['unverified']:
            message += f"\n⚠️  未验证公司: {', '.join(details['companies']['unverified'])}"
        
        if accuracy < 0.8:
            message += f"\n\n⚠️  建议：部分信息未能验证，请在出行前查询官方网站确认最新信息。"
        
        return message

# 全局实例
response_verifier = ResponseVerifier()
