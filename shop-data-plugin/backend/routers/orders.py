"""
订单管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import pandas as pd
import io

from database import get_db
from models.user import User
from models.order import Order, OrderStatus
from models.product import Product
from schemas import (
    OrderCreate, OrderUpdate, OrderResponse,
    SalesStats, DailyStats, ProductStats,
    Message, PaginatedResponse
)
from utils.auth import get_current_user

router = APIRouter(prefix="/api/orders", tags=["订单管理"])


@router.post("", response_model=OrderResponse, summary="创建订单")
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建单个订单"""
    # 检查订单号是否已存在
    existing_order = db.query(Order).filter(Order.order_id == order_data.order_id).first()
    if existing_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单号已存在"
        )

    # 创建订单
    new_order = Order(
        user_id=current_user.id,
        **order_data.model_dump()
    )

    # 计算利润
    new_order.calculate_profit()

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return OrderResponse.model_validate(new_order)


@router.post("/import", summary="导入订单文件")
async def import_orders(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导入Excel/CSV订单文件"""
    # 检查文件类型
    filename = file.filename.lower()
    if not (filename.endswith('.xlsx') or filename.endswith('.xls') or filename.endswith('.csv')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="仅支持Excel(.xlsx, .xls)和CSV格式文件"
        )

    try:
        # 读取文件内容
        content = await file.read()

        # 解析文件
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))

        # 标准化列名（拼多多订单导出格式）
        column_mapping = {
            "订单编号": "order_id",
            "商品名称": "product_name",
            "商品规格": "sku_name",
            "商品数量": "quantity",
            "商品单价": "sale_price",
            "订单金额": "total_amount",
            "订单状态": "status",
            "下单时间": "order_time",
            "收货人姓名": "buyer_name",
            "收货人手机": "buyer_phone",
            "省": "province",
            "市": "city",
            "区": "district"
        }

        # 重命名列
        df = df.rename(columns=column_mapping)

        # 转换数据并导入
        imported_count = 0
        skipped_count = 0

        for _, row in df.iterrows():
            try:
                order_id = str(row.get("order_id", "")).strip()
                if not order_id:
                    skipped_count += 1
                    continue

                # 检查是否已存在
                existing = db.query(Order).filter(Order.order_id == order_id).first()
                if existing:
                    skipped_count += 1
                    continue

                # 处理时间
                order_time = None
                if "order_time" in row and pd.notna(row["order_time"]):
                    try:
                        if isinstance(row["order_time"], str):
                            order_time = datetime.strptime(row["order_time"], "%Y-%m-%d %H:%M:%S")
                        else:
                            order_time = pd.to_datetime(row["order_time"]).to_pydatetime()
                    except:
                        pass

                # 创建订单
                new_order = Order(
                    user_id=current_user.id,
                    order_id=order_id,
                    product_name=str(row.get("product_name", ""))[:255] if pd.notna(row.get("product_name")) else None,
                    sku_name=str(row.get("sku_name", ""))[:255] if pd.notna(row.get("sku_name")) else None,
                    quantity=int(row.get("quantity", 1)) if pd.notna(row.get("quantity")) else 1,
                    sale_price=Decimal(str(row.get("sale_price", 0))) if pd.notna(row.get("sale_price")) else Decimal("0"),
                    total_amount=Decimal(str(row.get("total_amount", 0))) if pd.notna(row.get("total_amount")) else Decimal("0"),
                    status=str(row.get("status", "未知"))[:20] if pd.notna(row.get("status")) else "未知",
                    order_time=order_time,
                    buyer_name=str(row.get("buyer_name", ""))[:50] if pd.notna(row.get("buyer_name")) else None,
                    buyer_phone=str(row.get("buyer_phone", ""))[:20] if pd.notna(row.get("buyer_phone")) else None,
                    province=str(row.get("province", ""))[:20] if pd.notna(row.get("province")) else None,
                    city=str(row.get("city", ""))[:20] if pd.notna(row.get("city")) else None,
                    district=str(row.get("district", ""))[:20] if pd.notna(row.get("district")) else None,
                    platform="拼多多"
                )

                # 计算利润
                new_order.calculate_profit()

                db.add(new_order)
                imported_count += 1

            except Exception as e:
                skipped_count += 1
                continue

        db.commit()

        return {
            "message": f"成功导入 {imported_count} 条订单，跳过 {skipped_count} 条",
            "imported": imported_count,
            "skipped": skipped_count
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件解析失败: {str(e)}"
        )


@router.get("", response_model=PaginatedResponse, summary="获取订单列表")
async def get_orders(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="订单状态"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取订单列表（分页）"""
    query = db.query(Order).filter(Order.user_id == current_user.id)

    # 筛选条件
    if status:
        query = query.filter(Order.status == status)

    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Order.order_time >= start_dt)
        except:
            pass

    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(Order.order_time < end_dt)
        except:
            pass

    if keyword:
        query = query.filter(
            (Order.order_id.contains(keyword)) |
            (Order.product_name.contains(keyword)) |
            (Order.buyer_name.contains(keyword))
        )

    # 排序
    query = query.order_by(Order.order_time.desc())

    # 总数
    total = query.count()

    # 分页
    orders = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[OrderResponse.model_validate(order) for order in orders]
    )


