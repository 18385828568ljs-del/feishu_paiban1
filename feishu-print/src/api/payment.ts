import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export interface Plan {
  id: string;
  name: string;
  price: number;  // 分
  original_price: number;
  duration_days: number;
}

export interface Order {
  id: number;
  order_no: string;
  plan_type: string;
  amount: number;
  status: 'pending' | 'paid' | 'cancelled';
  expires_at: string | null;
  paid_at: string | null;
  created_at: string;
}

export const paymentApi = {
  /**
   * 获取会员计划列表
   */
  async getPlans(): Promise<{ plans: Plan[] }> {
    const response = await axios.get(`${API_BASE}/api/payment/plans`);
    return response.data;
  },

  /**
   * 创建订单
   */
  async createOrder(feishuUserId: string, planType: string): Promise<Order> {
    const response = await axios.post(`${API_BASE}/api/payment/create-order`, {
      feishu_user_id: feishuUserId,
      plan_type: planType
    });
    return response.data;
  },

  /**
   * 创建支付宝扫码支付订单
   */
  async createAlipayNativePay(feishuUserId: string, planType: string): Promise<{ qr_code_url: string; order_no: string }> {
    const response = await axios.post(`${API_BASE}/api/payment/alipay/create`, {
      feishu_user_id: feishuUserId,
      plan_type: planType
    });
    return response.data;
  },

  /**
   * 查询订单状态
   */
  async getOrderStatus(orderNo: string): Promise<{ order_no: string; status: string; paid_at: string | null }> {
    const response = await axios.get(`${API_BASE}/api/payment/alipay/query`, {
      params: { order_no: orderNo }
    });
    return response.data;
  },

  /**
   * 获取订单列表
   */
  async getOrders(feishuUserId: string): Promise<{ orders: Order[] }> {
    const response = await axios.get(`${API_BASE}/api/payment/orders`, {
      params: { feishu_user_id: feishuUserId }
    });
    return response.data;
  }
};









