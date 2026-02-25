<template>
  <div class="dialog-overlay" @click.self="handleCancel">
    <div class="dialog">
      <div class="dialog-header">
        <h3>发送签名请求</h3>
        <button class="btn-close" @click="handleCancel">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
        </button>
      </div>

      <!-- Tab 导航 -->
      <div class="dialog-tabs">
        <div 
          :class="['tab-item', { active: activeTab === 'create' }]"
          @click="switchTab('create')"
        >
          新建请求
        </div>
        <div 
          :class="['tab-item', { active: activeTab === 'history' }]"
          @click="switchTab('history')"
        >
          历史记录
        </div>
      </div>
      
      <!-- 新建请求 Tab -->
      <div v-if="activeTab === 'create'" class="dialog-body">
        <div class="form-group">
          <label>签名人姓名 <span class="required">*</span></label>
          <input 
            v-model="signerName" 
            type="text" 
            placeholder="请输入签名人姓名"
            class="form-input"
          />
        </div>
        
        <div class="form-group">
          <label>签名人邮箱（可选）</label>
          <input 
            v-model="signerEmail" 
            type="email" 
            placeholder="请输入邮箱地址"
            class="form-input"
          />
        </div>
        
        <div class="form-group">
          <label>有效期</label>
          <div class="custom-select" @click="toggleDropdown">
            <div class="select-selected">
              {{ expiresOptions.find(o => o.value === expiresHours)?.label }}
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :class="{ rotated: showDropdown }"><path d="m6 9 6 6 6-6"/></svg>
            </div>
            <div v-if="showDropdown" class="select-options">
              <div 
                v-for="option in expiresOptions" 
                :key="option.value"
                :class="['select-option', { active: expiresHours === option.value }]"
                @click.stop="selectOption(option.value)"
              >
                {{ option.label }}
              </div>
            </div>
          </div>
        </div>

        <!-- 生成的链接 -->
        <div v-if="signatureLink" class="link-section">
          <label>签名链接</label>
          <div class="link-box">
            <input 
              ref="linkInput"
              :value="signatureLink" 
              readonly 
              class="form-input link-input"
            />
            <button class="btn-copy" @click="copyLink">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
              {{ copied ? '已复制' : '复制' }}
            </button>
          </div>
          <p class="link-tip">请将此链接发送给签名人，链接有效期为 {{ expiresHours }} 小时</p>
          
          <!-- 签名状态 -->
          <div class="status-section">
            <div class="status-row">
              <span class="status-label">状态：</span>
              <span :class="['status-badge', `status-${signatureStatus}`]">
                {{ signatureStatus === 'pending' ? '等待签名' : signatureStatus === 'signed' ? '已签名' : '已过期' }}
              </span>
              <button class="btn-refresh" @click="checkStatus" :disabled="isChecking">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :class="{ spinning: isChecking }"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg>
                刷新
              </button>
            </div>
            
            <!-- 已签名预览 -->
            <div v-if="signatureStatus === 'signed' && signatureData" class="signed-preview">
              <img :src="signatureData" alt="签名" />
              <button class="btn btn-success" @click="insertSignature">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
                插入签名到文档
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 历史记录 Tab -->
      <div v-if="activeTab === 'history'" class="dialog-body history-body">
        <div v-if="isLoadingHistory" class="loading-state">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="spinning"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg>
          正在加载记录...
        </div>
        <div v-else-if="historyList.length === 0" class="empty-state">
          暂无历史记录
        </div>
        <div v-else class="history-list">
          <div v-for="item in historyList" :key="item.id" class="history-item">
            <div class="history-item-header">
              <span class="signer-name">{{ item.signer_name }}</span>
              <span :class="['status-badge', `status-${item.status}`]">
                {{ getStatusLabel(item.status) }}
              </span>
            </div>
            <div class="history-item-meta">
              <span>{{ formatDate(item.created_at) }}</span>
              <span v-if="item.document_title" class="doc-title">{{ item.document_title }}</span>
            </div>
            
            <div class="history-item-actions">
              <template v-if="item.status === 'pending'">
                <button class="btn-text" @click="copyItemLink(item.token)">复制链接</button>
                <button class="btn-text" @click="refreshItemStatus(item)">刷新状态</button>
              </template>
              <template v-else-if="item.status === 'signed'">
                <div class="signed-actions">
                  <button class="btn-text btn-insert" @click="insertItemSignature(item.signature_data)">
                    插入签名
                  </button>
                  <img v-if="item.signature_data" :src="item.signature_data" class="mini-preview" />
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="activeTab === 'create'" class="dialog-footer">
        <button class="btn btn-outline" @click="handleCancel">关闭</button>
        <button 
          v-if="!signatureLink"
          class="btn btn-primary" 
          @click="generateLink" 
          :disabled="!signerName || isGenerating"
        >
          {{ isGenerating ? '生成中...' : '生成签名链接' }}
        </button>
      </div>
      <div v-else class="dialog-footer">
        <button class="btn btn-outline" @click="handleCancel">关闭</button>
        <button class="btn btn-primary" @click="fetchHistory">刷新列表</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { signatureApi, type SignatureData } from '@/api/signature';
