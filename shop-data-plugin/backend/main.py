"""
店铺数据分析插件 - 后端服务主入口
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from config import settings
from database import init_db
from routers import auth_router, orders_router, costs_router, reports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    init_db()
    print("✓ 数据库初始化完成")
    yield
    # 关闭时的清理工作
    print("✓ 应用已关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    店铺数据分析插件后端API

    ## 功能模块

    * **认证** - 用户注册、登录、Token认证
    * **订单管理** - 订单导入、查询、统计
    * **成本管理** - 商品成本、运费模板管理
    * **报表导出** - Excel报表生成与导出

    ## 使用说明

    1. 首先注册账号并登录获取Token
    2. 在请求头中添加: `Authorization: Bearer <token>`
    3. 导入订单数据或手动创建订单
    4. 设置商品成本信息
    5. 查看统计数据和导出报表
    """,
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    return JSONResponse(
        status_code=500,
        content={
            "message": "服务器内部错误",
            "detail": str(exc) if settings.DEBUG else "请联系管理员"
        }
    )


# 注册路由
app.include_router(auth_router)
app.include_router(orders_router)
app.include_router(costs_router)
app.include_router(reports_router)


# 健康检查
@app.get("/", tags=["系统"])
async def root():
    """API根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
