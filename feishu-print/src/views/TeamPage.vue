<template>
  <div class="team-page">
    <!-- 返回按钮 -->
    <div class="back-home">
      <button @click="$router.push('/')" class="btn-back">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        返回
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 无团队状态 -->
    <div v-else-if="!team" class="no-team">
      <div class="no-team-content">
        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="icon-users"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        <h2>您还没有团队</h2>
        <p>创建团队开始协作，或输入邀请码加入现有团队</p>
        
        <div class="actions">
          <button @click="showCreateDialog = true" class="btn-primary">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14"/><path d="M5 12h14"/></svg>
            创建团队
          </button>
          <button @click="showJoinDialog = true" class="btn-outline">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" x2="3" y1="12" y2="12"/></svg>
            加入团队
          </button>
        </div>
      </div>
    </div>

    <!-- 团队详情 -->
    <div v-else class="team-content">
      <!-- 团队信息卡片 -->
      <div class="team-info-card">
        <div class="team-header">
          <div class="team-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          </div>
          <div class="team-details">
            <h1 class="team-name">{{ team.name }}</h1>
            <p class="team-desc">{{ team.description || '暂无描述' }}</p>
          </div>
        </div>
        <div class="team-stats">
          <div class="stat-item">
            <span class="stat-value">{{ team.member_count }}</span>
            <span class="stat-label">/ {{ team.max_members }} 成员</span>
          </div>
        </div>
      </div>

      <!-- 成员管理 -->
      <div class="section">
        <div class="section-header">
          <h2 class="section-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" x2="19" y1="8" y2="14"/><line x1="22" x2="16" y1="11" y2="11"/></svg>
            团队成员
          </h2>
          <button v-if="isAdmin" @click="showInviteDialog = true" class="btn-sm btn-primary">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" x2="19" y1="8" y2="14"/><line x1="22" x2="16" y1="11" y2="11"/></svg>
            邀请成员
          </button>
        </div>
        
        <div class="member-list">
          <div v-for="member in members" :key="member.id" class="member-item">
            <div class="member-avatar">
              {{ (member.nickname || member.feishu_user_id).charAt(0).toUpperCase() }}
            </div>
            <div class="member-info">
              <span class="member-name">{{ member.nickname || member.feishu_user_id }}</span>
              <span class="member-role" :class="member.role">
                {{ getRoleName(member.role) }}
              </span>
            </div>
            <div class="member-actions" v-if="isOwner && member.role !== 'owner'">
              <button @click="toggleRole(member)" class="btn-icon" title="更改角色">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
              </button>
              <button @click="removeMember(member)" class="btn-icon btn-danger" title="移除成员">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="17" x2="22" y1="11" y2="11"/></svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 共享模版 -->
      <div class="section">
        <div class="section-header">
          <h2 class="section-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
            共享模版
          </h2>
          <button @click="showShareDialog = true" class="btn-sm btn-outline">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/><polyline points="16 6 12 2 8 6"/><line x1="12" x2="12" y1="2" y2="15"/></svg>
            共享模版
          </button>
        </div>
        
        <div v-if="teamTemplates.length === 0" class="empty-state">
          <p>暂无共享模版</p>
        </div>
        <div v-else class="template-list">
          <div v-for="tt in teamTemplates" :key="tt.id" class="template-item">
            <div class="template-info">
              <span class="template-name">{{ tt.template_name }}</span>
              <span class="template-meta">
                由 {{ tt.shared_by_nickname || '未知' }} 共享
                <span v-if="tt.can_edit" class="badge">可编辑</span>
              </span>
            </div>
            <div class="template-actions" v-if="isAdmin">
              <button @click="unshareTemplate(tt)" class="btn-icon btn-danger" title="取消共享">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 退出/解散团队按钮 -->
      <div class="leave-section">
        <button v-if="isOwner" @click="handleDissolveTeam" class="btn-danger-outline">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
          解散团队
        </button>
        <button v-else @click="handleLeaveTeam" class="btn-danger-outline">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>
          退出团队
        </button>
      </div>
    </div>

    <!-- 创建团队弹窗 -->
    <div v-if="showCreateDialog" class="dialog-overlay" @click.self="showCreateDialog = false">
      <div class="dialog">
        <h3 class="dialog-title">创建团队</h3>
        <div class="dialog-body">
          <div class="form-group">
            <label>团队名称</label>
            <input v-model="newTeamName" type="text" placeholder="请输入团队名称" maxlength="50" />
          </div>
          <div class="form-group">
            <label>团队描述 (可选)</label>
            <textarea v-model="newTeamDesc" placeholder="请输入团队描述" maxlength="200"></textarea>
          </div>
        </div>
        <div class="dialog-footer">
          <button @click="showCreateDialog = false" class="btn-outline">取消</button>
          <button @click="createTeam" class="btn-primary" :disabled="!newTeamName.trim()">创建</button>
        </div>
      </div>
    </div>

    <!-- 加入团队弹窗 -->
    <div v-if="showJoinDialog" class="dialog-overlay" @click.self="showJoinDialog = false">
      <div class="dialog">
        <h3 class="dialog-title">加入团队</h3>
        <div class="dialog-body">
          <div class="form-group">
            <label>邀请码</label>
            <input v-model="inviteCode" type="text" placeholder="请输入邀请码" />
          </div>
        </div>
        <div class="dialog-footer">
          <button @click="showJoinDialog = false" class="btn-outline">取消</button>
          <button @click="joinTeam" class="btn-primary" :disabled="!inviteCode.trim()">加入</button>
        </div>
      </div>
    </div>

    <!-- 邀请成员弹窗 -->
    <div v-if="showInviteDialog" class="dialog-overlay" @click.self="showInviteDialog = false">
      <div class="dialog">
        <h3 class="dialog-title">邀请成员</h3>
        <div class="dialog-body">
          <div class="form-group">
            <label>被邀请人飞书用户ID（可选）</label>
            <input v-model="inviteeId" type="text" placeholder="留空则生成通用邀请码，任何人都可使用" />
            <p class="form-hint">如果不填写，将生成通用邀请码，任何知道邀请码的用户都可以加入团队</p>
          </div>
          <div v-if="generatedInviteCode" class="invite-result">
            <p>邀请码已生成：</p>
            <div class="invite-code">{{ generatedInviteCode }}</div>
            <p class="invite-tip">请将此邀请码发送给被邀请人，有效期7天</p>
          </div>
        </div>
        <div class="dialog-footer">
          <button @click="closeInviteDialog" class="btn-outline">关闭</button>
          <button v-if="!generatedInviteCode" @click="generateInvite" class="btn-primary">生成邀请码</button>
        </div>
      </div>
    </div>

    <!-- 共享模版弹窗 -->
    <div v-if="showShareDialog" class="dialog-overlay" @click.self="showShareDialog = false">
      <div class="dialog">
        <h3 class="dialog-title">共享模版到团队</h3>
        <div class="dialog-body">
          <div class="form-group">
            <label>选择模版</label>
            <select v-model="selectedTemplateId">
              <option value="">请选择模版</option>
              <option v-for="t in availableTemplates" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
          </div>
          <div class="form-group checkbox-group">
            <label>
              <input type="checkbox" v-model="shareCanEdit" />
              允许团队成员编辑
            </label>
          </div>
        </div>
        <div class="dialog-footer">
          <button @click="showShareDialog = false" class="btn-outline">取消</button>
          <button @click="shareTemplate" class="btn-primary" :disabled="!selectedTemplateId">共享</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { bitable } from '@lark-base-open/js-sdk';