import { ElMessage } from 'element-plus';
import dayjs from 'dayjs';

const props = defineProps<{
  documentHtml?: string;
  documentTitle?: string;
}>();

const emit = defineEmits(['close', 'insertSignature']);

const activeTab = ref<'create' | 'history'>('create');
const historyList = ref<SignatureData[]>([]);
const isLoadingHistory = ref(false);

const signerName = ref('');
const signerEmail = ref('');
const expiresHours = ref(72);
const showDropdown = ref(false);
const expiresOptions = [
  { value: 24, label: '24小时' },
  { value: 48, label: '48小时' },
  { value: 72, label: '72小时' },
  { value: 168, label: '7天' }
];
const signatureLink = ref('');

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value;
};

const selectOption = (value: number) => {
  expiresHours.value = value;
  showDropdown.value = false;
};
const isGenerating = ref(false);
const copied = ref(false);
const linkInput = ref<HTMLInputElement | null>(null);

const currentToken = ref('');
const signatureStatus = ref<'pending' | 'signed' | 'expired'>('pending');
const signatureData = ref('');
const isChecking = ref(false);

const generateLink = async () => {
  if (!signerName.value) {
    ElMessage.warning('请输入签名人姓名');
    return;
  }

  isGenerating.value = true;

  try {
    const result = await signatureApi.create({
      signer_name: signerName.value,
      signer_email: signerEmail.value || undefined,
      document_title: props.documentTitle || '文档签名',
      document_html: props.documentHtml || '',
      expires_hours: expiresHours.value
    });

    currentToken.value = result.token;
    signatureLink.value = signatureApi.generateLink(result.token);
    ElMessage.success('签名链接已生成');
  } catch (error) {
    console.error('生成签名链接失败:', error);
    ElMessage.error('生成签名链接失败');
  } finally {
    isGenerating.value = false;
  }
};

const checkStatus = async () => {
  if (!currentToken.value) return;
  
  isChecking.value = true;
  try {
    const result = await signatureApi.getByToken(currentToken.value);
    signatureStatus.value = result.status;
    if (result.signature_data) {
      signatureData.value = result.signature_data;
    }
    if (result.status === 'signed') {
      ElMessage.success('签名已完成！');
    }
  } catch (error) {
    console.error('检查状态失败:', error);
  } finally {
    isChecking.value = false;
  }
};

const insertSignature = () => {
  if (signatureData.value) {
    emit('insertSignature', signatureData.value);
    emit('close');
  }
};

const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(signatureLink.value);
    copied.value = true;
    ElMessage.success('链接已复制到剪贴板');
    setTimeout(() => {
      copied.value = false;
    }, 2000);
  } catch (error) {
    if (linkInput.value) {
      linkInput.value.select();
      document.execCommand('copy');
      copied.value = true;
      ElMessage.success('链接已复制到剪贴板');
      setTimeout(() => {
        copied.value = false;
      }, 2000);
    }
  }
};

const fetchHistory = async () => {
  isLoadingHistory.value = true;
  try {
    const list = await signatureApi.getAll();
    // 按时间倒序排列
    historyList.value = list.sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
  } catch (error) {
    console.error('获取签名历史失败:', error);
    ElMessage.error('获取历史记录失败');
  } finally {
    isLoadingHistory.value = false;
  }
};

const refreshItemStatus = async (item: SignatureData) => {
  try {
    const result = await signatureApi.getByToken(item.token);
    // 更新列表中的项目
    const index = historyList.value.findIndex(i => i.id === item.id);
    if (index !== -1) {
      historyList.value[index] = result;
    }
    ElMessage.success('状态已更新');
  } catch (error) {
    ElMessage.error('刷新状态失败');
  }
};

const copyItemLink = async (token: string) => {
  const link = signatureApi.generateLink(token);
  try {
    await navigator.clipboard.writeText(link);
    ElMessage.success('链接已复制');
  } catch (error) {
    // 降级处理
    const input = document.createElement('input');
    input.value = link;
    document.body.appendChild(input);
    input.select();
    document.execCommand('copy');
    document.body.removeChild(input);
    ElMessage.success('链接已复制');
  }
};

const insertItemSignature = (data: string | undefined) => {
  if (data) {
    emit('insertSignature', data);
    emit('close');
  }
};

const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm');
};

const getStatusLabel = (status: string) => {
  switch (status) {
    case 'pending': return '等待签名';
    case 'signed': return '已签名';
    case 'expired': return '已过期';
    default: return status;
  }
};

