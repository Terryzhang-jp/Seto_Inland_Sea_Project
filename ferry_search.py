#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
瀬户内海岛屿跳岛船班查询系统
Setouchi Island Hopping Ferry Search System
"""

import pandas as pd
import sys
from datetime import datetime

class FerrySearchSystem:
    def __init__(self):
        """初始化船班查询系统"""
        try:
            self.timetable = pd.read_csv('setouchi_ferry_timetable.csv')
            self.companies = pd.read_csv('ferry_companies_info.csv')
            self.ports = pd.read_csv('ports_info.csv')
            self.fares = pd.read_csv('fare_summary.csv')
            print("瀬户内海船班查询系统已启动！")
            print("Setouchi Ferry Search System Initialized!")
        except FileNotFoundError as e:
            print(f"错误：找不到数据文件 {e}")
            sys.exit(1)
    
    def search_routes(self, departure=None, arrival=None, company=None):
        """搜索航线"""
        result = self.timetable.copy()
        
        if departure:
            result = result[result['出发地'].str.contains(departure, na=False)]
        
        if arrival:
            result = result[result['到达地'].str.contains(arrival, na=False)]
        
        if company:
            result = result[result['运营公司'].str.contains(company, na=False)]
        
        return result
    
    def get_company_info(self, company_name=None):
        """获取船运公司信息"""
        if company_name:
            return self.companies[self.companies['公司名称'].str.contains(company_name, na=False)]
        return self.companies
    
    def get_port_info(self, port_name=None):
        """获取港口信息"""
        if port_name:
            return self.ports[self.ports['港口名称'].str.contains(port_name, na=False)]
        return self.ports
    
    def search_by_time(self, departure_time_start=None, departure_time_end=None):
        """按时间搜索"""
        result = self.timetable.copy()
        
        if departure_time_start:
            result = result[result['出发时间'] >= departure_time_start]
        
        if departure_time_end:
            result = result[result['出发时间'] <= departure_time_end]
        
        return result
    
    def get_fare_info(self, departure=None, arrival=None):
        """获取票价信息"""
        result = self.fares.copy()
        
        if departure:
            result = result[result['出发地'].str.contains(departure, na=False)]
        
        if arrival:
            result = result[result['到达地'].str.contains(arrival, na=False)]
        
        return result
    
    def display_results(self, results, title="搜索结果"):
        """显示搜索结果"""
        print(f"\n=== {title} ===")
        if results.empty:
            print("没有找到匹配的结果")
            return
        
        print(f"找到 {len(results)} 条记录：")
        for idx, row in results.iterrows():
            print(f"\n{idx+1}. {row['出发地']} → {row['到达地']}")
            print(f"   时间: {row['出发时间']} → {row['到达时间']}")
            print(f"   公司: {row['运营公司']}")
            print(f"   船型: {row['船只类型']}")
            print(f"   票价: 大人{row['大人票价']} / 小人{row['小人票价']}")
            if pd.notna(row['备注']) and row['备注']:
                print(f"   备注: {row['备注']}")
    
    def interactive_search(self):
        """交互式搜索"""
        print("\n=== 瀬户内海船班查询 ===")
        print("1. 按出发地和目的地搜索")
        print("2. 按运营公司搜索")
        print("3. 按时间段搜索")
        print("4. 查看所有港口信息")
        print("5. 查看所有船运公司信息")
        print("6. 查看票价信息")
        print("0. 退出")
        
        choice = input("\n请选择功能 (0-6): ")
        
        if choice == "1":
            departure = input("请输入出发地 (可留空): ").strip()
            arrival = input("请输入目的地 (可留空): ").strip()
            results = self.search_routes(
                departure if departure else None,
                arrival if arrival else None
            )
            self.display_results(results, f"{departure or '任意'} → {arrival or '任意'}")
        
        elif choice == "2":
            company = input("请输入船运公司名称 (可部分匹配): ").strip()
            results = self.search_routes(company=company if company else None)
            self.display_results(results, f"公司: {company}")
        
        elif choice == "3":
            start_time = input("请输入开始时间 (格式: HH:MM, 可留空): ").strip()
            end_time = input("请输入结束时间 (格式: HH:MM, 可留空): ").strip()
            results = self.search_by_time(
                start_time if start_time else None,
                end_time if end_time else None
            )
            self.display_results(results, f"时间段: {start_time or '00:00'} - {end_time or '23:59'}")
        
        elif choice == "4":
            port_name = input("请输入港口名称 (可留空查看全部): ").strip()
            results = self.get_port_info(port_name if port_name else None)
            print(f"\n=== 港口信息 ===")
            print(results.to_string(index=False))
        
        elif choice == "5":
            company_name = input("请输入公司名称 (可留空查看全部): ").strip()
            results = self.get_company_info(company_name if company_name else None)
            print(f"\n=== 船运公司信息 ===")
            print(results.to_string(index=False))
        
        elif choice == "6":
            departure = input("请输入出发地 (可留空): ").strip()
            arrival = input("请输入目的地 (可留空): ").strip()
            results = self.get_fare_info(
                departure if departure else None,
                arrival if arrival else None
            )
            print(f"\n=== 票价信息 ===")
            print(results.to_string(index=False))
        
        elif choice == "0":
            print("感谢使用！")
            return False
        
        else:
            print("无效选择，请重试")
        
        return True

def main():
    """主函数"""
    system = FerrySearchSystem()
    
    # 如果有命令行参数，直接搜索
    if len(sys.argv) > 1:
        departure = sys.argv[1] if len(sys.argv) > 1 else None
        arrival = sys.argv[2] if len(sys.argv) > 2 else None
        results = system.search_routes(departure, arrival)
        system.display_results(results)
        return
    
    # 否则进入交互模式
    while True:
        if not system.interactive_search():
            break
        
        input("\n按回车键继续...")

if __name__ == "__main__":
    main()
