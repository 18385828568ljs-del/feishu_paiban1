import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export interface PromoCode {
  id: number;
  code: string;
  plan_type: string;
  duration_days: number;
  max_uses: number;
  used_count: number;
  is_active: number;
  expires_at: string | null;
  created_at: string;
}

export const promoApi = {
  /**
   * 生成邀请码（管理员）
   */
  async generate(planType: string, durationDays: number = 30, maxUses: number = 1, expiresAt?: string): Promise<PromoCode> {
    const response = await axios.post(`${API_BASE}/api/promo/generate`, {
      plan_type: planType,
      duration_days: durationDays,
      max_uses: maxUses,
      expires_at: expiresAt
    });
    return response.data;
  },

  /**
   * 兑换邀请码
   */
  async redeem(code: string, feishuUserId: string): Promise<{ success: boolean; message: string }> {
    const response = await axios.post(`${API_BASE}/api/promo/redeem`, {
      code: code,
      feishu_user_id: feishuUserId
    });
    return response.data;
  },

  /**
   * 获取邀请码列表（管理员）
   */
  async list(): Promise<{ promo_codes: PromoCode[] }> {
    const response = await axios.get(`${API_BASE}/api/promo/list`);
    return response.data;
  }
};









