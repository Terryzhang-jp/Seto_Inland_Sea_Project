# 瀬户内海岛屿跳岛船班查询系统
# Setouchi Island Hopping Ferry Timetable System

## 项目概述 / Project Overview

这是一个专门为瀬户内海岛屿间跳岛旅行设计的船班时间表查询系统。系统收集了8个主要船运公司的详细时间表信息，涵盖了高松、宇野、直島、豊島、小豆島、犬島等主要港口之间的所有航线。

This is a comprehensive ferry timetable search system designed for island hopping in the Seto Inland Sea. The system collects detailed timetable information from 8 major ferry companies, covering all routes between major ports including Takamatsu, Uno, Naoshima, Teshima, Shodoshima, and Inujima.

## 数据来源 / Data Sources

本系统的数据来源于以下官方网站：

1. **豊島观光ナビ** - https://teshima-navi.jp/access/
2. **豊島フェリー** - https://t-ferry.com/schedule/
3. **四国汽船** - https://www.shikokukisen.com/
4. **四国汽船即时信息** - https://www.shikokukisen.com/instant/
5. **直島观光协会** - https://naoshima.net/access/access_area/
6. **四国フェリー** - https://www.shikokuferry.com/route2
7. **両備小豆島** - https://ryobi-shodoshima.jp/timetable/timetable_takamatsu/
8. **ジャンボフェリー** - https://ferry.co.jp/home/takamatsu-shodoshima/

## 文件结构 / File Structure

```
├── setouchi_ferry_timetable.csv    # 主要船班时间表
├── ferry_companies_info.csv        # 船运公司信息
├── ports_info.csv                  # 港口信息
├── fare_summary.csv                # 票价汇总
├── ferry_search.py                 # Python查询脚本
└── README.md                       # 说明文档
```

## 主要航线 / Main Routes

### 1. 宇野 ⇔ 豊島 ⇔ 小豆島航线
- **运营公司**: 小豆島豊島フェリー
- **特点**: 可载车辆（フェリー），每日运行
- **主要港口**: 宇野港 → 豊島家浦港 → 豊島唐櫃港 → 小豆島土庄港

### 2. 高松 ⇔ 直島 ⇔ 豊島航线
- **运营公司**: 豊島フェリー
- **特点**: 季节性运行，仅旅客船
- **运行期间**: 3月20日-11月30日

### 3. 直島 ⇔ 豊島 ⇔ 犬島航线
- **运营公司**: 四国汽船
- **特点**: 美術館开馆日运行，仅旅客船
- **运行期间**: 3月1日-11月30日（月水木金土日祝）

### 4. 高松 ⇔ 直島航线
- **运营公司**: 四国汽船
- **船型**: フェリー（可载车）+ 高速旅客船
- **特点**: 每日运行，班次频繁

### 5. 宇野 ⇔ 直島航线
- **运营公司**: 四国汽船
- **船型**: フェリー（可载车）+ 旅客船
- **特点**: 每日运行，班次最多

### 6. 高松 ⇔ 小豆島航线
- **土庄港**: 四国フェリー（可网上预约）
- **池田港**: 国際両備フェリー（可网上预约）
- **坂手港**: ジャンボフェリー（特殊船只）

## 使用方法 / How to Use

### 1. 直接查看CSV文件
可以直接打开CSV文件查看详细的船班信息。

### 2. 使用Python查询脚本

#### 安装依赖
```bash
pip install pandas
```

#### 交互式查询
```bash
python ferry_search.py
```

#### 命令行查询
```bash
# 查询从高松到直島的航线
python ferry_search.py 高松 直島

# 查询从宇野出发的所有航线
python ferry_search.py 宇野
```

## 重要提醒 / Important Notes

### 🚨 运行限制 / Operating Restrictions

1. **美術館休馆日**: 直島-豊島-犬島航线在美術館休馆时停运
2. **季节性运行**: 部分航线仅在特定季节运行
3. **危险物车辆专用便**: 某些班次不允许一般旅客乘船
4. **深夜便**: 部分深夜班次需要额外费用

### 💰 票价信息 / Fare Information

- **大人票价**: 成人票价
- **小人票价**: 儿童票价（小学生）
- **车辆费用**: フェリー可载车，旅客船不可载车
- **自行车**: 部分フェリー允许自行车，旅客船通常不允许

### 📞 联系方式 / Contact Information

各船运公司的详细联系方式请参考 `ferry_companies_info.csv` 文件。

## 数据更新 / Data Updates

本数据收集于2025年6月，建议在实际出行前：

1. 访问各船运公司官网确认最新时间表
2. 确认季节性航线的运行状态
3. 查询天气对航班的影响
4. 提前预约（如需要）

## 贡献 / Contributing

如发现数据错误或需要更新，请提交Issue或Pull Request。

## 许可证 / License

本项目仅供参考使用，数据版权归各船运公司所有。
# Seto_Inland_Sea_Project