// 监听 Tab 切换
const switchTab = (tab: 'create' | 'history') => {
  activeTab.value = tab;
  if (tab === 'history') {
    fetchHistory();
  }
};

onMounted(() => {
  // 默认加载一次历史记录，或者可以懒加载
});

const handleCancel = () => {
  emit('close');
};
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.dialog {
  background: white;
  border-radius: 4px;
  width: 90%;
  max-width: 450px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  overflow: visible;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
}

.dialog-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #0f172a;
}

.btn-close {
  background: none;
  border: none;
  cursor: pointer;
  color: #64748b;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s;
}

.btn-close:hover {
  background-color: #f1f5f9;
  color: #0f172a;
}

.dialog-body {
  padding: 1.25rem;
  overflow: visible;
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
  color: #ef4444;
}

.form-input {
  width: 100%;
  padding: 0.625rem 0.875rem;
  font-size: 0.875rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  outline: none;
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: #0f172a;
  box-shadow: 0 0 0 2px rgba(15, 23, 42, 0.1);
}

.custom-select {
  position: relative;
  width: 100%;
}

.select-selected {
  width: 100%;
  padding: 0.625rem 0.875rem;
  font-size: 0.875rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s;
  box-sizing: border-box;
}

.select-selected:hover {
  border-color: #9ca3af;
}

.select-selected svg {
  color: #64748b;
  transition: transform 0.2s;
}

.select-selected svg.rotated {
  transform: rotate(180deg);
}

.select-options {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
  overflow: hidden;
}

.select-option {
  padding: 0.625rem 0.875rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.15s;
}

.select-option:hover {
  background: #f8fafc;
}

.select-option.active {
  background: #0f172a;
  color: white;
}

.link-section {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.link-box {
  display: flex;
  gap: 0.5rem;
}

.link-input {
  flex: 1;
  background-color: #f8fafc;
  font-family: monospace;
  font-size: 0.75rem;
}

.btn-copy {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #0f172a;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-copy:hover {
  background-color: #f8fafc;
  border-color: #cbd5e1;
}

.link-tip {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #64748b;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid #e2e8f0;
  background-color: #f8fafc;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.btn-primary {
  background-color: #0f172a;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #1e293b;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-outline {
  background-color: white;
  color: #0f172a;
  border-color: #e2e8f0;
}

.btn-outline:hover {
  background-color: #f8fafc;
  border-color: #cbd5e1;
}

.status-section {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px dashed #e2e8f0;
}

.status-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-label {
  font-size: 0.875rem;
  color: #64748b;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-pending {
  background-color: #fef3c7;
  color: #92400e;
}

.status-signed {
  background-color: #d1fae5;
  color: #065f46;
}

.status-expired {
  background-color: #fee2e2;
  color: #991b1b;
}

.btn-refresh {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  color: #64748b;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  cursor: pointer;
  margin-left: auto;
}

.btn-refresh:hover {
  background-color: #f8fafc;
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-refresh .spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.signed-preview {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 4px;
  text-align: center;
}

.signed-preview img {
  max-width: 100%;
  max-height: 80px;
  margin-bottom: 0.75rem;
}


.dialog-tabs {
  display: flex;
  border-bottom: 1px solid #e2e8f0;
  background-color: #f8fafc;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 12px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab-item:hover {
  color: #0f172a;
  background-color: #f1f5f9;
}

.tab-item.active {
  color: #0f172a;
  border-bottom-color: #0f172a;
  background-color: white;
}

.history-body {
  padding: 0;
  max-height: 400px;
  overflow-y: auto;
  min-height: 300px;
  background-color: #f8fafc;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #64748b;
  font-size: 0.875rem;
  gap: 12px;
  text-align: center;
}

.spinning {
  animation: spin 1s linear infinite;
  display: block;
  margin: 0 auto;
}

.history-list {
  display: flex;
  flex-direction: column;
}

.history-item {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 16px;
  transition: background 0.2s;
}

.history-item:hover {
  background-color: #fcfcfc;
}

.history-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.signer-name {
  font-weight: 600;
  color: #0f172a;
  font-size: 0.95rem;
}

.history-item-meta {
  display: flex;
  gap: 12px;
  font-size: 0.75rem;
  color: #94a3b8;
  margin-bottom: 12px;
}

.doc-title {
  color: #64748b;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-item-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-text {
  background: none;
  border: none;
  color: #2563eb;
  font-size: 0.8rem;
  padding: 0;
  cursor: pointer;
}

.btn-text:hover {
  text-decoration: underline;
}

.signed-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.btn-insert {
  color: #059669;
  font-weight: 500;
}

.mini-preview {
  height: 24px;
  border: 1px solid #e2e8f0;
  border-radius: 2px;
  background-color: white;
}

.btn-success {
  background-color: #059669;
  color: white;
}

.btn-success:hover {
  background-color: #047857;
}
</style>
