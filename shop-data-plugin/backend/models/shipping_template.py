"""
运费模板数据模型
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from database import Base


class ShippingTemplate(Base):
    """运费模板表"""
    __tablename__ = "shipping_templates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    name = Column(String(100), nullable=False, comment="模板名称")

    # 计费方式
    calculation_type = Column(String(20), default="by_weight", comment="计费方式: by_weight按重量, by_piece按件, by_volume按体积")

    # 默认运费
    base_cost = Column(Numeric(10, 2), default=0, comment="首重/首件运费")
    base_unit = Column(Numeric(10, 2), default=1, comment="首重/首件单位")
    extra_cost = Column(Numeric(10, 2), default=0, comment="续重/续件运费")
    extra_unit = Column(Numeric(10, 2), default=1, comment="续重/续件单位")

    # 包邮条件
    free_shipping_enabled = Column(Boolean, default=False, comment="是否包邮")
    free_shipping_amount = Column(Numeric(10, 2), default=0, comment="满额包邮金额")
    free_shipping_quantity = Column(Integer, default=0, comment="满件包邮数量")

    # 状态
    is_default = Column(Boolean, default=False, comment="是否默认模板")
    is_active = Column(Boolean, default=True, comment="是否启用")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<ShippingTemplate {self.name}>"


class ShippingRegion(Base):
    """运费区域配置"""
    __tablename__ = "shipping_regions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    template_id = Column(Integer, ForeignKey("shipping_templates.id"), nullable=False, index=True, comment="模板ID")

    # 地区配置
    provinces = Column(String(500), nullable=True, comment="省份列表，逗号分隔")

    # 该区域的运费配置
    base_cost = Column(Numeric(10, 2), default=0, comment="首重/首件运费")
    base_unit = Column(Numeric(10, 2), default=1, comment="首重/首件单位")
    extra_cost = Column(Numeric(10, 2), default=0, comment="续重/续件运费")
    extra_unit = Column(Numeric(10, 2), default=1, comment="续重/续件单位")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<ShippingRegion {self.provinces}>"
