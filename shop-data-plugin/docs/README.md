# 店铺数据分析助手

一款专为拼多多商家设计的数据分析浏览器扩展插件，支持订单数据导入、成本核算、利润分析和报表导出功能。

## 功能特性

### 核心功能

- **订单数据导入**
  - 支持 Excel (.xlsx, .xls) 和 CSV 格式文件导入
  - 自动识别拼多多订单导出格式
  - 拼多多商家后台页面自动抓取订单

- **成本核算**
  - 商品成本管理
  - 运费模板配置
  - 平台佣金计算（默认0.6%）
  - 广告推广费分摊

- **利润分析**
  - 毛利润计算：销售额 - 总成本
  - 毛利率计算：毛利润 / 销售额 × 100%
  - 多维度分析（时间、商品、类目）

- **销售统计**
  - 销售额统计
  - 订单量统计
  - 客单价分析
  - 商品销量排行

- **报表导出**
  - 订单明细报表（Excel格式）
  - 利润分析报告
  - 每日统计报表

## 项目结构

```
shop-data-plugin/
├── backend/                # 后端服务
│   ├── main.py            # 主入口
│   ├── config.py          # 配置
│   ├── database.py        # 数据库
│   ├── schemas.py         # 数据模式
│   ├── models/            # 数据模型
│   │   ├── user.py       # 用户模型
│   │   ├── product.py    # 商品模型
│   │   ├── order.py      # 订单模型
│   │   └── shipping_template.py  # 运费模板
│   ├── routers/           # API路由
│   │   ├── auth.py       # 用户认证
│   │   ├── orders.py     # 订单管理
│   │   ├── costs.py      # 成本管理
│   │   └── reports.py    # 报表导出
│   └── requirements.txt   # Python依赖
│
├── extension/              # 浏览器扩展
│   ├── manifest.json      # 扩展配置
│   ├── popup/             # 弹窗页面
│   │   ├── index.html
│   │   └── popup.js
│   ├── content/           # 内容脚本
│   │   └── pdd.js        # 拼多多抓取脚本
│   ├── background/        # 后台服务
│   │   └── service-worker.js
│   ├── options/           # 设置页面
│   │   └── index.html
│   └── assets/            # 资源文件
│       ├── styles.css
│       └── icons/
│
└── docs/                  # 文档
    └── README.md
```

## 安装部署

### 后端服务

1. **安装Python依赖**

```bash
cd backend
pip install -r requirements.txt
```

2. **配置环境变量**

```bash
cp .env.example .env
# 编辑.env文件，修改SECRET_KEY等配置
```

3. **启动服务**

```bash
# 开发模式
python main.py

# 或使用uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

4. **访问API文档**

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 浏览器扩展

1. **加载扩展**

   - 打开 Chrome 浏览器
   - 访问 `chrome://extensions/`
   - 开启"开发者模式"
   - 点击"加载已解压的扩展程序"
   - 选择 `extension` 目录

2. **配置扩展**

   - 点击扩展图标
   - 进入设置页面
   - 配置后端API地址（默认：http://localhost:8000）
   - 点击"测试连接"确认连接成功

## 使用指南

### 1. 注册登录

首次使用需要注册账号：

1. 点击扩展图标打开弹窗
2. 点击"注册"标签
3. 输入用户名和密码
4. 点击"注册"完成注册

### 2. 导入订单

**文件导入方式：**

1. 从拼多多商家后台导出订单数据（Excel格式）
2. 点击扩展图标 → "导入订单"
3. 选择导出的文件上传
4. 系统自动解析并导入订单

**页面抓取方式：**

1. 登录拼多多商家后台
2. 进入订单管理页面
3. 页面右侧会出现"抓取订单数据"按钮
4. 点击按钮即可抓取当前页面的订单

### 3. 设置成本

1. 进入"成本管理"标签页
2. 点击"添加商品"
3. 设置商品信息：
   - 商品名称
   - 成本价
   - 默认运费
   - 佣金比例
   - 广告费比例

### 4. 查看统计

在"数据概览"标签页可以查看：

- 总订单数
- 总销售额
- 总利润
- 利润率

### 5. 导出报表

