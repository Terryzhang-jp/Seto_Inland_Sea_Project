#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证脚本
Data Validation Script
"""

import csv
from collections import defaultdict

def validate_timetable():
    """验证时间表数据"""
    print("=== 验证时间表数据 ===")
    
    routes = []
    companies = set()
    ports = set()
    
    try:
        with open('setouchi_ferry_timetable.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                routes.append(row)
                companies.add(row['运营公司'])
                ports.add(row['出发地'])
                ports.add(row['到达地'])
    except FileNotFoundError:
        print("错误：找不到 setouchi_ferry_timetable.csv 文件")
        return
    
    print(f"总航线数: {len(routes)}")
    print(f"运营公司数: {len(companies)}")
    print(f"港口数: {len(ports)}")
    
    print("\n运营公司列表:")
    for company in sorted(companies):
        print(f"  - {company}")
    
    print("\n港口列表:")
    for port in sorted(ports):
        print(f"  - {port}")
    
    # 统计各公司的航线数
    company_routes = defaultdict(int)
    for route in routes:
        company_routes[route['运营公司']] += 1
    
    print("\n各公司航线数统计:")
    for company, count in sorted(company_routes.items()):
        print(f"  {company}: {count} 条")
    
    # 统计各港口的航线数
    port_routes = defaultdict(int)
    for route in routes:
        port_routes[route['出发地']] += 1
        port_routes[route['到达地']] += 1
    
    print("\n各港口航线数统计:")
    for port, count in sorted(port_routes.items(), key=lambda x: x[1], reverse=True):
        print(f"  {port}: {count} 条")

def validate_companies():
    """验证公司信息"""
    print("\n=== 验证公司信息 ===")
    
    try:
        with open('ferry_companies_info.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            companies = list(reader)
    except FileNotFoundError:
        print("错误：找不到 ferry_companies_info.csv 文件")
        return
    
    print(f"公司信息记录数: {len(companies)}")
    for company in companies:
        print(f"  {company['公司名称']}: {company['主要航线']}")

def validate_ports():
    """验证港口信息"""
    print("\n=== 验证港口信息 ===")
    
    try:
        with open('ports_info.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            ports = list(reader)
    except FileNotFoundError:
        print("错误：找不到 ports_info.csv 文件")
        return
    
    print(f"港口信息记录数: {len(ports)}")
    for port in ports:
        print(f"  {port['港口名称']} ({port['所在岛屿']}): {port['连接岛屿']}")

def validate_fares():
    """验证票价信息"""
    print("\n=== 验证票价信息 ===")
    
    try:
        with open('fare_summary.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fares = list(reader)
    except FileNotFoundError:
        print("错误：找不到 fare_summary.csv 文件")
        return
    
    print(f"票价信息记录数: {len(fares)}")
    for fare in fares:
        print(f"  {fare['出发地']} → {fare['到达地']}: {fare['大人票价']} ({fare['运营公司']})")

def main():
    """主函数"""
    print("瀬户内海船班数据验证")
    print("=" * 50)
    
    validate_timetable()
    validate_companies()
    validate_ports()
    validate_fares()
    
    print("\n数据验证完成！")

if __name__ == "__main__":
    main()
