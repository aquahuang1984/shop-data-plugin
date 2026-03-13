# 店铺数据分析助手

> 专为拼多多商家设计的数据分析浏览器扩展插件

## 快速开始

### 1. 启动后端服务

```bash
cd backend
pip install -r requirements.txt
python main.py
```

服务将在 http://localhost:8000 启动

### 2. 安装浏览器扩展

1. 打开 Chrome，访问 `chrome://extensions/`
2. 开启"开发者模式"
3. 点击"加载已解压的扩展程序"
4. 选择 `extension` 目录

### 3. 使用插件

1. 点击扩展图标
2. 注册/登录账号
3. 导入订单数据
4. 查看数据分析

## 功能一览

| 功能 | 说明 |
|------|------|
| 📥 订单导入 | 支持Excel/CSV文件导入，自动抓取拼多多后台订单 |
| 💰 成本核算 | 商品成本、运费、佣金、广告费管理 |
| 📊 利润分析 | 毛利润、毛利率、净利润计算 |
| 📈 销售统计 | 多维度数据统计与可视化 |
| 📋 报表导出 | Excel格式报表一键导出 |

## 目录结构

```
shop-data-plugin/
├── backend/      # FastAPI后端服务
├── extension/    # Chrome浏览器扩展
└── docs/         # 文档
```

## 详细文档

请查看 [完整使用文档](./README.md)
