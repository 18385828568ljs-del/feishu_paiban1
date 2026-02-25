<template>
  <div class="home-container">
    <nav class="home-nav">
      <div class="nav-buttons">
        <div class="user-id-display" v-if="maskedUserId">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
          </svg>
          <span>{{ maskedUserId }}</span>
          <button @click="copyUserId" class="btn-copy" title="复制完整用户ID">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
          </button>
        </div>
        <button @click="goToPricing" :class="['btn-member', planClass]">
          <svg v-if="userStatus?.plan_type === 'free'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
             <path d="m2 4 3 12h14l3-12-6 7-4-3-4 3-6-7z"/>
          </svg>
          <span>{{ planLabel }}</span>
        </button>
        <button v-if="userStatus?.plan_type === 'team'" @click="goToTeam" class="btn-team">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
          团队
        </button>
        <button @click="showFeedbackDialog = true" class="btn-feedback">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          反馈
        </button>
      </div>
    </nav>

    <!-- 反馈弹窗 -->
    <div v-if="showFeedbackDialog" class="dialog-overlay" @click.self="showFeedbackDialog = false">
      <div class="dialog">
        <div class="dialog-header">
          <h3>意见反馈</h3>
          <button @click="showFeedbackDialog = false" class="btn-close">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>反馈内容 <span class="required">*</span></label>
            <textarea v-model="feedbackContent" rows="5" class="form-textarea" placeholder="请描述您的问题或建议..."></textarea>
          </div>
          <div class="form-group">
            <label>联系方式 <span class="optional">(选填)</span></label>
            <input v-model="feedbackContact" type="text" class="form-input" placeholder="邮箱或手机号，方便我们回复您" />
          </div>
          <p v-if="feedbackError" class="error-msg">{{ feedbackError }}</p>
          <p v-if="feedbackSuccess" class="success-msg">{{ feedbackSuccess }}</p>
        </div>
        <div class="dialog-footer">
          <button @click="showFeedbackDialog = false" class="btn-cancel">取消</button>
          <button @click="submitFeedback" class="btn-confirm" :disabled="isSubmitting">
            {{ isSubmitting ? '提交中...' : '提交反馈' }}
          </button>
        </div>
      </div>
    </div>

    <main class="home-main">
      <div class="home-content">
        <div class="home-header">
          <h1 class="home-title">
            排版，本该如此简单
          </h1>
        </div>

        <div class="home-buttons">
          <button @click="goToEditor" class="btn btn-primary">
            编辑排版
          </button>
          <div class="ai-btn-wrapper" @click="goToAIGenerate">
            <div class="glow-shadow"></div>
            <div class="ai-btn-content">
              <svg class="ai-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L14.4 9.6L22 12L14.4 14.4L12 22L9.6 14.4L2 12L9.6 9.6L12 2Z" />
              </svg>
              <span class="btn-text">AI 模版</span>
            </div>
          </div>
          <button @click="goToLibrary" class="btn btn-secondary">
            模版库
          </button>
        </div>
      </div>
    </main>

    <footer class="home-footer">
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUser } from '@/composables/useUser';
import { ElMessage } from 'element-plus';

const router = useRouter();
const { initUser, userStatus } = useUser();

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

// 反馈相关
const showFeedbackDialog = ref(false);
const feedbackContent = ref('');
const feedbackContact = ref('');
const feedbackError = ref('');
const feedbackSuccess = ref('');
const isSubmitting = ref(false);

