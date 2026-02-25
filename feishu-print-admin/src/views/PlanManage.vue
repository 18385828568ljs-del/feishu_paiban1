<template>
  <div class="plan-manage">
    <div class="header">
      <div>
        <h2>会员价格管理</h2>
        <p class="subtitle">管理专业版与团队版的价格与时长（单位：元 / 分）</p>
      </div>
      <button class="btn-refresh" @click="loadPlans" :disabled="loading">
        刷新
      </button>
    </div>

    <div class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>计划ID</th>
            <th>名称</th>
            <th>当前价格（元）</th>
            <th>时长（月）</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="plan in plans" :key="plan.id">
            <td class="text-mono">{{ plan.id }}</td>
            <td>
              <input v-model="plan.editName" class="input" />
            </td>
            <td>
              <input
                v-model.number="plan.editPriceYuan"
                type="number"
                min="0"
                step="0.01"
                class="input"
              />
            </td>
            <td>
              <span class="static-text">{{ plan.editDurationMonths }}</span>
            </td>
            <td>
              <button
                class="btn-save"
                @click="savePlan(plan)"
                :disabled="savingId === plan.id"
              >
                {{ savingId === plan.id ? '保存中...' : '保存' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="!loading && plans.length === 0" class="empty-state">
        暂无会员计划数据
      </div>

      <div v-if="loading" class="loading-state">
        正在加载会员计划...
      </div>
    </div>

    <p class="tip">
      提示：当前实现将价格配置保存在服务内存中，<strong>服务重启后会恢复为代码中的默认价格</strong>。
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { adminApi } from '@/api/admin';

interface PlanRow {
  id: string;
  name: string;
  price: number;
  original_price?: number | null;
  duration_days: number;
  editName: string;
  editPriceYuan: number;
  editOriginalPriceYuan: number;
  editDurationDays: number;
  editDurationMonths: number;
}

const plans = ref<PlanRow[]>([]);
const loading = ref(false);
const savingId = ref<string | null>(null);

const toYuan = (cents?: number | null): number =>
  cents ? Math.round(cents) / 100 : 0;

const toCents = (yuan: number): number =>
  Math.round((yuan || 0) * 100);

const loadPlans = async () => {
  loading.value = true;
  try {
    const data = await adminApi.getPlans();
    plans.value = (data || []).map((p: any) => ({
      id: p.id,
      name: p.name,
      price: p.price,
      original_price: p.original_price,
      duration_days: p.duration_days,
      editName: p.name,
      editPriceYuan: toYuan(p.price),
      editOriginalPriceYuan: toYuan(p.original_price),
      editDurationDays: p.duration_days,
      // 默认按 30 天为一个月计算，保留一位小数方便显示
      editDurationMonths: parseFloat((p.duration_days / 30).toFixed(1))
    }));
  } catch (e) {
    console.error('加载会员计划失败:', e);
    alert('加载会员计划失败，请检查后端服务');
  } finally {
    loading.value = false;
  }
};

const savePlan = async (plan: PlanRow) => {
  savingId.value = plan.id;
  try {
    // 仅更新名称和价格，时长保持原值
    await adminApi.updatePlan(plan.id, {
      name: plan.editName,
      price: toCents(plan.editPriceYuan),
      duration_days: plan.duration_days
    });
    
    plan.name = plan.editName;
    plan.price = toCents(plan.editPriceYuan);
    // duration_days 不变
    
    alert('保存成功');
  } catch (e) {
    console.error('保存会员计划失败:', e);
    alert('保存失败，请稍后重试');
  } finally {
    savingId.value = null;
  }
};

onMounted(() => {
  loadPlans();
});
</script>

<style scoped>
.plan-manage {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #0f172a;
}

.subtitle {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
  color: #64748b;
}

.btn-refresh {
  padding: 0.5rem 1rem;
  background: #0f172a;
  color: #fff;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.table-card {
  background: #fff;
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
  padding: 0.75rem 1rem;
  background: #f8fafc;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  border-bottom: 1px solid #e5e7eb;
}

.data-table td {
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  color: #374151;
  border-bottom: 1px solid #f1f5f9;
}

.text-mono {
  font-family: monospace;
  font-size: 0.8rem;
  color: #6b7280;
}

.input {
  width: 100%;
  padding: 0.4rem 0.5rem;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  font-size: 0.875rem;
}

.btn-save {
  padding: 0.4rem 0.9rem;
  border-radius: 6px;
  border: none;
  background: #0f172a;
  color: #fff;
  font-size: 0.8rem;
  cursor: pointer;
}

.btn-save:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.empty-state,
.loading-state {
  padding: 2rem;
  text-align: center;
  color: #9ca3af;
}

.tip {
  font-size: 0.75rem;
  color: #9ca3af;
}
</style>


