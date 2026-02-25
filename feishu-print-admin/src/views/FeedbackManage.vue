<template>
  <div class="feedback-manage">
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <button @click="filterStatus = ''" :class="['filter-btn', filterStatus === '' && 'active']">全部</button>
      <button @click="filterStatus = 'unread'" :class="['filter-btn', filterStatus === 'unread' && 'active']">未读</button>
      <button @click="filterStatus = 'read'" :class="['filter-btn', filterStatus === 'read' && 'active']">已读</button>
    </div>

    <!-- 反馈列表 -->
    <div class="feedback-list">
      <div v-for="feedback in filteredFeedbacks" :key="feedback.id" class="feedback-card" :class="{ unread: !feedback.is_read }">
        <div class="feedback-header">
          <div class="feedback-meta">
            <span class="feedback-id">#{{ feedback.id }}</span>
            <span v-if="!feedback.is_read" class="unread-badge">未读</span>
          </div>
          <span class="feedback-time">{{ formatDate(feedback.created_at) }}</span>
        </div>
        <div class="feedback-content">
          {{ feedback.content }}
        </div>
        <div v-if="feedback.contact" class="feedback-contact">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
          {{ feedback.contact }}
        </div>
        <div class="feedback-actions">
          <button v-if="!feedback.is_read" @click="markAsRead(feedback)" class="btn-action">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            标为已读
          </button>
          <button @click="deleteFeedback(feedback)" class="btn-action delete">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
            删除
          </button>
        </div>
      </div>

      <div v-if="filteredFeedbacks.length === 0" class="empty-state">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        <p>暂无反馈</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { adminApi } from '@/api/admin';

const feedbacks = ref<any[]>([]);
const filterStatus = ref('');

const filteredFeedbacks = computed(() => {
  if (filterStatus.value === 'unread') {
    return feedbacks.value.filter(f => !f.is_read);
  }
  if (filterStatus.value === 'read') {
    return feedbacks.value.filter(f => f.is_read);
  }
  return feedbacks.value;
});

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN');
};

const loadFeedbacks = async () => {
  try {
    const result = await adminApi.getFeedbacks();
    feedbacks.value = result.items || [];
  } catch (e) {
    console.error('加载反馈失败:', e);
  }
};

const markAsRead = async (feedback: any) => {
  try {
    await adminApi.markFeedbackRead(feedback.id);
    feedback.is_read = true;
  } catch (e) {
    console.error('标记失败:', e);
  }
};

const deleteFeedback = async (feedback: any) => {
  if (!confirm('确定要删除这条反馈吗？')) return;
  try {
    await adminApi.deleteFeedback(feedback.id);
    feedbacks.value = feedbacks.value.filter(f => f.id !== feedback.id);
  } catch (e) {
    console.error('删除失败:', e);
  }
};

onMounted(() => {
  loadFeedbacks();
});
</script>

<style scoped>
.feedback-manage {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.filter-bar {
  display: flex;
  gap: 0.5rem;
  background: white;
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filter-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #e5e7eb;
  background: white;
  border-radius: 8px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  background: #f8fafc;
}

.filter-btn.active {
  background: #0f172a;
  color: white;
  border-color: #0f172a;
}

.feedback-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.feedback-card {
  background: white;
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
}

.feedback-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.feedback-card.unread {
  border-left: 4px solid #3b82f6;
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.feedback-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.feedback-id {
  font-size: 0.75rem;
  color: #64748b;
  font-family: monospace;
}

.unread-badge {
  background: #dbeafe;
  color: #2563eb;
  font-size: 0.75rem;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  font-weight: 500;
}

.feedback-time {
  font-size: 0.75rem;
  color: #94a3b8;
}

.feedback-content {
  font-size: 0.9375rem;
  color: #374151;
  line-height: 1.6;
  margin-bottom: 0.75rem;
  white-space: pre-wrap;
}

.feedback-contact {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
  color: #64748b;
  margin-bottom: 0.75rem;
}

.feedback-actions {
  display: flex;
  gap: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid #f1f5f9;
}

.btn-action {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  background: #f1f5f9;
  border: none;
  border-radius: 6px;
  font-size: 0.8125rem;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s;
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
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  background: white;
  border-radius: 12px;
  color: #94a3b8;
  gap: 1rem;
}

.empty-state p {
  margin: 0;
}
</style>
