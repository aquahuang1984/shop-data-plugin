"""
路由初始化
"""
from routers.auth import router as auth_router
from routers.orders import router as orders_router
from routers.costs import router as costs_router
from routers.reports import router as reports_router

__all__ = [
    "auth_router",
    "orders_router",
    "costs_router",
    "reports_router",
]