1. 点击"导出报表"按钮
2. 选择报表类型
3. 系统自动下载Excel报表

## 成本计算说明

### 成本构成

```
总成本 = 商品成本 + 运费成本 + 平台佣金 + 广告费用 + 其他费用
```

### 利润计算

```
毛利润 = 销售额 - 总成本
毛利率 = 毛利润 / 销售额 × 100%
```

### 默认配置

| 项目 | 默认值 | 说明 |
|------|--------|------|
| 平台佣金 | 0.6% | 拼多多平台佣金比例 |
| 运费 | 0 | 根据实际设置 |
| 广告费 | 0 | 根据实际推广情况 |

## API接口

### 认证接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 用户注册 |
| POST | /api/auth/login | 用户登录 |
| GET | /api/auth/me | 获取当前用户信息 |

### 订单接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/orders/import | 导入订单文件 |
| GET | /api/orders | 获取订单列表 |
| GET | /api/orders/{id} | 获取订单详情 |
| PUT | /api/orders/{id} | 更新订单 |
| DELETE | /api/orders/{id} | 删除订单 |
| GET | /api/orders/stats/overview | 销售统计概览 |
| GET | /api/orders/stats/daily | 每日统计 |
| GET | /api/orders/stats/products | 商品统计 |

### 成本接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/costs/products | 创建商品 |
| GET | /api/costs/products | 获取商品列表 |
| PUT | /api/costs/products/{id} | 更新商品 |
| PUT | /api/costs/products/{id}/cost | 设置商品成本 |
| POST | /api/costs/shipping-templates | 创建运费模板 |
| GET | /api/costs/shipping-templates | 获取运费模板列表 |

### 报表接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/reports/orders/excel | 导出订单报表 |
| GET | /api/reports/profit/excel | 导出利润报表 |
| GET | /api/reports/daily/excel | 导出每日统计 |

## 数据库设计

### 用户表 (users)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| username | VARCHAR(50) | 用户名 |
| email | VARCHAR(100) | 邮箱 |
| password_hash | VARCHAR(255) | 密码哈希 |
| created_at | DATETIME | 创建时间 |

### 商品表 (products)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户ID |
| product_id | VARCHAR(50) | 拼多多商品ID |
| name | VARCHAR(255) | 商品名称 |
| cost_price | DECIMAL(10,2) | 成本价 |
| shipping_cost | DECIMAL(10,2) | 运费 |
| commission_rate | DECIMAL(5,4) | 佣金比例 |

### 订单表 (orders)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户ID |
| order_id | VARCHAR(50) | 订单号 |
| product_name | VARCHAR(255) | 商品名称 |
| quantity | INTEGER | 数量 |
| sale_price | DECIMAL(10,2) | 销售单价 |
| total_amount | DECIMAL(10,2) | 订单金额 |
| cost_price | DECIMAL(10,2) | 成本价 |
| shipping_cost | DECIMAL(10,2) | 运费 |
| commission | DECIMAL(10,2) | 佣金 |
| ad_cost | DECIMAL(10,2) | 广告费 |
| gross_profit | DECIMAL(10,2) | 毛利润 |
| status | VARCHAR(20) | 订单状态 |
| order_time | DATETIME | 下单时间 |

## 注意事项

1. **数据安全**
   - 密码使用 bcrypt 加密存储
   - API 使用 JWT Token 认证
   - 建议在生产环境使用 HTTPS

2. **浏览器扩展**
   - 需要在 Chrome 浏览器中使用
   - 首次使用需要加载扩展并配置API地址
   - 页面抓取功能仅在拼多多商家后台生效

3. **订单导入**
   - 支持拼多多标准订单导出格式
   - 重复订单会自动跳过
   - 建议定期导出备份

## 技术栈

### 后端

- **框架**: FastAPI
- **数据库**: SQLite
- **认证**: JWT
- **数据处理**: Pandas, OpenPyXL

### 前端

- **框架**: Vue.js 3
- **浏览器扩展**: Chrome Extension Manifest V3

## 版本历史

### v1.0.0 (2024-01)

- 初始版本发布
- 支持订单导入和成本核算
- 支持利润分析和统计
- 支持报表导出

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。
