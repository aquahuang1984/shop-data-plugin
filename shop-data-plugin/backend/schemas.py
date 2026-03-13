"""
Pydantic数据模式
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ==================== 用户相关 ====================
class UserBase(BaseModel):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")


class UserCreate(UserBase):
    """用户创建模式"""
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class UserLogin(BaseModel):
    """用户登录模式"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(UserBase):
    """用户响应模式"""
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token响应模式"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==================== 商品相关 ====================
class ProductBase(BaseModel):
    """商品基础模式"""
    product_id: Optional[str] = Field(None, description="拼多多商品ID")
    sku_id: Optional[str] = Field(None, description="SKU ID")
    name: str = Field(..., max_length=255, description="商品名称")
    category: Optional[str] = Field(None, max_length=100, description="商品类目")
    image_url: Optional[str] = Field(None, description="商品图片URL")
    cost_price: Decimal = Field(default=Decimal("0"), description="成本价")
    shipping_cost: Decimal = Field(default=Decimal("0"), description="默认运费")
    commission_rate: Decimal = Field(default=Decimal("0"), description="佣金比例")
    ad_cost_rate: Decimal = Field(default=Decimal("0"), description="广告费用比例")


class ProductCreate(ProductBase):
    """商品创建模式"""
    pass


class ProductUpdate(BaseModel):
    """商品更新模式"""
    name: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    cost_price: Optional[Decimal] = None
    shipping_cost: Optional[Decimal] = None
    commission_rate: Optional[Decimal] = None
    ad_cost_rate: Optional[Decimal] = None
    is_active: Optional[int] = None


class ProductResponse(ProductBase):
    """商品响应模式"""
    id: int
    user_id: int
    is_active: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 订单相关 ====================
class OrderBase(BaseModel):
    """订单基础模式"""
    order_id: str = Field(..., max_length=50, description="订单号")
    platform: str = Field(default="拼多多", description="平台")
    product_name: Optional[str] = Field(None, description="商品名称")
    sku_name: Optional[str] = Field(None, description="SKU规格")
    quantity: int = Field(default=1, ge=1, description="数量")
    sale_price: Decimal = Field(default=Decimal("0"), ge=0, description="销售单价")
    total_amount: Decimal = Field(default=Decimal("0"), ge=0, description="订单总额")
    status: str = Field(default="未知", description="订单状态")
    order_time: Optional[datetime] = Field(None, description="下单时间")
    buyer_name: Optional[str] = Field(None, description="买家姓名")
    province: Optional[str] = Field(None, description="省份")


class OrderCreate(OrderBase):
    """订单创建模式"""
    product_id: Optional[int] = None
    cost_price: Optional[Decimal] = None
    shipping_cost: Optional[Decimal] = None
    commission: Optional[Decimal] = None
    ad_cost: Optional[Decimal] = None
    other_cost: Optional[Decimal] = None


class OrderUpdate(BaseModel):
    """订单更新模式"""
    status: Optional[str] = None
    cost_price: Optional[Decimal] = None
    shipping_cost: Optional[Decimal] = None
    commission: Optional[Decimal] = None
    ad_cost: Optional[Decimal] = None
    other_cost: Optional[Decimal] = None
    note: Optional[str] = None


class OrderResponse(OrderBase):
    """订单响应模式"""
    id: int
    user_id: int
    product_id: Optional[int]
    cost_price: Decimal
    shipping_cost: Decimal
    commission: Decimal
    ad_cost: Decimal
    other_cost: Decimal
    gross_profit: Decimal
    net_profit: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 统计分析相关 ====================
class SalesStats(BaseModel):
    """销售统计"""
    total_orders: int = Field(description="总订单数")
    total_quantity: int = Field(description="总销售数量")
    total_sales: Decimal = Field(description="总销售额")
    total_cost: Decimal = Field(description="总成本")
    total_profit: Decimal = Field(description="总利润")
    avg_order_value: Decimal = Field(description="客单价")
    profit_rate: Decimal = Field(description="利润率")


class DailyStats(BaseModel):
    """每日统计"""
    date: str
    orders: int
    sales: Decimal
    profit: Decimal


class ProductStats(BaseModel):
"""商品统计"""
    product_name: str
    quantity: int
    sales: Decimal
    profit: Decimal
    profit_rate: Decimal


# ==================== 运费模板相关 ====================
class ShippingTemplateBase(BaseModel):
    """运费模板基础模式"""
    name: str = Field(..., max_length=100, description="模板名称")
    calculation_type: str = Field(default="by_piece", description="计费方式")
    base_cost: Decimal = Field(default=Decimal("0"), description="首重/首件运费")
    base_unit: Decimal = Field(default=Decimal("1"), description="首重/首件单位")
    extra_cost: Decimal = Field(default=Decimal("0"), description="续重/续件运费")
    extra_unit: Decimal = Field(default=Decimal("1"), description="续重/续件单位")
    free_shipping_enabled: bool = Field(default=False, description="是否包邮")
    free_shipping_amount: Optional[Decimal] = Field(None, description="满额包邮金额")


class ShippingTemplateCreate(ShippingTemplateBase):
    """运费模板创建模式"""
    pass


class ShippingTemplateResponse(ShippingTemplateBase):
    """运费模板响应模式"""
    id: int
    user_id: int
    is_default: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 通用响应 ====================
class Message(BaseModel):
    """通用消息响应"""
    message: str
    success: bool = True


class PaginatedResponse(BaseModel):
    """分页响应"""
    total: int
    page: int
    page_size: int
    items: List
