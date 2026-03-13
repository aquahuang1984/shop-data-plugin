"""
订单数据模型
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import enum


class OrderStatus(str, enum.Enum):
    """订单状态枚举"""
    PENDING = "待发货"
    SHIPPED = "已发货"
    DELIVERED = "已签收"
    CANCELLED = "已取消"
    REFUNDED = "已退款"
    UNKNOWN = "未知"


class Order(Base):
    """订单表"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True, comment="商品ID")

    # 订单基本信息
    order_id = Column(String(50), unique=True, index=True, nullable=False, comment="订单号")
    platform = Column(String(20), default="拼多多", comment="平台")

    # 商品信息
    product_name = Column(String(255), nullable=True, comment="商品名称")
    sku_name = Column(String(255), nullable=True, comment="SKU规格")
    quantity = Column(Integer, default=1, comment="数量")

    # 价格信息
    sale_price = Column(Numeric(10, 2), default=0, comment="销售单价")
    total_amount = Column(Numeric(10, 2), default=0, comment="订单总额")

    # 成本信息
    cost_price = Column(Numeric(10, 2), default=0, comment="成本单价")
    shipping_cost = Column(Numeric(10, 2), default=0, comment="运费成本")
    commission = Column(Numeric(10, 2), default=0, comment="平台佣金")
    ad_cost = Column(Numeric(10, 2), default=0, comment="广告费用")
    other_cost = Column(Numeric(10, 2), default=0, comment="其他费用")

    # 利润信息
    gross_profit = Column(Numeric(10, 2), default=0, comment="毛利润")
    net_profit = Column(Numeric(10, 2), default=0, comment="净利润")

    # 订单状态和时间
    status = Column(String(20), default=OrderStatus.UNKNOWN.value, comment="订单状态")
    order_time = Column(DateTime, nullable=True, comment="下单时间")
    pay_time = Column(DateTime, nullable=True, comment="支付时间")
    ship_time = Column(DateTime, nullable=True, comment="发货时间")
    finish_time = Column(DateTime, nullable=True, comment="完成时间")

    # 买家信息
    buyer_name = Column(String(50), nullable=True, comment="买家姓名")
    buyer_phone = Column(String(20), nullable=True, comment="买家电话")
    province = Column(String(20), nullable=True, comment="省份")
    city = Column(String(20), nullable=True, comment="城市")
    district = Column(String(20), nullable=True, comment="区县")

    # 其他
    note = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联
    product = relationship("Product", back_populates="orders")

    def __repr__(self):
        return f"<Order {self.order_id}>"

    def calculate_profit(self):
        """计算利润"""
        # 总成本 = (成本价 × 数量) + 运费 + 佣金 + 广告费 + 其他费用
        total_cost = (self.cost_price * self.quantity) + self.shipping_cost + self.commission + self.ad_cost + self.other_cost
        # 毛利润 = 销售总额 - 总成本
        self.gross_profit = self.total_amount - total_cost
        # 净利润（暂时等于毛利润，后续可扣除退款等）
        self.net_profit = self.gross_profit
        return self.gross_profit
