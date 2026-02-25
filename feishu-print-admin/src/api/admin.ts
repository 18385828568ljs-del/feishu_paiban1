import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器 - 添加token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('admin_token');
  if (token) {
    // 确保 headers 对象存在
    if (!config.headers) {
      config.headers = {};
    }
    (config.headers as any).Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器 - 统一处理未授权，自动跳转登录
api.interceptors.response.use(
  response => response,
  error => {
    const status = error?.response?.status;
    if (status === 401) {
      // 清理本地管理员登录信息
      localStorage.removeItem('admin_token');
      localStorage.removeItem('admin_user');

      // 仅在管理后台路径下才重定向，避免影响其它站点
      const currentPath = window.location.pathname || '';
      if (currentPath.startsWith('/admin') && currentPath !== '/admin/login') {
        window.location.href = '/admin/login';
      }
    }
    return Promise.reject(error);
  }
);

export const adminApi = {
  // 登录
  async login(username: string, password: string) {
    const response = await api.post('/api/admin/login', { username, password });
    return response.data;
  },

  // 获取统计数据
  async getStats() {
    const response = await api.get('/api/admin/stats');
    return response.data;
  },

  // 用户管理
  async getUsers(params: { page: number; pageSize: number; search?: string; planType?: string }) {
    const response = await api.get('/api/admin/users', { params });
    return response.data;
  },

  async updateUserMembership(userId: number, data: { plan_type: string; duration_days: number }) {
    const response = await api.put(`/api/admin/users/${userId}/membership`, data);
    return response.data;
  },

  // 订单管理
  async getOrders(params: { page: number; pageSize: number; search?: string; status?: string }) {
    const response = await api.get('/api/admin/orders', { params });
    return response.data;
  },

  async refundOrder(orderId: number, reason: string) {
    const response = await api.post(`/api/admin/orders/${orderId}/refund`, { reason });
    return response.data;
  },

  // 会员计划管理
  async getPlans() {
    const response = await api.get('/api/admin/plans');
    return response.data;
  },

  async updatePlan(
    planId: string,
    data: { name?: string; price?: number; original_price?: number; duration_days?: number }
  ) {
    const response = await api.put(`/api/admin/plans/${planId}`, data);
    return response.data;
  },

  // 邀请码管理
  async getPromos() {
    const response = await api.get('/api/admin/promos');
    return response.data;
  },

  async createPromo(data: {
    code?: string;
    plan_type: string;
    duration_days: number;
    max_uses: number;
    expires_days?: number | null;
  }) {
    const response = await api.post('/api/admin/promos', data);
    return response.data;
  },

  async togglePromo(promoId: number) {
    const response = await api.put(`/api/admin/promos/${promoId}/toggle`);
    return response.data;
  },

  async deletePromo(promoId: number) {
    const response = await api.delete(`/api/admin/promos/${promoId}`);
    return response.data;
  },

  // 反馈管理
  async getFeedbacks() {
    const response = await api.get('/api/admin/feedbacks');
    return response.data;
  },

  async markFeedbackRead(feedbackId: number) {
    const response = await api.put(`/api/admin/feedbacks/${feedbackId}/read`);
    return response.data;
  },

  async deleteFeedback(feedbackId: number) {
    const response = await api.delete(`/api/admin/feedbacks/${feedbackId}`);
    return response.data;
  }
};
