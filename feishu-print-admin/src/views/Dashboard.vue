<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon users">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ animatedStats.totalUsers }}</span>
          <span class="stat-label">总用户数</span>
        </div>
        <div class="stat-trend up">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m18 15-6-6-6 6"/></svg>
          +{{ animatedStats.newUsersToday }} 今日
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon orders">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ animatedStats.totalOrders }}</span>
          <span class="stat-label">总订单数</span>
        </div>
        <div class="stat-trend up">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m18 15-6-6-6 6"/></svg>
          +{{ animatedStats.ordersToday }} 今日
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon revenue">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="2" y2="22"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
        </div>
        <div class="stat-info">
          <span class="stat-value">¥{{ animatedStats.totalRevenue.toFixed(2) }}</span>
          <span class="stat-label">总收入</span>
        </div>
        <div class="stat-trend up">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m18 15-6-6-6 6"/></svg>
          +¥{{ animatedStats.revenueToday.toFixed(2) }} 今日
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon ai">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ animatedStats.totalAiGenerates }}</span>
          <span class="stat-label">AI 生成次数</span>
        </div>
        <div class="stat-trend">
          累计使用
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <div class="chart-card">
        <div class="chart-header">
          <h3>用户增长趋势</h3>
          <span class="chart-period">最近7天</span>
        </div>
        <div ref="userChartRef" class="echarts-container"></div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h3>收入趋势</h3>
          <span class="chart-period">最近7天</span>
        </div>
        <div ref="revenueChartRef" class="echarts-container"></div>
      </div>
    </div>

    <!-- 最新数据 -->
    <div class="recent-grid">
      <div class="recent-card">
        <div class="recent-header">
          <h3>最新订单</h3>
          <router-link to="/orders" class="view-all">查看全部</router-link>
        </div>
        <div class="recent-list">
          <div v-for="order in recentOrders" :key="order.id" class="recent-item">
            <div class="item-info">
              <span class="item-title">{{ order.plan_name }}</span>
              <span class="item-sub">{{ order.order_no }}</span>
            </div>
            <div class="item-meta">
              <span class="item-amount">¥{{ order.amount }}</span>
              <span :class="['item-status', order.status]">{{ getStatusText(order.status) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="recent-card">
        <div class="recent-header">
          <h3>最新用户</h3>
          <router-link to="/users" class="view-all">查看全部</router-link>
        </div>
        <div class="recent-list">
          <div v-for="user in recentUsers" :key="user.id" class="recent-item">
            <div class="item-avatar">
              {{ user.nickname?.charAt(0) || 'U' }}
            </div>
            <div class="item-info">
              <span class="item-title">{{ user.nickname || '未命名用户' }}</span>
              <span class="item-sub">{{ user.created_at }}</span>
            </div>
            <span :class="['plan-badge', user.plan_type]">{{ getPlanText(user.plan_type) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import * as echarts from 'echarts';
import { adminApi } from '@/api/admin';

const userChartRef = ref<HTMLElement | null>(null);
const revenueChartRef = ref<HTMLElement | null>(null);
let userChart: echarts.ECharts | null = null;
let revenueChart: echarts.ECharts | null = null;

// 动画数值
const animatedStats = ref({
  totalUsers: 0,
  newUsersToday: 0,
  totalOrders: 0,
  ordersToday: 0,
  totalRevenue: 0,
  revenueToday: 0,
  promoUsages: 0,
  activePromos: 0,
  totalAiGenerates: 0
});

const stats = ref({
  totalUsers: 0,
  newUsersToday: 0,
  totalOrders: 0,
  ordersToday: 0,
  totalRevenue: 0,
  revenueToday: 0,
  promoUsages: 0,
  activePromos: 0,
  totalAiGenerates: 0
});

const recentOrders = ref<any[]>([]);
const recentUsers = ref<any[]>([]);

// 数字滚动动画
const animateNumber = (key: keyof typeof animatedStats.value, target: number, duration = 1500) => {
  const start = animatedStats.value[key] || 0;
  const diff = target - start;
  const startTime = performance.now();
  
  const animate = (currentTime: number) => {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const easeProgress = 1 - Math.pow(1 - progress, 3);
    const current = start + diff * easeProgress;
    
    // 对于收入相关的字段，保留两位小数；其他字段四舍五入为整数
    if (key === 'totalRevenue' || key === 'revenueToday') {
      animatedStats.value[key] = Math.round(current * 100) / 100;
    } else {
      animatedStats.value[key] = Math.round(current);
    }
    
    if (progress < 1) {
      requestAnimationFrame(animate);
    } else {
      // 确保最终值准确
      if (key === 'totalRevenue' || key === 'revenueToday') {
        animatedStats.value[key] = Math.round(target * 100) / 100;
      } else {
        animatedStats.value[key] = Math.round(target);
      }
    }
  };
  
  requestAnimationFrame(animate);
};

// 初始化用户趋势图表
const initUserChart = (days: string[], data: number[]) => {
  if (!userChartRef.value) return;
  
  userChart = echarts.init(userChartRef.value);
  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: 'transparent',
      textStyle: { color: '#fff' },
      formatter: (params: any) => `${params[0].name}<br/>新增用户: <b>${params[0].value}</b>`
    },
    grid: { left: 0, right: 0, top: 10, bottom: 30, containLabel: true },
    xAxis: {
      type: 'category',
      data: days,
      axisLine: { lineStyle: { color: '#e5e7eb' } },
      axisLabel: { color: '#94a3b8', fontSize: 11 },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: { color: '#94a3b8', fontSize: 11 }
    },
    series: [{
      type: 'bar',
      data: data,
      barWidth: '50%',
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#3b82f6' },
          { offset: 1, color: '#93c5fd' }
        ])
      },
      emphasis: {
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#2563eb' },
            { offset: 1, color: '#60a5fa' }
          ])
        }
      },
      animationDuration: 1500,
      animationEasing: 'elasticOut'
    }]
  };
  userChart.setOption(option);
};

