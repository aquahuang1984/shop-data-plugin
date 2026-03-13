"""
成本管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from database import get_db
from models.user import User
from models.product import Product, ProductCostHistory
from models.shipping_template import ShippingTemplate, ShippingRegion
from schemas import (
    ProductCreate, ProductUpdate, ProductResponse,
    ShippingTemplateCreate, ShippingTemplateResponse,
    Message, PaginatedResponse
)
from utils.auth import get_current_user

router = APIRouter(prefix="/api/costs", tags=["成本管理"])


# ==================== 商品成本管理 ====================

@router.post("/products", response_model=ProductResponse, summary="创建商品")
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建商品"""
    new_product = Product(
        user_id=current_user.id,
        **product_data.model_dump()
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return ProductResponse.model_validate(new_product)


@router.post("/products/batch", summary="批量创建商品")
async def create_products_batch(
    products: List[ProductCreate],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量创建商品"""
    created_count = 0
    for product_data in products:
        new_product = Product(
            user_id=current_user.id,
            **product_data.model_dump()
        )
        db.add(new_product)
        created_count += 1

    db.commit()
    return {"message": f"成功创建 {created_count} 个商品", "count": created_count}


@router.get("/products", response_model=PaginatedResponse, summary="获取商品列表")
async def get_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None, description="商品类目"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取商品列表"""
    query = db.query(Product).filter(Product.user_id == current_user.id)

    if category:
        query = query.filter(Product.category == category)

    if keyword:
        query = query.filter(
            (Product.name.contains(keyword)) |
            (Product.product_id.contains(keyword))
        )

    total = query.count()
    products = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[ProductResponse.model_validate(p) for p in products]
    )


@router.get("/products/{product_id}", response_model=ProductResponse, summary="获取商品详情")
async def get_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取商品详情"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )

    return ProductResponse.model_validate(product)


@router.put("/products/{product_id}", response_model=ProductResponse, summary="更新商品")
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新商品信息"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )

    # 记录成本变更历史
    if product_data.cost_price is not None and product_data.cost_price != product.cost_price:
        history = ProductCostHistory(
            product_id=product.id,
            cost_price=product_data.cost_price,
            shipping_cost=product_data.shipping_cost or product.shipping_cost,
            note="成本更新"
        )
        db.add(history)

    # 更新字段
    for field, value in product_data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return ProductResponse.model_validate(product)


@router.put("/products/{product_id}/cost", summary="设置商品成本")
async def set_product_cost(
    product_id: int,
    cost_price: Decimal,
    shipping_cost: Optional[Decimal] = None,
    commission_rate: Optional[Decimal] = None,
    ad_cost_rate: Optional[Decimal] = None,
    note: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """设置商品成本信息"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )

    # 记录历史
    history = ProductCostHistory(
        product_id=product.id,
        cost_price=cost_price,
        shipping_cost=shipping_cost or product.shipping_cost,
        note=note
    )
    db.add(history)

    # 更新成本
    product.cost_price = cost_price
    if shipping_cost is not None:
        product.shipping_cost = shipping_cost
    if commission_rate is not None:
        product.commission_rate = commission_rate
    if ad_cost_rate is not None:
        product.ad_cost_rate = ad_cost_rate

    db.commit()

    return {"message": "成本设置成功"}


@router.delete("/products/{product_id}", response_model=Message, summary="删除商品")
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除商品"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )

    db.delete(product)
    db.commit()

    return Message(message="商品删除成功")


# ==================== 运费模板管理 ====================

@router.post("/shipping-templates", response_model=ShippingTemplateResponse, summary="创建运费模板")
async def create_shipping_template(
    template_data: ShippingTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建运费模板"""
    new_template = ShippingTemplate(
        user_id=current_user.id,
        **template_data.model_dump()
    )
    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    return ShippingTemplateResponse.model_validate(new_template)


@router.get("/shipping-templates", response_model=List[ShippingTemplateResponse], summary="获取运费模板列表")
async def get_shipping_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取运费模板列表"""
    templates = db.query(ShippingTemplate).filter(
        ShippingTemplate.user_id == current_user.id
    ).all()

    return [ShippingTemplateResponse.model_validate(t) for t in templates]


@router.get("/shipping-templates/{template_id}", response_model=ShippingTemplateResponse, summary="获取运费模板详情")
async def get_shipping_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取运费模板详情"""
    template = db.query(ShippingTemplate).filter(
        ShippingTemplate.id == template_id,
        ShippingTemplate.user_id == current_user.id
    ).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="运费模板不存在"
        )

    return ShippingTemplateResponse.model_validate(template)


@router.put("/shipping-templates/{template_id}", response_model=ShippingTemplateResponse, summary="更新运费模板")
async def update_shipping_template(
    template_id: int,
    template_data: ShippingTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新运费模板"""
    template = db.query(ShippingTemplate).filter(
        ShippingTemplate.id == template_id,
        ShippingTemplate.user_id == current_user.id
    ).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="运费模板不存在"
        )

    for field, value in template_data.model_dump(exclude_unset=True).items():
        setattr(template, field, value)

    db.commit()
    db.refresh(template)

    return ShippingTemplateResponse.model_validate(template)


@router.delete("/shipping-templates/{template_id}", response_model=Message, summary="删除运费模板")
async def delete_shipping_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除运费模板"""
    template = db.query(ShippingTemplate).filter(
        ShippingTemplate.id == template_id,
        ShippingTemplate.user_id == current_user.id
    ).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="运费模板不存在"
        )

    db.delete(template)
    db.commit()

    return Message(message="运费模板删除成功")


@router.post("/shipping-templates/{template_id}/set-default", summary="设置默认运费模板")
async def set_default_shipping_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """设置默认运费模板"""
    # 清除其他默认
    db.query(ShippingTemplate).filter(
        ShippingTemplate.user_id == current_user.id
    ).update({"is_default": False})

    # 设置新的默认
    template = db.query(ShippingTemplate).filter(
        ShippingTemplate.id == template_id,
        ShippingTemplate.user_id == current_user.id
    ).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="运费模板不存在"
        )

    template.is_default = True
    db.commit()

    return {"message": "已设置为默认模板"}


