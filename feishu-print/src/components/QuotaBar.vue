<template>
  <div class="quota-section" v-if="userStatus">
    <div class="quota-card">
      <div class="quota-header">
        <div class="user-info">
          <span class="plan-tag" :class="userStatus.plan_type">
            {{ planName }}
          </span>
          <span class="welcome-text">当前权益使用情况</span>
        </div>
      </div>
      
      <div class="quota-metrics">
        <!-- PDF 导出额度 -->
        <div class="metric-item">
          <div class="metric-label">
            <span>导出</span>
            <span class="metric-value">
              <template v-if="userStatus.pdf_exports_limit === -1">无限量</template>
              <template v-else>
                {{ userStatus.pdf_exports_used }} / {{ userStatus.pdf_exports_limit }}
              </template>
            </span>
          </div>
          <div class="progress-track">
            <div 
              class="progress-bar" 
              :class="{ 'is-full': pdfPercent >= 100 }"
              :style="{ width: `${pdfPercent}%` }"
            ></div>
          </div>
        </div>

        <!-- AI 生成额度 -->
        <div class="metric-item">
          <div class="metric-label">
            <span>AI 生成</span>
            <span class="metric-value">
              <template v-if="userStatus.ai_generates_limit === -1">无限量</template>
              <template v-else>
                {{ userStatus.ai_generates_used }} / {{ userStatus.ai_generates_limit }}
              </template>
            </span>
          </div>
          <div class="progress-track">
            <div 
              class="progress-bar ai-bar"
              :class="{ 'is-full': aiPercent >= 100 }" 
              :style="{ width: `${aiPercent}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useUser } from '@/composables/useUser';

const { userStatus, planName } = useUser();

const pdfPercent = computed(() => {
  if (!userStatus.value || userStatus.value.pdf_exports_limit === -1) return 0;
  if (userStatus.value.pdf_exports_limit === 0) return 100;
  const percent = (userStatus.value.pdf_exports_used / userStatus.value.pdf_exports_limit) * 100;
  return Math.min(100, Math.max(0, percent));
});

const aiPercent = computed(() => {
  if (!userStatus.value || userStatus.value.ai_generates_limit === -1) return 0;
  if (userStatus.value.ai_generates_limit === 0) return 100;
  const percent = (userStatus.value.ai_generates_used / userStatus.value.ai_generates_limit) * 100;
  return Math.min(100, Math.max(0, percent));
});
</script>

<style scoped>
.quota-section {
  margin-bottom: 2rem;
  width: 100%;
  max-width: 1200px; /* match parent container if needed */
  margin-left: auto;
  margin-right: auto;
}

.quota-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  border: 1px solid #f1f5f9;
}

.quota-header {
  margin-bottom: 1.25rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.plan-tag {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.plan-tag.free {
  background-color: #f1f5f9;
  color: #64748b;
}

.plan-tag.pro {
  background-color: #e0f2fe;
  color: #0284c7;
}

.plan-tag.team {
  background-color: #f0fdf4;
  color: #16a34a;
}

.welcome-text {
  font-size: 0.95rem;
  font-weight: 600;
  color: #0f172a;
}

.quota-metrics {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.25rem;
}

@media (min-width: 640px) {
  .quota-metrics {
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
  }
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.metric-label {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  color: #475569;
}

.metric-value {
  font-weight: 500;
  color: #0f172a;
  font-feature-settings: "tnum";
}

.progress-track {
  height: 8px;
  background-color: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background-color: #0f172a;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.progress-bar.ai-bar {
  background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
}

.progress-bar.is-full {
  background-color: #ef4444; /* Red when full */
}
</style>