// 初始化收入趋势图表
const initRevenueChart = (days: string[], data: number[]) => {
  if (!revenueChartRef.value) return;
  
  revenueChart = echarts.init(revenueChartRef.value);
  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: 'transparent',
      textStyle: { color: '#fff' },
      formatter: (params: any) => `${params[0].name}<br/>收入: <b>¥${params[0].value}</b>`
    },
    grid: { left: 0, right: 0, top: 10, bottom: 30, containLabel: true },
    xAxis: {
      type: 'category',
      data: days,
      axisLine: { lineStyle: { color: '#e5e7eb' } },
      axisLabel: { color: '#94a3b8', fontSize: 11 },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: { color: '#94a3b8', fontSize: 11, formatter: '¥{value}' }
    },
    series: [{
      type: 'line',
      data: data,
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: { width: 3, color: '#059669' },
      itemStyle: { color: '#059669', borderWidth: 2, borderColor: '#fff' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(5, 150, 105, 0.3)' },
          { offset: 1, color: 'rgba(5, 150, 105, 0.05)' }
        ])
      },
      animationDuration: 2000,
      animationEasing: 'cubicOut'
    }]
  };
  revenueChart.setOption(option);
};

// 窗口大小变化时重绘图表
const handleResize = () => {
  userChart?.resize();
  revenueChart?.resize();
};

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    paid: '已支付',
    pending: '待支付',
    cancelled: '已取消'
  };
  return map[status] || status;
};

const getPlanText = (plan: string) => {
  const map: Record<string, string> = {
    free: '免费版',
    pro: '专业版',
    team: '团队版'
  };
  return map[plan] || plan;
};

