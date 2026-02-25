<template>
  <div class="promo-manage">
    <!-- 操作栏 -->
    <div class="action-bar">
      <button @click="showCreateDialog = true" class="btn-create">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
        创建邀请码
      </button>
    </div>

    <!-- 邀请码列表 -->
    <div class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>邀请码</th>
            <th>会员类型</th>
            <th>有效期</th>
            <th>使用次数</th>
            <th>状态</th>
            <th>过期时间</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="promo in promos" :key="promo.id">
            <td class="text-mono promo-code">{{ promo.code }}</td>
            <td>
              <span :class="['plan-badge', promo.plan_type]">{{ getPlanText(promo.plan_type) }}</span>
            </td>
            <td>{{ promo.duration_days }} 天</td>
            <td>
              <span :class="{ 'text-warning': isPromoUsageExceeded(promo) }">
                {{ promo.used_count }} / {{ formatMaxUses(promo.max_uses) }}
              </span>
            </td>
            <td>
              <span :class="['status-badge', promo.is_active ? 'active' : 'inactive']">
                {{ promo.is_active ? '启用' : '禁用' }}
              </span>
            </td>
            <td>{{ promo.expires_at ? formatDate(promo.expires_at) : '永久有效' }}</td>
            <td>{{ formatDate(promo.created_at) }}</td>
            <td>
              <div class="action-btns">
                <button @click="togglePromo(promo)" class="btn-action" :title="promo.is_active ? '禁用' : '启用'">
                  <svg v-if="promo.is_active" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                </button>
                <button @click="deletePromo(promo)" class="btn-action delete">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="promos.length === 0" class="empty-state">
        <p>暂无邀请码</p>
      </div>
    </div>

    <!-- 创建邀请码弹窗 -->
    <div v-if="showCreateDialog" class="dialog-overlay" @click.self="showCreateDialog = false">
      <div class="dialog">
        <div class="dialog-header">
          <h3>创建邀请码</h3>
          <button @click="showCreateDialog = false" class="btn-close">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>会员类型</label>
            <select v-model="newPromo.plan_type" class="form-select">
              <option value="free">免费版</option>
              <option value="pro">专业版</option>
              <option value="team">团队版</option>
            </select>
          </div>
          <div class="form-group">
            <label>有效期（天）</label>
            <input v-model.number="newPromo.duration_days" type="number" class="form-input" placeholder="30" min="1" />
          </div>
          <div class="form-group">
            <label>最大使用次数</label>
            <input v-model.number="newPromo.max_uses" type="number" class="form-input" placeholder="1" min="1" />
          </div>
          <div class="form-group">
            <label>邀请码有效期（天，留空表示永久）</label>
            <input v-model.number="newPromo.expires_days" type="number" class="form-input" placeholder="留空表示永久有效" min="1" />
          </div>
        </div>
        <div class="dialog-footer">
          <button @click="showCreateDialog = false" class="btn-cancel">取消</button>
          <button @click="handleCreate" class="btn-confirm" :disabled="isCreating">
            {{ isCreating ? '创建中...' : '创建' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { adminApi } from '@/api/admin';
import { ElMessage } from 'element-plus';

const promos = ref<any[]>([]);
const showCreateDialog = ref(false);
const isCreating = ref(false);

const newPromo = ref({
  plan_type: 'pro',
  duration_days: 30,
  max_uses: 1,
  expires_days: null as number | null
});

const getPlanText = (plan: string) => {
  const map: Record<string, string> = { free: '免费版', pro: '专业版', team: '团队版' };
  return map[plan] || plan;
};

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN');
};

const formatMaxUses = (maxUses: number) => {
  // 约定：-1 表示不限次数
  if (maxUses === -1) return '不限';
  return String(maxUses);
};

const isPromoUsageExceeded = (promo: any) => {
  // max_uses = -1 表示不限次数，不应触发“用完”提示
  if (promo?.max_uses === -1) return false;
  if (typeof promo?.max_uses !== 'number') return false;
  return promo.used_count >= promo.max_uses;
};

const loadPromos = async () => {
  try {
    const result = await adminApi.getPromos();
    promos.value = result.items || [];
  } catch (e) {
    console.error('加载邀请码失败:', e);
    ElMessage.error('加载邀请码失败');
  }
};

const handleCreate = async () => {
  if (!newPromo.value.plan_type || !newPromo.value.duration_days || !newPromo.value.max_uses) {
    ElMessage.warning('请填写完整信息');
    return;
  }

  isCreating.value = true;
  try {
    const result = await adminApi.createPromo({
      plan_type: newPromo.value.plan_type,
      duration_days: newPromo.value.duration_days,
      max_uses: newPromo.value.max_uses,
      expires_days: newPromo.value.expires_days || undefined
    });
    
    if (result.success) {
      ElMessage.success('邀请码创建成功');
      showCreateDialog.value = false;
      newPromo.value = {
        plan_type: 'pro',
        duration_days: 30,
        max_uses: 1,
        expires_days: null
      };
      loadPromos();
    } else {
      ElMessage.error(result.message || '创建失败');
    }
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '创建失败');
  } finally {
    isCreating.value = false;
  }
};

const togglePromo = async (promo: any) => {
  try {
    await adminApi.togglePromo(promo.id);
    promo.is_active = promo.is_active ? 0 : 1;
    ElMessage.success('操作成功');
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败');
  }
};

const deletePromo = async (promo: any) => {
  if (!confirm(`确定要删除邀请码 ${promo.code} 吗？`)) return;
  
  try {
    await adminApi.deletePromo(promo.id);
    ElMessage.success('删除成功');
    loadPromos();
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '删除失败');
  }
};

onMounted(() => {
  loadPromos();
});
</script>

<style scoped>
.promo-manage {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.action-bar {
  display: flex;
  justify-content: flex-end;
}

.btn-create {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #0f172a;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
}

.btn-create:hover {
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

.text-mono {
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
}

.promo-code {
  font-weight: 600;
  color: #0f172a;
}

.plan-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.plan-badge.free {
  background: #f1f5f9;
  color: #64748b;
}

.plan-badge.pro {
  background: #dbeafe;
  color: #1e40af;
}

.plan-badge.team {
  background: #fef3c7;
  color: #92400e;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.active {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.inactive {
  background: #fee2e2;
  color: #991b1b;
}

.text-warning {
  color: #f59e0b;
}

.action-btns {
  display: flex;
  gap: 0.5rem;
}

.btn-action {
  padding: 0.375rem;
  background: #f1f5f9;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-action:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.btn-action.delete:hover {
  background: #fee2e2;
  color: #dc2626;
}

.empty-state {
  padding: 3rem;
  text-align: center;
  color: #9ca3af;
}

/* 弹窗样式 */
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
  max-width: 500px;
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

.form-input,
.form-select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.875rem;
  outline: none;
}

.form-input:focus,
.form-select:focus {
  border-color: #0f172a;
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