import { teamApi, type Team, type TeamMember, type TeamTemplate } from '@/api/team';
import { templateApi } from '@/api/templates';
import { useUser } from '@/composables/useUser';

const router = useRouter();
const { initUser, userStatus } = useUser();

// 状态
const isLoading = ref(true);
const feishuUserId = ref('');
const team = ref<Team | null>(null);
const members = ref<TeamMember[]>([]);
const teamTemplates = ref<TeamTemplate[]>([]);
const availableTemplates = ref<{ id: number; name: string }[]>([]);

// 弹窗状态
const showCreateDialog = ref(false);
const showJoinDialog = ref(false);
const showInviteDialog = ref(false);
const showShareDialog = ref(false);

// 表单数据
const newTeamName = ref('');
const newTeamDesc = ref('');
const inviteCode = ref('');
const inviteeId = ref('');
const generatedInviteCode = ref('');
const selectedTemplateId = ref<number | ''>('');
const shareCanEdit = ref(false);

// 计算属性
const currentMember = computed(() => {
  return members.value.find(m => m.feishu_user_id === feishuUserId.value);
});

const isOwner = computed(() => {
  return currentMember.value?.role === 'owner';
});

const isAdmin = computed(() => {
  return currentMember.value?.role === 'owner' || currentMember.value?.role === 'admin';
});

// 方法
const getRoleName = (role: string) => {
  switch (role) {
    case 'owner': return '所有者';
    case 'admin': return '管理员';
    default: return '成员';
  }
};

