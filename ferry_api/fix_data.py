#!/usr/bin/env python3
"""
修复数据文件格式
"""

import pandas as pd
import json
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def fix_ports_data():
    """修复港口数据"""
    try:
        # 手动创建港口数据
        ports_data = [
            {"name": "高松港", "island": "本州", "address": "香川県高松市", "features": "主要出发港", "connections": "直島、豊島、小豆島"},
            {"name": "宇野港", "island": "本州", "address": "岡山県玉野市", "features": "主要出发港", "connections": "直島、豊島、小豆島"},
            {"name": "直島宮浦港", "island": "直島", "address": "香川県香川郡直島町", "features": "主要港口", "connections": "高松、宇野、豊島、犬島"},
            {"name": "直島本村港", "island": "直島", "address": "香川県香川郡直島町", "features": "东侧港口", "connections": "高松、宇野"},
            {"name": "豊島家浦港", "island": "豊島", "address": "香川県小豆郡土庄町", "features": "主要港口", "connections": "宇野、直島、小豆島、犬島"},
            {"name": "豊島唐櫃港", "island": "豊島", "address": "香川県小豆郡土庄町", "features": "北侧港口", "connections": "宇野、小豆島"},
            {"name": "小豆島土庄港", "island": "小豆島", "address": "香川県小豆郡土庄町", "features": "西侧主要港口", "connections": "高松、宇野、豊島"},
            {"name": "小豆島池田港", "island": "小豆島", "address": "香川県小豆郡小豆島町", "features": "东侧港口", "connections": "高松"},
            {"name": "小豆島坂手港", "island": "小豆島", "address": "香川県小豆郡小豆島町", "features": "东南侧港口", "connections": "高松"},
            {"name": "犬島港", "island": "犬島", "address": "岡山県岡山市", "features": "小岛港口", "connections": "直島、豊島"},
            {"name": "神戸港", "island": "本州", "address": "兵庫県神戸市", "features": "関西主要港口", "connections": "高松、小豆島"},
            {"name": "新岡山港", "island": "本州", "address": "岡山県玉野市", "features": "岡山主要港口", "connections": "小豆島土庄"},
            {"name": "女木島港", "island": "女木島", "address": "香川県高松市", "features": "鬼島港口", "connections": "高松、男木島"},
            {"name": "男木島港", "island": "男木島", "address": "香川県高松市", "features": "猫島港口", "connections": "高松、女木島"}
        ]
        
        df = pd.DataFrame(ports_data)
        df.to_csv('data/ports.csv', index=False, encoding='utf-8')
        logger.info(f"修复港口数据完成，共 {len(ports_data)} 条")
        return True
        
    except Exception as e:
        logger.error(f"修复港口数据失败: {str(e)}")
        return False

def fix_companies_data():
    """修复公司数据"""
    try:
        # 手动创建公司数据
        companies_data = [
            {"name": "四国汽船", "phone": "087-851-5500", "website": "https://www.shikokukisen.com/", "main_routes": "高松-直島、宇野-直島", "notes": "主要运营直島航线"},
            {"name": "ジャンボフェリー", "phone": "087-811-4383", "website": "https://www.ferry.co.jp/", "main_routes": "神戸-高松、高松-小豆島", "notes": "长距离航线专家"},
            {"name": "国際両備フェリー", "phone": "086-272-5520", "website": "https://www.ryobi-ferry.com/", "main_routes": "高松-小豆島、新岡山-小豆島", "notes": "小豆島主要运营商"},
            {"name": "四国フェリー", "phone": "087-851-4383", "website": "https://www.shikokuferry.com/", "main_routes": "高松-小豆島土庄", "notes": "小豆島土庄港专线"},
            {"name": "雌雄島海運", "phone": "087-840-9055", "website": "https://www.shiwaku.jp/", "main_routes": "高松-女木島-男木島", "connections": "女木島、男木島专线"},
            {"name": "豊島フェリー", "phone": "087-840-0006", "website": "https://teshima-ferry.jp/", "main_routes": "高松-豊島-直島", "notes": "豊島美术馆航线"},
            {"name": "小豆島豊島フェリー", "phone": "0879-62-2220", "website": "https://www.shodoshima-ferry.co.jp/", "main_routes": "宇野-豊島-小豆島", "notes": "宇野出发的豊島航线"},
            {"name": "雌雄島海運", "phone": "087-840-9055", "website": "https://www.shiwaku.jp/", "main_routes": "高松-女木島-男木島", "notes": "女木島、男木島专线"}
        ]
        
        df = pd.DataFrame(companies_data)
        df.to_csv('data/companies.csv', index=False, encoding='utf-8')
        logger.info(f"修复公司数据完成，共 {len(companies_data)} 条")
        return True
        
    except Exception as e:
        logger.error(f"修复公司数据失败: {str(e)}")
        return False

def main():
    """主函数"""
    logger.info("=== 开始修复数据文件 ===")
    
    success_count = 0
    total_tasks = 2
    
    if fix_ports_data():
        success_count += 1
    
    if fix_companies_data():
        success_count += 1
    
    logger.info(f"=== 数据修复完成: {success_count}/{total_tasks} 成功 ===")
    
    if success_count == total_tasks:
        logger.info("✅ 所有数据修复成功！")
    else:
        logger.warning("⚠️ 部分数据修复失败")

if __name__ == "__main__":
    main()
