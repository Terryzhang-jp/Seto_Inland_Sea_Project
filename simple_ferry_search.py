#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
瀬户内海岛屿跳岛船班查询系统 - 简化版
Setouchi Island Hopping Ferry Search System - Simple Version
"""

import csv
import sys

class SimpleFerrySearch:
    def __init__(self):
        """初始化船班查询系统"""
        self.timetable = []
        self.load_timetable()
        print("瀬户内海船班查询系统已启动！")
        print("Setouchi Ferry Search System Initialized!")
    
    def load_timetable(self):
        """加载时间表数据"""
        try:
            with open('setouchi_ferry_timetable.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.timetable = list(reader)
            print(f"成功加载 {len(self.timetable)} 条船班记录")
        except FileNotFoundError:
            print("错误：找不到 setouchi_ferry_timetable.csv 文件")
            sys.exit(1)
    
    def search_routes(self, departure=None, arrival=None, company=None):
        """搜索航线"""
        results = []
        
        for route in self.timetable:
            match = True
            
            if departure and departure not in route['出发地']:
                match = False
            
            if arrival and arrival not in route['到达地']:
                match = False
            
            if company and company not in route['运营公司']:
                match = False
            
            if match:
                results.append(route)
        
        return results
    
    def display_results(self, results, title="搜索结果"):
        """显示搜索结果"""
        print(f"\n=== {title} ===")
        if not results:
            print("没有找到匹配的结果")
            return
        
        print(f"找到 {len(results)} 条记录：")
        for i, route in enumerate(results, 1):
            print(f"\n{i}. {route['出发地']} → {route['到达地']}")
            print(f"   时间: {route['出发时间']} → {route['到达时间']}")
            print(f"   公司: {route['运营公司']}")
            print(f"   船型: {route['船只类型']}")
            print(f"   票价: 大人{route['大人票价']} / 小人{route['小人票价']}")
            print(f"   载车: {route['允许车辆']} / 载自行车: {route['允许自行车']}")
            if route['备注']:
                print(f"   备注: {route['备注']}")
    
    def interactive_search(self):
        """交互式搜索"""
        print("\n=== 瀬户内海船班查询 ===")
        print("1. 按出发地和目的地搜索")
        print("2. 按运营公司搜索")
        print("3. 显示所有航线")
        print("4. 显示热门路线")
        print("0. 退出")
        
        choice = input("\n请选择功能 (0-4): ")
        
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
            self.display_results(self.timetable, "所有航线")
        
        elif choice == "4":
            self.show_popular_routes()
        
        elif choice == "0":
            print("感谢使用！")
            return False
        
        else:
            print("无效选择，请重试")
        
        return True
    
    def show_popular_routes(self):
        """显示热门路线"""
        popular_routes = [
            ("高松", "直島"),
            ("宇野", "直島"),
            ("高松", "小豆島"),
            ("宇野", "豊島"),
            ("直島", "豊島"),
            ("豊島", "犬島")
        ]
        
        print("\n=== 热门路线 ===")
        for departure, arrival in popular_routes:
            print(f"\n--- {departure} → {arrival} ---")
            results = self.search_routes(departure, arrival)
            if results:
                for route in results[:3]:  # 只显示前3个结果
                    print(f"  {route['出发时间']} → {route['到达时间']} ({route['运营公司']})")
            else:
                print("  暂无直达航线")

def main():
    """主函数"""
    system = SimpleFerrySearch()
    
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