const submitFeedback = async () => {
  feedbackError.value = '';
  feedbackSuccess.value = '';
  
  if (!feedbackContent.value || feedbackContent.value.trim().length < 5) {
    feedbackError.value = '反馈内容至少需要5个字符';
    return;
  }
  
  isSubmitting.value = true;
  
  try {
    const response = await fetch(`${API_BASE}/api/feedback/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content: feedbackContent.value,
        contact: feedbackContact.value || null,
        user_id: userStatus.value?.id || null
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      feedbackSuccess.value = '感谢您的反馈！我们会认真处理。';
      feedbackContent.value = '';
      feedbackContact.value = '';
      setTimeout(() => {
        showFeedbackDialog.value = false;
        feedbackSuccess.value = '';
      }, 2000);
    } else {
      feedbackError.value = result.message || '提交失败';
    }
  } catch (e) {
    feedbackError.value = '网络错误，请重试';
  } finally {
    isSubmitting.value = false;
  }
};

// 计算属性
const planLabel = computed(() => {
  switch (userStatus.value?.plan_type) {
    case 'pro': return '专业版';
    case 'team': return '团队版';
    default: return '免费版';
  }
});

const planClass = computed(() => {
  switch (userStatus.value?.plan_type) {
    case 'pro': return 'plan-pro';
    case 'team': return 'plan-team';
    default: return 'plan-free';
  }
});

// 脱敏显示用户ID
const maskedUserId = computed(() => {
  if (!userStatus.value?.feishu_user_id) return '';
  const userId = userStatus.value.feishu_user_id;
  // 显示前6位，其余用***代替
  if (userId.length <= 6) return userId;
  return userId.substring(0, 6) + '***';
});

// 复制完整用户ID
const copyUserId = async () => {
  if (!userStatus.value?.feishu_user_id) return;
  
  try {
    await navigator.clipboard.writeText(userStatus.value.feishu_user_id);
    ElMessage.success('用户ID已复制到剪贴板');
  } catch (error) {
    // 降级方案：使用传统方法
    const textarea = document.createElement('textarea');
    textarea.value = userStatus.value.feishu_user_id;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    try {
      document.execCommand('copy');
      ElMessage.success('用户ID已复制到剪贴板');
    } catch (e) {
      ElMessage.error('复制失败，请手动复制');
    }
    document.body.removeChild(textarea);
  }
};

const goToEditor = () => {
  router.push('/editor');
};

const goToLibrary = () => {
  router.push('/library');
};

const goToAIGenerate = () => {
  router.push('/ai-generate');
};

const goToPricing = () => {
  // 始终跳转到定价/会员页面
  router.push('/pricing');
};

const goToTeam = () => {
  router.push('/team');
};

onMounted(() => {
  initUser();
});
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.home-container {
  background-color: white;
  color: #0f172a;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.home-nav {
  display: flex;
  justify-content: flex-end;
  padding: 1.5rem 2rem;
}

.nav-buttons {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-id-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 0.75rem;
  color: #64748b;
  font-family: 'Courier New', monospace;
}

.user-id-display svg {
  flex-shrink: 0;
}

.btn-copy {
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 3px;
  transition: all 0.2s ease;
  margin-left: 0.25rem;
}

.btn-copy:hover {
  background-color: #e2e8f0;
  color: #0f172a;
}

.btn-copy:active {
  transform: scale(0.95);
}

.nav-buttons {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-member {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: white;
  color: #0f172a;
  border: 1px solid #e2e8f0;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
}

.btn-member:hover {
  background-color: #f8fafc;
  border-color: #94a3b8;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.btn-member.plan-pro {
  background-color: #0f172a;
  color: white;
  border-color: #0f172a;
}

.btn-member.plan-pro:hover {
  background-color: #1e293b;
  border-color: #1e293b;
}

.btn-member.plan-team {
  background-color: #0f172a;
  color: #fbbf24;
  border-color: #0f172a;
}

.btn-member.plan-team:hover {
  background-color: #1e293b;
  border-color: #1e293b;
}

.home-main {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0 1.5rem;
}

.home-content {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.home-header {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.home-title {
  font-size: 2.25rem;
  font-weight: 700;
  letter-spacing: -0.025em;
  color: #0f172a;
  margin: 0;
  line-height: 1.2;
}

.home-subtitle {
  color: #64748b;
  font-size: 1.125rem;
  max-width: 36rem;
  margin: 0 auto;
  line-height: 1.75;
}

.home-buttons {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  justify-content: center;
  padding-top: 1rem;
}

.btn {
  padding: 1rem 3rem;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  font-size: 1rem;
}

.btn:active {
  transform: scale(0.95);
}

.btn-primary {
  background-color: #0f172a;
  color: white;
}

.btn-primary:hover {
  background-color: #1e293b;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.btn-secondary {
  background-color: white;
  color: #0f172a;
  border: 1px solid #e2e8f0;
}

.btn-secondary:hover {
  border-color: #94a3b8;
  background-color: #f8fafc;
}

/* AI按钮流光动效 */
.ai-btn-wrapper {
  position: relative;
  display: inline-block;
  padding: 3px;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.ai-btn-wrapper::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: conic-gradient(
    from 0deg,
    transparent 0%,
    transparent 20%,
    #8b5cf6 40%,
    #3b82f6 50%,
    #8b5cf6 60%,
    transparent 80%,
    transparent 100%
  );
  animation: ai-rotate 3s linear infinite;
}

.glow-shadow {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, #8b5cf6, #3b82f6);
  filter: blur(15px);
  opacity: 0.2;
  transition: opacity 0.3s ease;
  z-index: -1;
}

.ai-btn-wrapper:hover .glow-shadow {
  opacity: 0.5;
}

.ai-btn-content {
  position: relative;
  background: linear-gradient(135deg, #1f2937 0%, #4b5563 50%, #f9fafb 100%);
  padding: 1rem 2rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  z-index: 1;
  transition: background 0.3s ease;
}

.ai-btn-wrapper:hover .ai-btn-content {
  background: linear-gradient(135deg, #374151 0%, #6b7280 50%, #ffffff 100%);
}

.ai-btn-content .btn-text {
  font-weight: 600;
  font-size: 1rem;
  color: white;
}

.ai-icon {
  width: 18px;
  height: 18px;
  fill: #8b5cf6;
  filter: drop-shadow(0 0 4px #8b5cf6);
  animation: ai-pulse 2s ease-in-out infinite;
}

.ai-btn-content::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  border-radius: 4px;
  transition: 0.5s;
}

.ai-btn-wrapper:hover .ai-btn-content::after {
  left: 100%;
  transition: 0.7s;
}

.ai-btn-wrapper:active {
  transform: scale(0.96);
}

@keyframes ai-rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes ai-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(0.9); }
}

.home-footer {
  padding: 2.5rem;
  text-align: center;
  font-size: 0.75rem;
  color: #cbd5e1;
  letter-spacing: 0.05em;
}

.footer-links {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 1rem;
}

.footer-link {
  color: #cbd5e1;
  text-decoration: none;
  transition: color 0.2s ease;
}

.footer-link:hover {
  color: #475569;
}

.footer-copyright {
  margin: 0;
}

/* 响应式设计 */
@media (min-width: 640px) {
  .home-buttons {
    flex-direction: row;
  }
}

@media (min-width: 768px) {
  .home-title {
    font-size: 3.75rem;
  }
  
  .home-subtitle {
    font-size: 1.25rem;
  }
}

/* 团队按钮 */
.btn-team {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: white;
  color: #0f172a;
  border: 1px solid #e2e8f0;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-team:hover {
  background: #f8fafc;
  border-color: #94a3b8;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

/* 反馈按钮 */
.btn-feedback {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  background: white;
  color: #64748b;
  border: 1px solid #e2e8f0;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-feedback:hover {
  background: #f8fafc;
  color: #0f172a;
  border-color: #94a3b8;
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
  border-radius: 4px;
  width: 100%;
  max-width: 450px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
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
  margin: 0;
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

.required {
  color: #dc2626;
}

.optional {
  color: #94a3b8;
  font-weight: 400;
}

.form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  font-size: 0.875rem;
  resize: none;
  font-family: inherit;
  transition: border-color 0.2s;
}

.form-textarea:focus {
  outline: none;
  border-color: #0f172a;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #0f172a;
}

.error-msg {
  color: #dc2626;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.success-msg {
  color: #059669;
  font-size: 0.875rem;
  margin-top: 0.5rem;
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
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-confirm {
  padding: 0.625rem 1.25rem;
  background: #0f172a;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-confirm:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
