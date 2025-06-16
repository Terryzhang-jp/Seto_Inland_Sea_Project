#!/usr/bin/env python3
"""
数据准备脚本
将现有数据文件转换为RAG系统需要的格式
"""

import pandas as pd
import json
import os
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def prepare_ferry_routes():
    """准备船班路线数据"""
    try:
        # 读取现有的船班数据
        df = pd.read_csv('data/setouchi_ferry_timetable.csv')
        logger.info(f"读取到 {len(df)} 条船班数据")
        
        # 重命名列以匹配RAG系统期望的格式
        column_mapping = {
            '出发地': 'departure_port',
            '到达地': 'arrival_port',
            '出发时间': 'departure_time',
            '到达时间': 'arrival_time',
            '运营公司': 'company',
            '船只类型': 'ship_type',
            '大人票价': 'adult_fare',
            '小人票价': 'child_fare',
            '运营日期': 'operating_days',
            '允许车辆': 'allows_vehicles',
            '允许自行车': 'allows_bicycles',
            '备注': 'notes'
        }

        # 检查现有列
        logger.info(f"现有列: {list(df.columns)}")

        # 重命名列
        ferry_routes = df.rename(columns=column_mapping)
        
        # 确保必要的列存在
        required_columns = [
            'departure_port', 'arrival_port', 'departure_time', 'arrival_time',
            'company', 'ship_type', 'adult_fare', 'child_fare', 'operating_days'
        ]
        
        for col in required_columns:
            if col not in ferry_routes.columns:
                if col == 'allows_vehicles':
                    ferry_routes[col] = True  # 默认允许车辆
                elif col == 'allows_bicycles':
                    ferry_routes[col] = True  # 默认允许自行车
                elif col == 'notes':
                    ferry_routes[col] = ''  # 默认无备注
                else:
                    logger.warning(f"缺少必要列: {col}")
        
        # 保存为新文件
        ferry_routes.to_csv('data/ferry_routes.csv', index=False, encoding='utf-8')
        logger.info("船班路线数据准备完成")
        
        return True
        
    except Exception as e:
        logger.error(f"准备船班路线数据失败: {str(e)}")
        return False

def prepare_ports_data():
    """准备港口数据"""
    try:
        # 读取现有的港口数据
        df = pd.read_csv('data/ports_info.csv')
        logger.info(f"读取到 {len(df)} 条港口数据")

        # 重命名列
        column_mapping = {
            '港口名称': 'name',
            '所在岛屿': 'island',
            '地址': 'address',
            '特点': 'features',
            '连接岛屿': 'connections'
        }

        ports_data = df.rename(columns=column_mapping)

        # 确保必要的列存在
        required_columns = ['name', 'island', 'address', 'features', 'connections']

        for col in required_columns:
            if col not in ports_data.columns:
                if col == 'island':
                    ports_data[col] = '未知'
                elif col == 'address':
                    ports_data[col] = '地址待补充'
                elif col == 'features':
                    ports_data[col] = '港口特色待补充'
                elif col == 'connections':
                    ports_data[col] = '连接信息待补充'

        # 只保留需要的列
        ports_data = ports_data[required_columns]

        # 保存为新文件
        ports_data.to_csv('data/ports.csv', index=False, encoding='utf-8')
        logger.info("港口数据准备完成")

        return True

    except Exception as e:
        logger.error(f"准备港口数据失败: {str(e)}")
        return False

def prepare_companies_data():
    """准备公司数据"""
    try:
        # 读取现有的公司数据
        df = pd.read_csv('data/ferry_companies_info.csv')
        logger.info(f"读取到 {len(df)} 条公司数据")

        # 重命名列
        column_mapping = {
            '公司名称': 'name',
            '联系电话': 'phone',
            '官方网站': 'website',
            '主要航线': 'main_routes',
            '备注': 'notes'
        }

        companies_data = df.rename(columns=column_mapping)

        # 确保必要的列存在
        required_columns = ['name', 'phone', 'website', 'main_routes', 'notes']

        for col in required_columns:
            if col not in companies_data.columns:
                if col == 'phone':
                    companies_data[col] = '电话待补充'
                elif col == 'website':
                    companies_data[col] = '网站待补充'
                elif col == 'main_routes':
                    companies_data[col] = '主要航线待补充'
                elif col == 'notes':
                    companies_data[col] = ''

        # 只保留需要的列
        companies_data = companies_data[required_columns]

        # 保存为新文件
        companies_data.to_csv('data/companies.csv', index=False, encoding='utf-8')
        logger.info("公司数据准备完成")

        return True

    except Exception as e:
        logger.error(f"准备公司数据失败: {str(e)}")
        return False

def prepare_popular_routes():
    """准备热门路线数据"""
    try:
        # 创建热门路线数据
        popular_routes = [
            {
                "departure": "高松",
                "arrival": "直島",
                "description": "最受欢迎的艺术岛屿路线，可欣赏现代艺术作品"
            },
            {
                "departure": "高松",
                "arrival": "豊島",
                "description": "豊島美术馆所在地，自然与艺术的完美结合"
            },
            {
                "departure": "高松",
                "arrival": "小豆島",
                "description": "橄榄之岛，可体验地中海风情"
            },
            {
                "departure": "宇野",
                "arrival": "直島",
                "description": "从本州出发的便捷艺术岛屿路线"
            },
            {
                "departure": "直島",
                "arrival": "豊島",
                "description": "艺术岛屿间的跳岛路线"
            },
            {
                "departure": "高松",
                "arrival": "女木島",
                "description": "鬼岛传说的神秘岛屿"
            }
        ]
        
        # 保存为JSON文件
        with open('data/popular_routes.json', 'w', encoding='utf-8') as f:
            json.dump(popular_routes, f, ensure_ascii=False, indent=2)
        
        logger.info(f"热门路线数据准备完成，共 {len(popular_routes)} 条")
        return True
        
    except Exception as e:
        logger.error(f"准备热门路线数据失败: {str(e)}")
        return False

def main():
    """主函数"""
    logger.info("=== 开始准备RAG系统数据 ===")
    
    # 确保data目录存在
    os.makedirs('data', exist_ok=True)
    
    success_count = 0
    total_tasks = 4
    
    # 准备各类数据
    if prepare_ferry_routes():
        success_count += 1
    
    if prepare_ports_data():
        success_count += 1
    
    if prepare_companies_data():
        success_count += 1
    
    if prepare_popular_routes():
        success_count += 1
    
    logger.info(f"=== 数据准备完成: {success_count}/{total_tasks} 成功 ===")
    
    if success_count == total_tasks:
        logger.info("✅ 所有数据准备成功！可以运行 initialize_rag.py 初始化RAG系统")
    else:
        logger.warning("⚠️ 部分数据准备失败，请检查错误信息")

if __name__ == "__main__":
    main()
