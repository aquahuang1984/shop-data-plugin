# 店铺数据分析插件后端

基于 FastAPI 构建的店铺数据分析后端服务。

## 功能特性

- 用户认证与管理
- 订单数据导入（Excel/CSV）
- 成本核算与管理
- 利润分析计算
- 销售统计分析
- 报表导出（Excel）

## 安装

```bash
# 安装依赖
pip install -r requirements.txt
```

## 运行

```bash
# 开发模式
python main.py

# 或使用uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 环境变量

创建 `.env` 文件配置：

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./shop_data.db
DEBUG=True
```

## 目录结构

```
backend/
├── main.py           # 主入口
├── config.py         # 配置
├── database.py       # 数据库
├── schemas.py        # 数据模式
├── models/           # 数据模型
├── routers/          # API路由
├── services/         # 业务逻辑
└── utils/            # 工具函数
```
