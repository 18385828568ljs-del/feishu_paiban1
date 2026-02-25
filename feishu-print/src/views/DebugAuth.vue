<template>
  <div class="debug-page">
    <h1>认证调试页面</h1>
    
    <div class="section">
      <h2>1. 检查 Session Token</h2>
      <button @click="checkToken">检查 Token</button>
      <pre>{{ tokenInfo }}</pre>
    </div>
    
    <div class="section">
      <h2>2. 初始化用户</h2>
      <button @click="testInitUser">初始化用户</button>
      <pre>{{ initResult }}</pre>
    </div>
    
    <div class="section">
      <h2>3. 测试获取模板</h2>
      <button @click="testGetTemplates">获取 AI 模板</button>
      <pre>{{ templatesResult }}</pre>
    </div>
    
    <div class="section">
      <h2>4. 用户状态</h2>
      <pre>{{ userStatusInfo }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useUser } from '@/composables/useUser';
import { templateApi } from '@/api/templates';

const { initUser, userStatus } = useUser();

const tokenInfo = ref('');
const initResult = ref('');
const templatesResult = ref('');
const userStatusInfo = ref('');

const checkToken = () => {
  const token = localStorage.getItem('session_token');
  if (token) {
    tokenInfo.value = `✅ Token 存在\n长度: ${token.length}\n前50字符: ${token.substring(0, 50)}...`;
  } else {
    tokenInfo.value = '❌ Token 不存在';
  }
};

const testInitUser = async () => {
  initResult.value = '正在初始化...';
  try {
    const result = await initUser();
    initResult.value = `✅ 初始化成功\n${JSON.stringify(result, null, 2)}`;
    checkToken();
  } catch (error: any) {
    initResult.value = `❌ 初始化失败\n${error.message}\n${JSON.stringify(error.response?.data, null, 2)}`;
  }
};

const testGetTemplates = async () => {
  templatesResult.value = '正在获取...';
  try {
    const templates = await templateApi.getAll(undefined, 'ai');
    templatesResult.value = `✅ 获取成功\n共 ${templates.length} 个模板\n${JSON.stringify(templates.slice(0, 3), null, 2)}`;
  } catch (error: any) {
    templatesResult.value = `❌ 获取失败\n${error.message}\n${JSON.stringify(error.response?.data, null, 2)}`;
  }
};

onMounted(() => {
  checkToken();
  userStatusInfo.value = JSON.stringify(userStatus.value, null, 2);
});
</script>

<style scoped>
.debug-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.section {
  margin: 20px 0;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #f9f9f9;
}

h1 {
  color: #333;
}

h2 {
  color: #666;
  font-size: 18px;
  margin-bottom: 10px;
}

button {
  padding: 10px 20px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

button:hover {
  background: #66b1ff;
}

pre {
  background: #fff;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #ddd;
  overflow-x: auto;
  margin-top: 10px;
  font-size: 12px;
  line-height: 1.5;
}
</style>