# ==================== 佣金计算 ====================

@router.post("/calculate/commission", summary="计算平台佣金")
async def calculate_commission(
    amount: Decimal,
    commission_rate: Decimal = Decimal("0.006"),  # 拼多多默认0.6%
    current_user: User = Depends(get_current_user)
):
    """计算平台佣金"""
    commission = amount * commission_rate
    return {
        "amount": amount,
        "commission_rate": commission_rate,
        "commission": commission,
        "actual_amount": amount - commission
    }


@router.post("/calculate/profit", summary="计算利润")
async def calculate_profit(
    sale_price: Decimal,
    quantity: int,
    cost_price: Decimal,
    shipping_cost: Decimal = Decimal("0"),
    commission_rate: Decimal = Decimal("0.006"),
    ad_cost_rate: Decimal = Decimal("0"),
    other_cost: Decimal = Decimal("0")
):
    """计算订单利润"""
    # 销售总额
    total_sales = sale_price * quantity

    # 各项成本
    product_cost = cost_price * quantity
    commission = total_sales * commission_rate
    ad_cost = total_sales * ad_cost_rate

    # 总成本
    total_cost = product_cost + shipping_cost + commission + ad_cost + other_cost

    # 利润
    gross_profit = total_sales - total_cost
    profit_rate = (gross_profit / total_sales * 100) if total_sales > 0 else Decimal("0")

    return {
        "total_sales": total_sales,
        "cost_breakdown": {
            "product_cost": product_cost,
            "shipping_cost": shipping_cost,
            "commission": commission,
            "ad_cost": ad_cost,
            "other_cost": other_cost,
            "total_cost": total_cost
        },
        "gross_profit": gross_profit,
        "profit_rate": profit_rate
    }