onMounted(async () => {
  try {
    const data = await adminApi.getStats();
    stats.value = data.overview;
    recentOrders.value = data.recentOrders || [];
    recentUsers.value = data.recentUsers || [];
    
    // 数字滚动动画
    animateNumber('totalUsers', stats.value.totalUsers);
    animateNumber('newUsersToday', stats.value.newUsersToday);
    animateNumber('totalOrders', stats.value.totalOrders);
    animateNumber('ordersToday', stats.value.ordersToday);
    animateNumber('totalRevenue', stats.value.totalRevenue);
    animateNumber('revenueToday', stats.value.revenueToday);
    animateNumber('promoUsages', stats.value.promoUsages);
    animateNumber('activePromos', stats.value.activePromos);
    animateNumber('totalAiGenerates', stats.value.totalAiGenerates);
    
    // 初始化图表
    await nextTick();
    initUserChart(data.trendDays || [], data.userTrend || []);
    initRevenueChart(data.trendDays || [], data.revenueTrend || []);
    
    // 监听窗口大小变化
    window.addEventListener('resize', handleResize);
  } catch (e) {
    console.error('加载统计数据失败:', e);
  }
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  userChart?.dispose();
  revenueChart?.dispose();
});
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
}

.stat-card:hover .stat-icon {
  transform: scale(1.1);
}

.stat-card:hover .stat-value {
  color: #3b82f6;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease;
}

.stat-icon.users {
  background: #dbeafe;
  color: #2563eb;
}

.stat-icon.orders {
  background: #fef3c7;
  color: #d97706;
}

.stat-icon.revenue {
  background: #d1fae5;
  color: #059669;
}

.stat-icon.promos {
  background: #ede9fe;
  color: #7c3aed;
}

.stat-icon.ai {
  background: #fce7f3;
  color: #db2777;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #0f172a;
  transition: color 0.3s ease;
}

.stat-label {
  font-size: 0.875rem;
  color: #64748b;
}

.stat-trend {
  font-size: 0.75rem;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.stat-trend.up {
  color: #059669;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.chart-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.chart-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.echarts-container {
  width: 100%;
  height: 220px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.chart-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #0f172a;
}

.chart-period {
  font-size: 0.75rem;
  color: #64748b;
  background: #f1f5f9;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.chart-placeholder {
  height: 200px;
  display: flex;
  flex-direction: column;
}

.chart-bars {
  flex: 1;
  display: flex;
  align-items: flex-end;
  gap: 0.75rem;
  padding-bottom: 0.5rem;
}

.chart-bars .bar {
  flex: 1;
  background: linear-gradient(180deg, #3b82f6 0%, #60a5fa 100%);
  border-radius: 4px 4px 0 0;
  min-height: 4px;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.chart-bars .bar:hover {
  transform: scaleX(1.1);
  filter: brightness(1.1);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.chart-bars .bar::after {
  content: attr(title);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: #0f172a;
  color: white;
  padding: 0.375rem 0.625rem;
  border-radius: 6px;
  font-size: 0.75rem;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s;
  margin-bottom: 8px;
}

.chart-bars .bar:hover::after {
  opacity: 1;
}

.chart-bars.revenue .bar {
  background: linear-gradient(180deg, #059669 0%, #34d399 100%);
}

.chart-bars.revenue .bar:hover {
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.4);
}

.chart-labels {
  display: flex;
  justify-content: space-between;
  padding-top: 0.5rem;
  border-top: 1px solid #e5e7eb;
}

.chart-labels span {
  font-size: 0.75rem;
  color: #94a3b8;
}

.recent-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.recent-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.recent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.recent-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #0f172a;
}

.view-all {
  font-size: 0.875rem;
  color: #3b82f6;
  text-decoration: none;
}

.view-all:hover {
  text-decoration: underline;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 10px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.recent-item:hover {
  background: #f1f5f9;
  transform: translateX(4px);
}

.recent-item:hover .item-avatar {
  transform: scale(1.1);
}

.item-avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #0f172a, #334155);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
  transition: transform 0.2s ease;
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.item-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #0f172a;
}

.item-sub {
  font-size: 0.75rem;
  color: #94a3b8;
}

.item-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.125rem;
}

.item-amount {
  font-weight: 600;
  color: #0f172a;
}

.item-status {
  font-size: 0.75rem;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
}

.item-status.paid {
  background: #d1fae5;
  color: #059669;
}

.item-status.pending {
  background: #fef3c7;
  color: #d97706;
}

.plan-badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
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

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
