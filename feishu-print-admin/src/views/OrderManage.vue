<template>
  <div class="order-manage">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <div class="search-input-wrapper">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        <input v-model="searchQuery" type="text" placeholder="搜索订单号、用户..." @keyup.enter="handleSearch" />
      </div>
      <select v-model="filterStatus" class="filter-select">
        <option value="">全部状态</option>
        <option value="pending">待支付</option>
        <option value="paid">已支付</option>
        <option value="cancelled">已取消</option>
      </select>
      <button @click="handleSearch" class="btn-search">搜索</button>
    </div>

    <!-- 订单表格 -->
    <div class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>订单号</th>
            <th>用户</th>
            <th>会员类型</th>
            <th>金额</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>支付时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.id">
            <td class="text-mono">{{ order.order_no }}</td>
            <td>
              <div class="user-cell">
                <div class="user-avatar">{{ order.user_nickname?.charAt(0) || 'U' }}</div>
                <div>
                  <div>{{ order.user_nickname || '未命名' }}</div>
                  <div class="text-muted">{{ order.user_feishu_id }}</div>
                </div>
              </div>
            </td>
            <td>
              <span :class="['plan-badge', order.plan_type]">{{ getPlanText(order.plan_type) }}</span>
            </td>
            <td>¥{{ (order.amount / 100).toFixed(2) }}</td>
            <td>
              <span :class="['status-badge', order.status ? order.status.toLowerCase() : '']">{{ getStatusText(order.status) }}</span>
            </td>
            <td>{{ formatDate(order.created_at) }}</td>
            <td>{{ order.paid_at ? formatDate(order.paid_at) : '-' }}</td>
          </tr>
        </tbody>
      </table>

      <div v-if="orders.length === 0" class="empty-state">
        <p>暂无订单数据</p>
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { adminApi } from '@/api/admin';

const orders = ref<any[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = 20;
const searchQuery = ref('');
const filterStatus = ref('');

const totalPages = computed(() => Math.ceil(total.value / pageSize));

const getPlanText = (plan: string) => {
  const map: Record<string, string> = { free: '免费版', pro: '专业版', team: '团队版' };
  return map[plan] || plan;
};

const getStatusText = (status: string) => {
  const map: Record<string, string> = { 
    PENDING: '待支付', 
    PAID: '已支付', 
    CANCELLED: '已取消',
    REFUNDED: '已退款',
    pending: '待支付', 
    paid: '已支付', 
    cancelled: '已取消',
    refunded: '已退款'
  };
  return map[status] || status;
};

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN');
};

const loadOrders = async () => {
  try {
    const result = await adminApi.getOrders({
      page: page.value,
      pageSize,
      search: searchQuery.value,
      status: filterStatus.value
    });
    orders.value = result.items;
    total.value = result.total;
  } catch (e) {
    console.error('加载订单失败:', e);
  }
};

const handleSearch = () => {
  page.value = 1;
  loadOrders();
};

const changePage = (p: number) => {
  page.value = p;
  loadOrders();
};

onMounted(() => {
  loadOrders();
});
</script>

<style scoped>
.order-manage {
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
  flex-shrink: 0;
}

.text-mono {
  font-family: monospace;
  font-size: 0.75rem;
  color: #64748b;
}

.text-muted {
  font-size: 0.75rem;
  color: #9ca3af;
}

.plan-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
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

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
}

.status-badge.pending {
  background: #fef3c7;
  color: #d97706;
}

.status-badge.paid {
  background: #dcfce7;
  color: #166534;
}

.status-badge.cancelled {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.refunded {
  background: #f3f4f6;
  color: #374151;
}

.empty-state {
  padding: 3rem;
  text-align: center;
  color: #9ca3af;
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
  border: 1px solid #e5e7eb;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
}

.page-btn:hover:not(:disabled) {
  background: #f8fafc;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-current {
  padding: 0.5rem 1rem;
  background: #0f172a;
  color: white;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
}
</style>

