"""
数据模型初始化
"""
from models.user import User
from models.product import Product, ProductCostHistory
from models.order import Order, OrderStatus
from models.shipping_template import ShippingTemplate, ShippingRegion

__all__ = [
    "User",
    "Product",
    "ProductCostHistory",
    "Order",
    "OrderStatus",
    "ShippingTemplate",
    "ShippingRegion",
]
