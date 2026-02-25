import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export interface Team {
  id: number;
  name: string;
  description: string | null;
  owner_id: number;
  max_members: number;
  member_count: number;
  created_at: string;
}

export interface TeamMember {
  id: number;
  user_id: number;
  feishu_user_id: string;
  nickname: string | null;
  role: 'owner' | 'admin' | 'member';
  joined_at: string;
}

export interface TeamTemplate {
  id: number;
  template_id: number;
  template_name: string;
  shared_by_nickname: string | null;
  can_edit: boolean;
  created_at: string;
}

export interface InviteResult {
  invite_code: string;
  expires_at: string;
}

export const teamApi = {
  /**
   * 创建团队
   */
  async createTeam(feishuUserId: string, name: string, description?: string): Promise<Team> {
    const response = await axios.post(`${API_BASE}/api/team/create?feishu_user_id=${feishuUserId}`, {
      name,
      description
    });
    return response.data;
  },

  /**
   * 获取我所在的团队
   */
  async getMyTeam(feishuUserId: string): Promise<Team | null> {
    const response = await axios.get(`${API_BASE}/api/team/my-team?feishu_user_id=${feishuUserId}`);
    return response.data;
  },

  /**
   * 获取团队成员列表
   */
  async getMembers(teamId: number, feishuUserId: string): Promise<TeamMember[]> {
    const response = await axios.get(`${API_BASE}/api/team/${teamId}/members?feishu_user_id=${feishuUserId}`);
    return response.data;
  },

  /**
   * 邀请成员
   * @param inviteeFeishuId 可选，为空时生成通用邀请码
   */
  async inviteMember(teamId: number, feishuUserId: string, inviteeFeishuId?: string): Promise<InviteResult> {
    const response = await axios.post(`${API_BASE}/api/team/${teamId}/invite?feishu_user_id=${feishuUserId}`, {
      invitee_feishu_id: inviteeFeishuId || null
    });
    return response.data;
  },

  /**
   * 接受邀请
   */
  async acceptInvite(feishuUserId: string, inviteCode: string): Promise<{ success: boolean; team_name: string }> {
    const response = await axios.post(`${API_BASE}/api/team/accept-invite`, {
      feishu_user_id: feishuUserId,
      invite_code: inviteCode
    });
    return response.data;
  },

  /**
   * 移除成员
   */
  async removeMember(teamId: number, memberId: number, feishuUserId: string): Promise<void> {
    await axios.delete(`${API_BASE}/api/team/${teamId}/members/${memberId}?feishu_user_id=${feishuUserId}`);
  },

  /**
   * 退出团队
   */
  async leaveTeam(teamId: number, feishuUserId: string): Promise<void> {
    await axios.post(`${API_BASE}/api/team/${teamId}/leave?feishu_user_id=${feishuUserId}`);
  },

  /**
   * 解散团队（仅团队所有者）
   */
  async dissolveTeam(teamId: number, feishuUserId: string): Promise<void> {
    await axios.delete(`${API_BASE}/api/team/${teamId}/dissolve?feishu_user_id=${feishuUserId}`);
  },

  /**
   * 更新成员角色
   */
  async updateMemberRole(teamId: number, memberId: number, feishuUserId: string, role: 'admin' | 'member'): Promise<void> {
    await axios.put(`${API_BASE}/api/team/${teamId}/members/${memberId}/role?feishu_user_id=${feishuUserId}`, {
      role
    });
  },

  /**
   * 共享模版到团队
   */
  async shareTemplate(teamId: number, feishuUserId: string, templateId: number, canEdit: boolean = false): Promise<void> {
    await axios.post(`${API_BASE}/api/team/${teamId}/templates/share?feishu_user_id=${feishuUserId}`, {
      template_id: templateId,
      can_edit: canEdit
    });
  },

  /**
   * 获取团队共享模版
   */
  async getTeamTemplates(teamId: number, feishuUserId: string): Promise<TeamTemplate[]> {
    const response = await axios.get(`${API_BASE}/api/team/${teamId}/templates?feishu_user_id=${feishuUserId}`);
    return response.data;
  },

  /**
   * 取消共享模版
   */
  async unshareTemplate(teamId: number, teamTemplateId: number, feishuUserId: string): Promise<void> {
    await axios.delete(`${API_BASE}/api/team/${teamId}/templates/${teamTemplateId}?feishu_user_id=${feishuUserId}`);
  }
};