const loadTeamData = async () => {
  isLoading.value = true;
  try {
    feishuUserId.value = await bitable.bridge.getUserId();
    
    // 初始化用户
    await initUser();
    
    team.value = await teamApi.getMyTeam(feishuUserId.value);
    
    if (team.value) {
      members.value = await teamApi.getMembers(team.value.id, feishuUserId.value);
      teamTemplates.value = await teamApi.getTeamTemplates(team.value.id, feishuUserId.value);
    }
    
    // 加载可用模版
    const templates = await templateApi.getAll();
    availableTemplates.value = templates.map(t => ({ id: t.id, name: t.name }));
  } catch (error) {
    console.error('加载团队数据失败:', error);
  } finally {
    isLoading.value = false;
  }
};

const createTeam = async () => {
  if (!newTeamName.value.trim()) return;
  
  try {
    team.value = await teamApi.createTeam(feishuUserId.value, newTeamName.value, newTeamDesc.value);
    showCreateDialog.value = false;
    ElMessage.success('团队创建成功');
    await loadTeamData();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '创建失败');
  }
};

const joinTeam = async () => {
  if (!inviteCode.value.trim()) return;
  
  try {
    const result = await teamApi.acceptInvite(feishuUserId.value, inviteCode.value);
    showJoinDialog.value = false;
    ElMessage.success(`成功加入团队：${result.team_name}`);
    await loadTeamData();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加入失败');
  }
};

const generateInvite = async () => {
  if (!team.value) return;
  
  try {
    // 如果输入了被邀请人ID，则生成指定用户的邀请码；否则生成通用邀请码
    const inviteeIdValue = inviteeId.value.trim() || undefined;
    const result = await teamApi.inviteMember(team.value.id, feishuUserId.value, inviteeIdValue);
    generatedInviteCode.value = result.invite_code;
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '生成邀请码失败');
  }
};

const closeInviteDialog = () => {
  showInviteDialog.value = false;
  inviteeId.value = '';
  generatedInviteCode.value = '';
};

const toggleRole = async (member: TeamMember) => {
  if (!team.value) return;
  
  const newRole = member.role === 'admin' ? 'member' : 'admin';
  const roleName = newRole === 'admin' ? '管理员' : '普通成员';
  
  try {
    await ElMessageBox.confirm(`确定将 ${member.nickname || member.feishu_user_id} 设为${roleName}？`, '更改角色');
    await teamApi.updateMemberRole(team.value.id, member.id, feishuUserId.value, newRole);
    ElMessage.success('角色已更新');
    await loadTeamData();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '更新失败');
    }
  }
};

const removeMember = async (member: TeamMember) => {
  if (!team.value) return;
  
  try {
    await ElMessageBox.confirm(`确定移除成员 ${member.nickname || member.feishu_user_id}？`, '移除成员', { type: 'warning' });
    await teamApi.removeMember(team.value.id, member.id, feishuUserId.value);
    ElMessage.success('成员已移除');
    await loadTeamData();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '移除失败');
    }
  }
};

const handleLeaveTeam = async () => {
  if (!team.value) return;
  
  try {
    await ElMessageBox.confirm('确定退出当前团队？', '退出团队', { type: 'warning' });
    await teamApi.leaveTeam(team.value.id, feishuUserId.value);
    ElMessage.success('已退出团队');
    team.value = null;
    members.value = [];
    teamTemplates.value = [];
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '退出失败');
    }
  }
};

const handleDissolveTeam = async () => {
  if (!team.value) return;
  
  try {
    await ElMessageBox.confirm(
      '确定要解散团队吗？此操作将删除团队及其所有数据，且无法恢复。',
      '解散团队',
      { 
        type: 'warning',
        confirmButtonText: '确定解散',
        cancelButtonText: '取消',
        confirmButtonClass: 'el-button--danger'
      }
    );
    await teamApi.dissolveTeam(team.value.id, feishuUserId.value);
    ElMessage.success('团队已解散');
    team.value = null;
    members.value = [];
    teamTemplates.value = [];
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '解散失败');
    }
  }
};

const shareTemplate = async () => {
  if (!team.value || !selectedTemplateId.value) return;
  
  try {
    await teamApi.shareTemplate(team.value.id, feishuUserId.value, selectedTemplateId.value as number, shareCanEdit.value);
    showShareDialog.value = false;
    selectedTemplateId.value = '';
    shareCanEdit.value = false;
    ElMessage.success('模版已共享');
    await loadTeamData();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '共享失败');
  }
};

const unshareTemplate = async (tt: TeamTemplate) => {
  if (!team.value) return;
  
  try {
    await ElMessageBox.confirm(`确定取消共享模版 ${tt.template_name}？`, '取消共享');
    await teamApi.unshareTemplate(team.value.id, tt.id, feishuUserId.value);
    ElMessage.success('已取消共享');
    await loadTeamData();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '操作失败');
    }
  }
};

onMounted(() => {
  loadTeamData();
});
</script>

<style scoped>
.team-page {
  min-height: 100vh;
  background: #f8fafc;
  padding: 2rem;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  position: relative;
}

