"""
商品数据模型
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class Product(Base):
    """商品表"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    product_id = Column(String(50), index=True, nullable=True, comment="拼多多商品ID")
    sku_id = Column(String(50), index=True, nullable=True, comment="SKU ID")
    name = Column(String(255), nullable=False, comment="商品名称")
    category = Column(String(100), nullable=True, comment="商品类目")
    image_url = Column(String(500), nullable=True, comment="商品图片URL")

    # 成本相关
    cost_price = Column(Numeric(10, 2), default=0, comment="成本价")
    shipping_cost = Column(Numeric(10, 2), default=0, comment="默认运费")
    commission_rate = Column(Numeric(5, 4), default=0, comment="佣金比例")
    ad_cost_rate = Column(Numeric(5, 4), default=0, comment="广告费用比例")

    # 状态
    is_active = Column(Integer, default=1, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联
    orders = relationship("Order", back_populates="product")

    def __repr__(self):
        return f"<Product {self.name}>"


class ProductCostHistory(Base):
    """商品成本历史记录"""
    __tablename__ = "product_cost_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    cost_price = Column(Numeric(10, 2), comment="成本价")
    shipping_cost = Column(Numeric(10, 2), comment="运费")
    changed_at = Column(DateTime, server_default=func.now(), comment="变更时间")
    note = Column(Text, nullable=True, comment="备注")
