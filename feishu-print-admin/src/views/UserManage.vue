<template>
  <div class="user-manage">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <div class="search-input-wrapper">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        <input v-model="searchQuery" type="text" placeholder="搜索用户..." @keyup.enter="handleSearch" />
      </div>
      <select v-model="filterPlan" class="filter-select">
        <option value="">全部会员</option>
        <option value="free">免费版</option>
        <option value="pro">专业版</option>
        <option value="team">团队版</option>
      </select>
      <button @click="handleSearch" class="btn-search">搜索</button>
    </div>

    <!-- 用户表格 -->
    <div class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>用户</th>
            <th>飞书ID</th>
            <th>会员等级</th>
            <th>到期时间</th>
            <th>注册时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>
              <div class="user-cell">
                <div class="user-avatar">{{ user.nickname?.charAt(0) || 'U' }}</div>
                <span>{{ user.nickname || '未命名' }}</span>
              </div>
            </td>
            <td class="text-mono">{{ user.feishu_user_id }}</td>
            <td>
              <span :class="['plan-badge', user.plan_type]">{{ getPlanText(user.plan_type) }}</span>
            </td>
            <td>{{ user.expires_at ? formatDate(user.expires_at) : '永久' }}</td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td>
              <div class="action-btns">
                <button @click="openUpgradeDialog(user)" class="btn-action">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m2 4 3 12h14l3-12-6 7-4-7-4 7-6-7zm3 16h14"/></svg>
                </button>
                <button @click="viewUser(user)" class="btn-action">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="users.length === 0" class="empty-state">
        <p>暂无用户数据</p>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination">
      <span class="page-info">共 {{ total }} 条</span>
      <div class="page-btns">
        <button @click="changePage(page - 1)" :disabled="page <= 1" class="page-btn">上一页</button>
        <span class="page-current">{{ page }}</span>
        <button @click="changePage(page + 1)" :disabled="page >= totalPages" class="page-btn">下一页</button>
      </div>
    </div>

    <!-- 升级弹窗 -->
    <div v-if="showUpgradeDialog" class="dialog-overlay" @click.self="showUpgradeDialog = false">
      <div class="dialog">
        <div class="dialog-header">
          <h3>修改会员等级</h3>
          <button @click="showUpgradeDialog = false" class="btn-close">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
        </div>
        <div class="dialog-body">
          <p class="dialog-info">用户: {{ selectedUser?.nickname || selectedUser?.feishu_user_id }}</p>
          <div class="form-group">
            <label>会员等级</label>
            <select v-model="upgradePlan" class="form-select">
              <option value="free">免费版</option>
              <option value="pro">专业版</option>
              <option value="team">团队版</option>
            </select>
          </div>
          <div class="form-group">
            <label>有效期（天）</label>
            <input v-model.number="upgradeDays" type="number" class="form-input" placeholder="30" />
          </div>
        </div>
        <div class="dialog-footer">
          <button @click="showUpgradeDialog = false" class="btn-cancel">取消</button>
          <button @click="handleUpgrade" class="btn-confirm" :disabled="isUpgrading">
            {{ isUpgrading ? '处理中...' : '确认' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { adminApi } from '@/api/admin';

const users = ref<any[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = 20;
const searchQuery = ref('');
const filterPlan = ref('');

const showUpgradeDialog = ref(false);
const selectedUser = ref<any>(null);
const upgradePlan = ref('pro');
const upgradeDays = ref(30);
const isUpgrading = ref(false);

const totalPages = computed(() => Math.ceil(total.value / pageSize));

const getPlanText = (plan: string) => {
  const map: Record<string, string> = { free: '免费版', pro: '专业版', team: '团队版' };
  return map[plan] || plan;
};

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('zh-CN');
};

const loadUsers = async () => {
  try {
    const result = await adminApi.getUsers({
      page: page.value,
      pageSize,
      search: searchQuery.value,
      planType: filterPlan.value
    });
    users.value = result.items;
    total.value = result.total;
  } catch (e) {
    console.error('加载用户失败:', e);
  }
};

const handleSearch = () => {
  page.value = 1;
  loadUsers();
};

const changePage = (p: number) => {
  page.value = p;
  loadUsers();
};

const openUpgradeDialog = (user: any) => {
  selectedUser.value = user;
  upgradePlan.value = user.plan_type || 'pro';
  upgradeDays.value = 30;
  showUpgradeDialog.value = true;
};

const viewUser = (user: any) => {
  alert(`用户详情: ${JSON.stringify(user, null, 2)}`);
};

const handleUpgrade = async () => {
  if (!selectedUser.value) return;
  isUpgrading.value = true;
  try {
    await adminApi.updateUserMembership(selectedUser.value.id, {
      plan_type: upgradePlan.value,
      duration_days: upgradeDays.value
    });
    showUpgradeDialog.value = false;
    loadUsers();
  } catch (e) {
    console.error('升级失败:', e);
  } finally {
    isUpgrading.value = false;
  }
};

onMounted(() => {
  loadUsers();
});
</script>

<style scoped>
.user-manage {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.search-bar {
  display: flex;
  gap: 1rem;
  background: white;
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.search-input-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.search-input-wrapper svg {
  position: absolute;
  left: 1rem;
  color: #9ca3af;
}

.search-input-wrapper input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.875rem;
  outline: none;
}

.search-input-wrapper input:focus {
  border-color: #0f172a;
}

.filter-select {
  padding: 0.75rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.875rem;
  background: white;
  cursor: pointer;
  min-width: 120px;
}

.btn-search {
  padding: 0.75rem 1.5rem;
  background: #0f172a;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
}

.btn-search:hover {
  background: #1e293b;
}

.table-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 1rem;
  background: #f8fafc;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  border-bottom: 1px solid #e5e7eb;
}

.data-table td {
  padding: 1rem;
  font-size: 0.875rem;
  color: #374151;
  border-bottom: 1px solid #f1f5f9;
}

.data-table tr:hover {
  background: #f8fafc;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #0f172a, #334155);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.75rem;
}

.text-mono {
  font-family: monospace;
  font-size: 0.75rem;
  color: #64748b;
}

.plan-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.plan-badge.free {
  background: #f1f5f9;
  color: #64748b;
}

.plan-badge.pro {
  background: #dbeafe;
  color: #2563eb;
}

.plan-badge.team {
  background: #fef3c7;
  color: #d97706;
}

.action-btns {
  display: flex;
  gap: 0.5rem;
}

.btn-action {
  width: 32px;
  height: 32px;
  background: #f1f5f9;
  border: none;
  border-radius: 6px;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-action:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.empty-state {
  padding: 3rem;
  text-align: center;
  color: #94a3b8;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.page-info {
  font-size: 0.875rem;
  color: #64748b;
}

.page-btns {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-btn {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-btn:hover:not(:disabled) {
  background: #f8fafc;
}

.page-current {
  padding: 0.5rem 1rem;
  background: #0f172a;
  color: white;
  border-radius: 6px;
  font-weight: 500;
}

.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 400px;
  overflow: hidden;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem;
  border-bottom: 1px solid #e5e7eb;
}

.dialog-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #0f172a;
}

.btn-close {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.25rem;
}

.dialog-body {
  padding: 1.25rem;
}

.dialog-info {
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-select,
.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.875rem;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.25rem;
  border-top: 1px solid #e5e7eb;
}

.btn-cancel {
  padding: 0.625rem 1.25rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
}

.btn-confirm {
  padding: 0.625rem 1.25rem;
  background: #0f172a;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
}

.btn-confirm:disabled {
  opacity: 0.7;
}
</style>