.back-home {
  position: absolute;
  top: 1.5rem;
  left: 1.5rem;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: white;
  border: 1px solid #e2e8f0;
  color: #475569;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
  color: #64748b;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: #0f172a;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.upgrade-prompt {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 70vh;
}

.upgrade-content {
  text-align: center;
  max-width: 400px;
  background: white;
  padding: 3rem;
  border-radius: 4px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.upgrade-content .icon-lock {
  color: #94a3b8;
  margin-bottom: 1.5rem;
}

.upgrade-content h2 {
  font-size: 1.5rem;
  color: #0f172a;
  margin-bottom: 0.5rem;
}

.upgrade-content p {
  color: #64748b;
  margin-bottom: 1.5rem;
}

.upgrade-features {
  text-align: left;
  margin-bottom: 2rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 4px;
}

.upgrade-features .feature {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #334155;
  font-size: 0.875rem;
  padding: 0.5rem 0;
}

.upgrade-features .feature svg {
  color: #059669;
}

.btn-upgrade {
  width: 100%;
  justify-content: center;
}

.no-team {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 70vh;
}

.no-team-content {
  text-align: center;
  max-width: 400px;
}

.no-team-content .icon-users {
  color: #cbd5e1;
  margin-bottom: 1.5rem;
}

.no-team-content h2 {
  font-size: 1.5rem;
  color: #0f172a;
  margin-bottom: 0.5rem;
}

.no-team-content p {
  color: #64748b;
  margin-bottom: 2rem;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.team-content {
  max-width: 800px;
  margin: 3rem auto 0;
}

.team-info-card {
  background: white;
  border-radius: 4px;
  padding: 2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.team-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.team-icon {
  width: 64px;
  height: 64px;
  background: #f1f5f9;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #475569;
}

.team-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.25rem;
}

.team-desc {
  color: #64748b;
  margin: 0;
}

.team-stats {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.stat-item {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #0f172a;
}

.stat-label {
  color: #64748b;
}

.section {
  background: white;
  border-radius: 4px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.member-list, .template-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.member-item, .template-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 4px;
}

.member-avatar {
  width: 40px;
  height: 40px;
  background: #0f172a;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.member-info, .template-info {
  flex: 1;
}

.member-name, .template-name {
  font-weight: 500;
  color: #0f172a;
}

.member-role {
  display: inline-block;
  margin-left: 0.5rem;
  padding: 0.125rem 0.5rem;
  background: #e2e8f0;
  color: #475569;
  border-radius: 4px;
  font-size: 0.75rem;
}

.member-role.owner {
  background: #fef3c7;
  color: #92400e;
}

.member-role.admin {
  background: #dbeafe;
  color: #1e40af;
}

.template-meta {
  display: block;
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.25rem;
}

.badge {
  display: inline-block;
  margin-left: 0.5rem;
  padding: 0.125rem 0.375rem;
  background: #dcfce7;
  color: #166534;
  border-radius: 4px;
  font-size: 0.625rem;
}

.member-actions, .template-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: #64748b;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.btn-icon.btn-danger:hover {
  background: #fee2e2;
  color: #dc2626;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #94a3b8;
}

.leave-section {
  text-align: center;
  margin-top: 2rem;
}

/* 按钮样式 */
.btn-primary, .btn-outline, .btn-sm, .btn-danger-outline {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  border-radius: 4px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #0f172a;
  color: white;
  border: none;
}

.btn-primary:hover {
  background: #1e293b;
}

.btn-primary:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.btn-outline {
  background: white;
  color: #0f172a;
  border: 1px solid #e2e8f0;
}

.btn-outline:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
}

.btn-danger-outline {
  background: white;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.btn-danger-outline:hover {
  background: #fee2e2;
}

/* 弹窗样式 */
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: white;
  border-radius: 4px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
}

.dialog-title {
  padding: 1.5rem 1.5rem 0;
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #0f172a;
}

.dialog-body {
  padding: 1.5rem;
}

.dialog-footer {
  padding: 0 1.5rem 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-group input, .form-group textarea, .form-group select {
  width: 100%;
  padding: 0.625rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.form-group input:focus, .form-group textarea:focus, .form-group select:focus {
  outline: none;
  border-color: #0f172a;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-group input[type="checkbox"] {
  width: auto;
}

.invite-result {
  margin-top: 1rem;
  padding: 1rem;
  background: #f0fdf4;
  border-radius: 4px;
}

.invite-code {
  font-family: monospace;
  font-size: 1rem;
  background: white;
  padding: 0.5rem;
  border-radius: 4px;
  margin: 0.5rem 0;
  word-break: break-all;
}

.invite-tip {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0;
}
</style>
