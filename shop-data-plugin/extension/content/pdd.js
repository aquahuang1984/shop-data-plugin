/**
 * 店铺数据分析助手 - 内容脚本
 * 用于在拼多多商家后台页面抓取订单数据
 */

(function() {
  'use strict';

  // 配置
  const CONFIG = {
    orderListSelector: '.order-list-table, .order-table, [class*="orderList"]',
    orderRowSelector: 'tr[class*="order"], tbody tr',
    paginationSelector: '.ant-pagination, .el-pagination'
  };

  /**
   * 抓取订单数据
   */
  function grabOrders() {
    const orders = [];

    try {
      // 查找订单列表
      const orderTables = document.querySelectorAll(CONFIG.orderListSelector);

      orderTables.forEach(table => {
        const rows = table.querySelectorAll(CONFIG.orderRowSelector);

        rows.forEach(row => {
          try {
            const order = parseOrderRow(row);
            if (order && order.order_id) {
              orders.push(order);
            }
          } catch (e) {
            console.error('解析订单行失败:', e);
          }
        });
      });

      // 如果没找到表格，尝试其他方式
      if (orders.length === 0) {
        const alternativeOrders = tryAlternativeGrab();
        orders.push(...alternativeOrders);
      }

    } catch (error) {
      console.error('抓取订单失败:', error);
    }

    return orders;
  }

  /**
   * 解析订单行
   */
  function parseOrderRow(row) {
    const cells = row.querySelectorAll('td');
    if (cells.length < 5) return null;

    const order = {};

    // 尝试提取订单号
    const orderNoEl = row.querySelector('[class*="orderNo"], [class*="order-no"], [data-order-id]');
    if (orderNoEl) {
      order.order_id = orderNoEl.textContent.trim();
    }

    // 如果没找到，尝试从文本中提取
    if (!order.order_id) {
      const text = row.textContent;
      const orderNoMatch = text.match(/(\d{15,25})/);
      if (orderNoMatch) {
        order.order_id = orderNoMatch[1];
      }
    }

    // 提取商品名称
    const productEl = row.querySelector('[class*="product"], [class*="goods"]');
    if (productEl) {
      order.product_name = productEl.textContent.trim().slice(0, 255);
    }

    // 提取数量
    const qtyEl = row.querySelector('[class*="qty"], [class*="quantity"], [class*="num"]');
    if (qtyEl) {
      const qtyMatch = qtyEl.textContent.match(/\d+/);
      if (qtyMatch) {
        order.quantity = parseInt(qtyMatch[0]);
      }
    }

    // 提取金额
    const amountEl = row.querySelector('[class*="amount"], [class*="price"], [class*="money"]');
    if (amountEl) {
      const amountMatch = amountEl.textContent.match(/[\d.]+/);
      if (amountMatch) {
        order.total_amount = parseFloat(amountMatch[0]);
      }
    }

    // 提取状态
    const statusEl = row.querySelector('[class*="status"], [class*="state"]');
    if (statusEl) {
      order.status = statusEl.textContent.trim();
    }

    // 提取买家信息
    const buyerEl = row.querySelector('[class*="buyer"], [class*="customer"]');
    if (buyerEl) {
      order.buyer_name = buyerEl.textContent.trim().slice(0, 50);
    }

    return order.order_id ? order : null;
  }

  /**
   * 尝试其他抓取方式
   */
  function tryAlternativeGrab() {
    const orders = [];

    // 方法1: 查找所有看起来像订单号的元素
    const allElements = document.querySelectorAll('*');
    const orderNoPattern = /\d{15,25}/g;

    const foundOrderNos = new Set();

    allElements.forEach(el => {
      const text = el.textContent;
      if (text && text.length < 100) { // 避免匹配太长的文本
        const matches = text.match(orderNoPattern);
        if (matches) {
          matches.forEach(no => foundOrderNos.add(no));
        }
      }
    });

    foundOrderNos.forEach(orderId => {
      orders.push({
        order_id: orderId,
        platform: '拼多多',
        status: '未知'
      });
    });

    return orders;
  }

  /**
   * 发送数据到后台
   */
  async function sendToBackground(orders) {
    if (orders.length === 0) {
      return { success: false, message: '未找到订单数据' };
    }

    try {
      const response = await chrome.runtime.sendMessage({
        action: 'saveOrders',
        orders: orders
      });
      return response;
    } catch (error) {
      console.error('发送数据失败:', error);
      return { success: false, message: error.message };
    }
  }

  /**
   * 显示抓取按钮
   */
  function injectGrabButton() {
    // 检查是否已存在
    if (document.getElementById('shop-data-grab-btn')) return;

    // 创建按钮
    const btn = document.createElement('button');
    btn.id = 'shop-data-grab-btn';
    btn.textContent = '📊 抓取订单数据';
    btn.style.cssText = `
      position: fixed;
      top: 100px;
      right: 20px;
      z-index: 99999;
      padding: 10px 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-size: 14px;
      box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
      transition: all 0.3s ease;
    `;

    btn.onmouseover = () => {
      btn.style.transform = 'translateY(-2px)';
      btn.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.6)';
    };

    btn.onmouseout = () => {
      btn.style.transform = 'translateY(0)';
      btn.style.boxShadow = '0 4px 15px rgba(102, 126, 234, 0.4)';
    };

    btn.onclick = async () => {
      btn.textContent = '⏳ 抓取中...';
      btn.disabled = true;

      const orders = grabOrders();

      if (orders.length > 0) {
        const result = await sendToBackground(orders);
        if (result.success) {
          btn.textContent = `✓ 已抓取 ${orders.length} 条`;
          setTimeout(() => {
            btn.textContent = '📊 抓取订单数据';
            btn.disabled = false;
          }, 2000);
        } else {
          btn.textContent = `✗ ${result.message}`;
          setTimeout(() => {
            btn.textContent = '📊 抓取订单数据';
            btn.disabled = false;
          }, 2000);
        }
      } else {
        btn.textContent = '✗ 未找到订单';
        setTimeout(() => {
          btn.textContent = '📊 抓取订单数据';
          btn.disabled = false;
        }, 2000);
      }
    };

    document.body.appendChild(btn);
  }

  /**
   * 监听来自popup的消息
   */
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'grabOrders') {
      const orders = grabOrders();
      sendResponse({
        success: true,
        count: orders.length,
        orders: orders
      });
    }
    return true;
  });

  // 页面加载完成后注入按钮
  if (document.readyState === 'complete') {
    injectGrabButton();
  } else {
    window.addEventListener('load', injectGrabButton);
  }

})();
