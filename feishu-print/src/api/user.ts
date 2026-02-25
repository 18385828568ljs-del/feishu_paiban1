import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export interface UserStatus {
  id: number;
  feishu_user_id: string;
  nickname: string | null;
  plan_type: 'free' | 'pro' | 'team';
  expires_at: string | null;
  pdf_exports_used: number;
  pdf_exports_limit: number;
  ai_generates_used: number;
  ai_generates_limit: number;
  can_use_signature: boolean;
  can_use_premium_templates: boolean;
}

export interface PermissionResult {
  allowed: boolean;
  reason?: string;
  remaining?: number;
}

export const userApi = {
  /**
   * 初始化用户（首次使用时调用）
   */
  async init(feishuUserId: string, tenantKey?: string, nickname?: string, clientFingerprint?: string): Promise<{ user: UserStatus; session_token: string }> {
    const response = await axios.post(`${API_BASE}/api/user/init`, {
      feishu_user_id: feishuUserId,
      tenant_key: tenantKey,
      nickname: nickname,
      client_fingerprint: clientFingerprint
    });
    return response.data;
  },

  /**
   * 获取用户会员状态
   */
  async getStatus(feishuUserId: string): Promise<UserStatus> {
    const response = await axios.get(`${API_BASE}/api/user/status/${feishuUserId}`);
    return response.data;
  },

  /**
   * 检查功能权限
   * @param feature 功能名称: 'pdf_export', 'ai_generate', 'signature', 'premium_templates'
   */
  async checkPermission(feishuUserId: string, feature: string): Promise<PermissionResult> {
    const response = await axios.post(`${API_BASE}/api/user/check-permission`, {
      feishu_user_id: feishuUserId,
      feature: feature
    });
    return response.data;
  },

  /**
   * 记录功能使用（消耗次数）
   * @param feature 功能名称: 'pdf_export', 'ai_generate'
   */
  async useFeature(feishuUserId: string, feature: string): Promise<void> {
    await axios.post(`${API_BASE}/api/user/use-feature`, {
      feishu_user_id: feishuUserId,
      feature: feature
    });
  }
};