@router.get("/{order_id}", response_model=OrderResponse, summary="获取订单详情")
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取订单详情"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    return OrderResponse.model_validate(order)


@router.put("/{order_id}", response_model=OrderResponse, summary="更新订单")
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新订单信息"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    # 更新字段
    for field, value in order_data.model_dump(exclude_unset=True).items():
        setattr(order, field, value)

    # 重新计算利润
    order.calculate_profit()

    db.commit()
    db.refresh(order)

    return OrderResponse.model_validate(order)


@router.delete("/{order_id}", response_model=Message, summary="删除订单")
async def delete_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除订单"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    db.delete(order)
    db.commit()

    return Message(message="订单删除成功")


@router.delete("/batch", response_model=Message, summary="批量删除订单")
async def delete_orders_batch(
    order_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量删除订单"""
    deleted = db.query(Order).filter(
        Order.id.in_(order_ids),
        Order.user_id == current_user.id
    ).delete(synchronize_session=False)

    db.commit()

    return Message(message=f"成功删除 {deleted} 条订单")


@router.get("/stats/overview", response_model=SalesStats, summary="获取销售统计概览")
async def get_sales_stats(
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取销售统计概览"""
    query = db.query(Order).filter(Order.user_id == current_user.id)

    # 时间筛选
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Order.order_time >= start_dt)
        except:
            pass

    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(Order.order_time < end_dt)
        except:
            pass

    orders = query.all()

    # 计算统计数据
    total_orders = len(orders)
    total_quantity = sum(o.quantity for o in orders)
    total_sales = sum(o.total_amount for o in orders)
    total_cost = sum(
        (o.cost_price * o.quantity) + o.shipping_cost + o.commission + o.ad_cost + o.other_cost
        for o in orders
    )
    total_profit = sum(o.gross_profit for o in orders)

    avg_order_value = total_sales / total_orders if total_orders > 0 else Decimal("0")
    profit_rate = (total_profit / total_sales * 100) if total_sales > 0 else Decimal("0")

    return SalesStats(
        total_orders=total_orders,
        total_quantity=total_quantity,
        total_sales=total_sales,
        total_cost=total_cost,
        total_profit=total_profit,
        avg_order_value=avg_order_value,
        profit_rate=profit_rate
    )


@router.get("/stats/daily", response_model=List[DailyStats], summary="获取每日统计")
async def get_daily_stats(
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取每日销售统计"""
    query = db.query(
        func.date(Order.order_time).label("date"),
        func.count(Order.id).label("orders"),
        func.sum(Order.total_amount).label("sales"),
        func.sum(Order.gross_profit).label("profit")
    ).filter(Order.user_id == current_user.id)

    # 时间筛选
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Order.order_time >= start_dt)
        except:
            pass

    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(Order.order_time < end_dt)
        except:
            pass

    results = query.group_by(func.date(Order.order_time)).order_by(func.date(Order.order_time)).all()

    return [
        DailyStats(
            date=str(r.date),
            orders=r.orders,
            sales=r.sales or Decimal("0"),
            profit=r.profit or Decimal("0")
        )
        for r in results
    ]


@router.get("/stats/products", response_model=List[ProductStats], summary="获取商品统计")
async def get_product_stats(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取商品销售统计排行"""
    results = db.query(
        Order.product_name,
        func.sum(Order.quantity).label("quantity"),
        func.sum(Order.total_amount).label("sales"),
        func.sum(Order.gross_profit).label("profit")
    ).filter(
        Order.user_id == current_user.id,
        Order.product_name.isnot(None)
    ).group_by(Order.product_name).order_by(func.sum(Order.total_amount).desc()).limit(limit).all()

    return [
        ProductStats(
            product_name=r.product_name or "未知商品",
            quantity=r.quantity,
            sales=r.sales or Decimal("0"),
            profit=r.profit or Decimal("0"),
            profit_rate=(r.profit / r.sales * 100) if r.sales and r.sales > 0 else Decimal("0")
        )
        for r in results
    ]
