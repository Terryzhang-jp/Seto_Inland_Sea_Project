# 瀬户内海船班查询API

一个基于FastAPI的瀬户内海船班时刻表查询后端系统，提供完整的岛屿跳岛航线信息。

## 🚀 功能特性

- **航线搜索** - 支持多条件组合搜索（出发地、到达地、时间、公司等）
- **港口信息** - 获取瀬户内海所有港口详情和连接信息
- **公司信息** - 船运公司详情和联系方式
- **热门路线** - 推荐常用跳岛路线
- **实时数据** - 基于最新的船班时刻表数据
- **RESTful API** - 标准化的API接口
- **自动文档** - 自动生成的API文档
- **CORS支持** - 为前端应用做好准备

## 📊 数据覆盖

- **244条航线** - 覆盖瀬户内海主要岛屿间的所有航线
- **7家船运公司** - 包括四国汽船、ジャンボフェリー等主要运营商
- **14个港口** - 覆盖直島、豊島、小豆島、犬島、女木島、男木島等
- **完整跳岛路线** - 支持高松⇔直島⇔豊島⇔小豆島等所有跳岛组合

## 🛠️ 技术栈

- **FastAPI** - 现代Python Web框架
- **Pydantic** - 数据验证和序列化
- **pandas** - 高效CSV数据处理
- **uvicorn** - ASGI服务器

## 📦 安装和运行

### 1. 克隆项目
```bash
cd ferry_api
```

### 2. 创建虚拟环境
```bash
python -m venv ferry_env
source ferry_env/bin/activate  # Linux/Mac
# 或
ferry_env\Scripts\activate     # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 启动服务器
```bash
python run.py
```

服务器将在 http://localhost:8000 启动

## 📚 API文档

启动服务器后，访问以下地址查看API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔗 API端点

### 航线相关
- `GET /api/v1/routes` - 搜索航线
- `GET /api/v1/routes/popular` - 获取热门路线

### 港口相关
- `GET /api/v1/ports` - 获取所有港口
- `GET /api/v1/ports/{port_name}` - 获取特定港口信息

### 公司相关
- `GET /api/v1/companies` - 获取所有船运公司
- `GET /api/v1/companies/{company_name}` - 获取特定公司信息

### 系统相关
- `GET /` - API根路径
- `GET /health` - 健康检查

## 🔍 使用示例

### 搜索航线
```bash
# 搜索高松到直島的航线
curl "http://localhost:8000/api/v1/routes?departure=高松&arrival=直島"

# 搜索允许车辆的航线
curl "http://localhost:8000/api/v1/routes?allows_vehicles=true"

# 搜索特定时间段的航线
curl "http://localhost:8000/api/v1/routes?departure_time_start=08:00&departure_time_end=10:00"
```

### 获取港口信息
```bash
# 获取所有港口
curl "http://localhost:8000/api/v1/ports"

# 搜索港口
curl "http://localhost:8000/api/v1/ports?search=直島"
```

### 获取公司信息
```bash
# 获取所有公司
curl "http://localhost:8000/api/v1/companies"

# 搜索公司
curl "http://localhost:8000/api/v1/companies?search=四国汽船"
```

## 📋 查询参数

### 航线搜索参数
- `departure` - 出发地（支持模糊匹配）
- `arrival` - 到达地（支持模糊匹配）
- `company` - 运营公司（支持模糊匹配）
- `departure_time_start` - 出发时间开始 (HH:MM)
- `departure_time_end` - 出发时间结束 (HH:MM)
- `allows_vehicles` - 是否允许车辆 (true/false)
- `allows_bicycles` - 是否允许自行车 (true/false)
- `page` - 页码 (默认: 1)
- `limit` - 每页数量 (默认: 20, 最大: 100)

## 🌟 响应格式

所有API响应都遵循统一格式：

```json
{
  "success": true,
  "data": [...],
  "message": "Success",
  "total": 100,
  "page": 1,
  "limit": 20
}
```

## 🧪 测试

运行测试脚本：

```bash
# 测试数据加载
python test_data_loading.py

# 测试基本API功能
python test_api.py

# 测试高级API功能
python test_advanced_api.py
```

## 📁 项目结构

```
ferry_api/
├── app/
│   ├── models/          # Pydantic模型
│   ├── services/        # 业务逻辑
│   ├── routers/         # API路由
│   ├── core/            # 核心配置
│   └── main.py          # FastAPI应用入口
├── data/                # CSV数据文件
├── ferry_env/           # 虚拟环境
├── requirements.txt     # 依赖列表
├── run.py              # 启动脚本
└── README.md           # 项目文档
```

## 🔧 开发

### 添加新功能
1. 在 `app/models/` 中定义数据模型
2. 在 `app/services/` 中实现业务逻辑
3. 在 `app/routers/` 中添加API路由
4. 在 `app/main.py` 中注册路由

### 数据更新
更新 `data/` 目录下的CSV文件，服务器会自动重新加载数据。

## 📞 联系方式

如有问题或建议，请联系开发团队。

---

**瀬户内海船班查询API v1.0.0**  
*让岛屿跳岛旅行变得简单*
