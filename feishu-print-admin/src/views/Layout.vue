<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="sidebar-header">
        <div class="logo">
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.375 2.625a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4Z"/></svg>
        </div>
        <span v-if="!isCollapsed" class="logo-text">智能排版</span>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/dashboard" class="nav-item" active-class="active">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>
          <span v-if="!isCollapsed">仪表盘</span>
        </router-link>
        
        <router-link to="/users" class="nav-item" active-class="active">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          <span v-if="!isCollapsed">用户管理</span>
        </router-link>
        
        <router-link to="/feedbacks" class="nav-item" active-class="active">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          <span v-if="!isCollapsed">反馈管理</span>
        </router-link>
        
        <router-link to="/orders" class="nav-item" active-class="active">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>
          <span v-if="!isCollapsed">订单管理</span>
        </router-link>
        
        <router-link to="/promos" class="nav-item" active-class="active">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0Z"/><circle cx="12" cy="10" r="3"/></svg>
          <span v-if="!isCollapsed">邀请码管理</span>
        </router-link>

        <router-link to="/plans" class="nav-item" active-class="active">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M16 8h-6a2 2 0 0 0 0 4h4a2 2 0 0 1 0 4H8"/><path d="M12 6v2"/><path d="M12 16v2"/></svg>
          <span v-if="!isCollapsed">会员价格管理</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <button @click="isCollapsed = !isCollapsed" class="btn-collapse">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :style="{ transform: isCollapsed ? 'rotate(180deg)' : '' }"><path d="m15 18-6-6 6-6"/></svg>
        </button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="main-wrapper">
      <!-- 顶部栏 -->
      <header class="topbar">
        <div class="topbar-left">
          <h2>{{ currentTitle }}</h2>
        </div>
        <div class="topbar-right">
          <div class="user-info">
            <div class="avatar">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="5"/><path d="M20 21a8 8 0 0 0-16 0"/></svg>
            </div>
            <span class="username">{{ adminUser?.username || 'Admin' }}</span>
          </div>
          <button @click="showPasswordDialog = true" class="btn-password">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            修改密码
          </button>
          <button @click="handleLogout" class="btn-logout">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>
            退出
          </button>
        </div>
      </header>

      <!-- 内容区 -->
      <main class="main-content">
        <router-view />
      </main>
    </div>

    <!-- 修改密码弹窗 -->
    <div v-if="showPasswordDialog" class="dialog-overlay" @click.self="showPasswordDialog = false">
      <div class="dialog">
        <div class="dialog-header">
          <h3>修改密码</h3>
          <button @click="showPasswordDialog = false" class="btn-close">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>当前密码</label>
            <input v-model="oldPassword" type="password" class="form-input" placeholder="请输入当前密码" />
          </div>
          <div class="form-group">
            <label>新密码</label>
            <input v-model="newPassword" type="password" class="form-input" placeholder="请输入新密码" />
          </div>
          <div class="form-group">
            <label>确认新密码</label>
            <input v-model="confirmPassword" type="password" class="form-input" placeholder="请再次输入新密码" />
          </div>
          <p v-if="passwordError" class="error-msg">{{ passwordError }}</p>
        </div>
        <div class="dialog-footer">
          <button @click="showPasswordDialog = false" class="btn-cancel">取消</button>
          <button @click="handleChangePassword" class="btn-confirm" :disabled="isChangingPassword">
            {{ isChangingPassword ? '修改中...' : '确认修改' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';

const router = useRouter();
const route = useRoute();
const isCollapsed = ref(false);

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

// 修改密码相关
const showPasswordDialog = ref(false);
const oldPassword = ref('');
const newPassword = ref('');
const confirmPassword = ref('');
const passwordError = ref('');
const isChangingPassword = ref(false);

const adminUser = computed(() => {
  const user = localStorage.getItem('admin_user');
  return user ? JSON.parse(user) : null;
});

const currentTitle = computed(() => {
  return (route.meta?.title as string) || '仪表盘';
});

const handleLogout = () => {
  localStorage.removeItem('admin_token');
  localStorage.removeItem('admin_user');
  router.push('/login');
};

const handleChangePassword = async () => {
  passwordError.value = '';
  
  if (!oldPassword.value) {
    passwordError.value = '请输入当前密码';
    return;
  }
  if (!newPassword.value) {
    passwordError.value = '请输入新密码';
    return;
  }
  if (newPassword.value.length < 6) {
    passwordError.value = '新密码长度不能少于6位';
    return;
  }
  if (newPassword.value !== confirmPassword.value) {
    passwordError.value = '两次输入的密码不一致';
    return;
  }
  
  isChangingPassword.value = true;
  
  try {
    const response = await fetch(`${API_BASE}/api/admin/change-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: adminUser.value?.username,
        old_password: oldPassword.value,
        new_password: newPassword.value
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      showPasswordDialog.value = false;
      oldPassword.value = '';
      newPassword.value = '';
      confirmPassword.value = '';
      ElMessage.success('密码修改成功');
    } else {
      passwordError.value = result.message || '修改失败';
    }
  } catch (e) {
    passwordError.value = '修改失败，请重试';
  } finally {
    isChangingPassword.value = false;
  }
};
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: #f5f7fa;
}

.sidebar {
  width: 260px;
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 100;
}

.sidebar.collapsed {
  width: 72px;
}

.sidebar-header {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.logo-text {
  font-size: 1.125rem;
  font-weight: 700;
  color: white;
  white-space: nowrap;
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  border-radius: 10px;
  transition: all 0.2s;
  white-space: nowrap;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.active {
  background: rgba(255, 255, 255, 0.15);
  color: white;
}

.nav-item svg {
  flex-shrink: 0;
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-collapse {
  width: 100%;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-collapse:hover {
  background: rgba(255, 255, 255, 0.15);
  color: white;
}

.btn-collapse svg {
  transition: transform 0.3s;
}

.main-wrapper {
  flex: 1;
  margin-left: 260px;
  transition: margin-left 0.3s ease;
  display: flex;
  flex-direction: column;
}

.sidebar.collapsed + .main-wrapper {
  margin-left: 72px;
}

.topbar {
  height: 64px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  position: sticky;
  top: 0;
  z-index: 50;
}

.topbar-left h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #0f172a;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.avatar {
  width: 36px;
  height: 36px;
  background: #f1f5f9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
}

.username {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.btn-logout {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  background: #fee2e2;
  color: #dc2626;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: #fecaca;
}

.btn-password {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  background: #f1f5f9;
  color: #475569;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-password:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.main-content {
  flex: 1;
  padding: 1.5rem;
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

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.875rem;
  outline: none;
  transition: border-color 0.2s;
}

.form-input:focus {
  border-color: #0f172a;
}

.error-msg {
  color: #dc2626;
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
