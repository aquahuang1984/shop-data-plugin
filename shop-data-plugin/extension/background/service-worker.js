/**
 * 店铺数据分析助手 - Service Worker
 * 后台服务脚本
 */

// API配置
let API_URL = 'http://localhost:8000';

// 初始化
chrome.storage.local.get(['apiUrl'], (result) => {
  if (result.apiUrl) {
    API_URL = result.apiUrl;
  }
});

/**
 * 监听存储变化
 */
chrome.storage.onChanged.addListener((changes, namespace) => {
  if (changes.apiUrl) {
    API_URL = changes.apiUrl.newValue;
  }
});

/**
 * 监听来自content script的消息
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'saveOrders') {
    saveOrdersToServer(request.orders)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, message: error.message }));
    return true;
  }
});

/**
 * 保存订单到服务器
 */
async function saveOrdersToServer(orders) {
  try {
    const token = await getStoredToken();
    if (!token) {
      return { success: false, message: '请先登录' };
    }

    // 批量创建订单
    const response = await fetch(`${API_URL}/api/orders/import`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: await createFormData(orders)
    });

    if (response.ok) {
      const data = await response.json();
      return { success: true, message: data.message, count: data.imported };
    } else {
      const error = await response.json();
      return { success: false, message: error.detail };
    }
  } catch (error) {
    return { success: false, message: error.message };
  }
}

/**
 * 创建FormData
 */
async function createFormData(orders) {
  // 由于后端期望文件上传，需要将订单转为JSON文件
  const jsonStr = JSON.stringify(orders);
  const blob = new Blob([jsonStr], { type: 'application/json' });
  const formData = new FormData();
  formData.append('file', blob, 'orders.json');
  return formData;
}

/**
 * 获取存储的Token
 */
function getStoredToken() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['token'], (result) => {
      resolve(result.token);
    });
  });
}

/**
 * 扩展安装/更新事件
 */
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('扩展已安装');
    // 打开欢迎页面
    chrome.tabs.create({
      url: chrome.runtime.getURL('options/index.html')
    });
  } else if (details.reason === 'update') {
    console.log('扩展已更新到版本:', chrome.runtime.getManifest().version);
  }
});

/**
 * 定时同步数据（可选功能）
 * 注意：需要先创建alarm才能监听
 */
if (chrome.alarms) {
  chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === 'syncData') {
      syncData();
    }
  });
}

/**
 * 同步数据
 */
async function syncData() {
  // TODO: 实现数据同步逻辑
  console.log('同步数据...');
}
