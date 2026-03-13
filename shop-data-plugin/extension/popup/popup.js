/**
 * 店铺数据分析助手 - 弹窗脚本
 */

// API配置
const DEFAULT_API_URL = 'http://localhost:8000';

// 创建Vue应用
const app = Vue.createApp({
  data() {
    return {
      // 状态
      isLoggedIn: false,
      loading: false,
      errorMsg: '',
      activeTab: 'login',
      currentTab: 'overview',
      isPddPage: false,

      // 用户数据
      user: null,
      token: null,

      // 表单数据
      loginForm: {
        username: '',
        password: ''
      },
      registerForm: {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      },

      // 统计数据
      stats: {
        totalOrders: 0,
        totalSales: 0,
        totalProfit: 0,
        profitRate: 0
      },

      // 订单列表
      orders: [],
      searchKeyword: '',

      // 商品列表
      products: [],
      productSearch: '',

      // 弹窗控制
      showImportModal: false,
      showAddProductModal: false,

      // 设置
      apiUrl: DEFAULT_API_URL,
      defaultCommissionRate: 0.006,

      // 标签页配置
      tabs: [
        { id: 'overview', name: '数据概览' },
        { id: 'orders', name: '订单管理' },
        { id: 'costs', name: '成本管理' },
        { id: 'settings', name: '设置' }
      ]
    };
  },

  mounted() {
    this.init();
  },

  methods: {
    /**
     * 初始化
     */
    async init() {
      // 加载设置
      await this.loadSettings();

      // 检查登录状态
      await this.checkAuth();

      // 检查当前页面
      this.checkCurrentPage();
    },

    /**
     * 加载设置
     */
    async loadSettings() {
      const result = await chrome.storage.local.get(['token', 'user', 'apiUrl', 'defaultCommissionRate']);
      if (result.token) {
        this.token = result.token;
        this.user = result.user;
        this.isLoggedIn = true;
      }
      if (result.apiUrl) {
        this.apiUrl = result.apiUrl;
      }
      if (result.defaultCommissionRate) {
        this.defaultCommissionRate = result.defaultCommissionRate;
      }
    },

    /**
     * 检查认证状态
     */
    async checkAuth() {
      if (this.token) {
        try {
          const response = await this.apiRequest('/api/auth/me', 'GET');
          if (response.ok) {
            const data = await response.json();
            this.user = data;
            this.isLoggedIn = true;
            await this.loadStats();
          } else {
            this.logout();
          }
        } catch (error) {
          console.error('认证检查失败:', error);
        }
      }
    },

    /**
     * 检查当前页面
     */
    checkCurrentPage() {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0] && tabs[0].url) {
          this.isPddPage = tabs[0].url.includes('mms.pinduoduo.com');
        }
      });
    },

    /**
     * 登录
     */
    async handleLogin() {
      this.loading = true;
      this.errorMsg = '';

      try {
        const formData = new FormData();
        formData.append('username', this.loginForm.username);
        formData.append('password', this.loginForm.password);

        const response = await this.apiRequest('/api/auth/login', 'POST', formData, false);

        if (response.ok) {
          const data = await response.json();
          this.token = data.access_token;
          this.user = data.user;
          this.isLoggedIn = true;

          // 保存到storage
          await chrome.storage.local.set({
            token: this.token,
            user: this.user
          });

          // 加载数据
          await this.loadStats();
        } else {
          const error = await response.json();
          this.errorMsg = error.detail || '登录失败';
        }
      } catch (error) {
        this.errorMsg = '网络错误，请检查服务器连接';
      } finally {
        this.loading = false;
      }
    },

    /**
     * 注册
     */
    async handleRegister() {
      if (this.registerForm.password !== this.registerForm.confirmPassword) {
        this.errorMsg = '两次密码输入不一致';
        return;
      }

      this.loading = true;
      this.errorMsg = '';

      try {
        const response = await this.apiRequest('/api/auth/register', 'POST', {
          username: this.registerForm.username,
          email: this.registerForm.email || null,
          password: this.registerForm.password
        });

        if (response.ok) {
          const data = await response.json();
          this.token = data.access_token;
          this.user = data.user;
          this.isLoggedIn = true;

          await chrome.storage.local.set({
            token: this.token,
            user: this.user
          });
        } else {
          const error = await response.json();
          this.errorMsg = error.detail || '注册失败';
        }
      } catch (error) {
        this.errorMsg = '网络错误';
      } finally {
        this.loading = false;
      }
    },

    /**
     * 登出
     */
    async handleLogout() {
      await chrome.storage.local.remove(['token', 'user']);
      this.token = null;
      this.user = null;
      this.isLoggedIn = false;
    },

    /**
     * 加载统计数据
     */
    async loadStats() {
      try {
        const response = await this.apiRequest('/api/orders/stats/overview', 'GET');
        if (response.ok) {
          const data = await response.json();
          this.stats = {
            totalOrders: data.total_orders,
            totalSales: data.total_sales,
            totalProfit: data.total_profit,
            profitRate: data.profit_rate.toFixed(2)
          };
        }
      } catch (error) {
        console.error('加载统计数据失败:', error);
      }
    },

    /**
     * 加载订单列表
     */
    async loadOrders() {
      try {
        const response = await this.apiRequest('/api/orders?page=1&page_size=50', 'GET');
        if (response.ok) {
          const data = await response.json();
          this.orders = data.items;
        }
      } catch (error) {
        console.error('加载订单失败:', error);
      }
    },

    /**
     * 加载商品列表
     */
    async loadProducts() {
      try {
        const response = await this.apiRequest('/api/costs/products?page=1&page_size=50', 'GET');
        if (response.ok) {
          const data = await response.json();
          this.products = data.items;
        }
      } catch (error) {
        console.error('加载商品失败:', error);
      }
    },

    /**
     * 触发文件选择
     */
    triggerFileInput() {
      this.$refs.fileInput.click();
    },

    /**
     * 处理文件导入
     */
    async handleFileImport(event) {
      const file = event.target.files[0];
      if (!file) return;

      this.loading = true;
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await this.apiRequest('/api/orders/import', 'POST', formData);
        if (response.ok) {
          const data = await response.json();
          alert(data.message);
          this.showImportModal = false;
          await this.loadStats();
          await this.loadOrders();
        } else {
          const error = await response.json();
          alert('导入失败: ' + error.detail);
        }
      } catch (error) {
        alert('导入失败: ' + error.message);
      } finally {
        this.loading = false;
        event.target.value = '';
      }
    },

    /**
     * 抓取订单
     */
    async grabOrders() {
      try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tab && tab.id) {
          const response = await chrome.tabs.sendMessage(tab.id, { action: 'grabOrders' });
          if (response && response.success) {
            alert(`成功抓取 ${response.count} 条订单`);
            await this.loadStats();
          }
        }
      } catch (error) {
        alert('抓取失败: ' + error.message);
      }
    },

    /**
     * 导出报表
     */
    async exportReport() {
      try {
        const response = await this.apiRequest('/api/reports/orders/excel', 'GET');
        if (response.ok) {
          const blob = await response.blob();
          const url = URL.createObjectURL(blob);
          const filename = `订单报表_${new Date().toISOString().slice(0, 10)}.xlsx`;

          chrome.downloads.download({
            url: url,
            filename: filename,
            saveAs: true
          });
        }
      } catch (error) {
        alert('导出失败: ' + error.message);
      }
    },

    /**
     * 保存设置
     */
    async saveSettings() {
      await chrome.storage.local.set({
        apiUrl: this.apiUrl,
        defaultCommissionRate: this.defaultCommissionRate
      });
      alert('设置已保存');
    },

    /**
     * API请求封装
     */
    async apiRequest(endpoint, method = 'GET', body = null, json = true) {
      const url = this.apiUrl + endpoint;
      const headers = {
        'Authorization': `Bearer ${this.token}`
      };

      const options = {
        method,
        headers
      };

      if (body && !(body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(body);
      } else if (body instanceof FormData) {
        options.body = body;
      }

      return fetch(url, options);
    },

    /**
     * 格式化数字
     */
    formatNumber(num) {
      if (num >= 10000) {
        return (num / 10000).toFixed(2) + '万';
      }
      return num.toFixed(2);
    },

    /**
     * 获取状态样式类
     */
    getStatusClass(status) {
      const statusMap = {
        '已签收': 'success',
        '已发货': 'info',
        '待发货': 'warning',
        '已取消': 'danger',
        '已退款': 'danger'
      };
      return statusMap[status] || 'default';
    },

    /**
     * 编辑商品
     */
    editProduct(product) {
      // TODO: 实现编辑功能
      console.log('编辑商品:', product);
    }
  },

  watch: {
    currentTab(newTab) {
      if (newTab === 'orders') {
        this.loadOrders();
      } else if (newTab === 'costs') {
        this.loadProducts();
      }
    }
  }
});

app.mount('#app');
