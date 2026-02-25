<template>
  <div class="template-library">
    <header class="library-header">
      <div class="header-left">
        <button @click="goBack" class="btn btn-secondary">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></svg>
          返回
        </button>
      </div>
      <div class="header-center">
        <h1 class="library-title">模板库</h1>
        <p class="library-subtitle">选择模板开始创作</p>
      </div>
      <div class="header-right">
        <button @click="handleCreateTemplate" class="btn btn-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
          新建模板
        </button>
      </div>
    </header>

    <div class="library-container">
      <!-- 分类和搜索 -->
      <div class="filter-section">
        <div class="filter-row">
          <!-- 搜索框 -->
          <div class="search-box">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="search-icon">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.35-4.35"/>
            </svg>
            <input 
              v-model="searchQuery" 
              @input="handleSearch"
              type="text" 
              placeholder="搜索模板名称..." 
              class="search-input"
            />
            <button 
              v-if="searchQuery" 
              @click="clearSearch" 
              class="clear-btn"
              title="清除搜索"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 6 6 18"/>
                <path d="m6 6 12 12"/>
              </svg>
            </button>
          </div>
          
          <!-- 分类标签 -->
          <div class="category-tabs">
            <button 
              @click="selectCategory('normal')"
              :class="['category-tab', { active: selectedCategory === 'normal' }]"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/>
                <path d="M14 2v4a2 2 0 0 0 2 2h4"/>
                <path d="M10 9H8"/>
                <path d="M16 13H8"/>
                <path d="M16 17H8"/>
              </svg>
              <span>模版</span>
            </button>
            <button 
              @click="selectCategory('ai')"
              :class="['category-tab', { active: selectedCategory === 'ai' }]"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
                <path d="M5 3v4"/>
                <path d="M9 3v4"/>
                <path d="M3 5h4"/>
                <path d="M3 9h4"/>
              </svg>
              <span>AI模版</span>
            </button>
            <button 
              @click="selectCategory('user')"
              :class="['category-tab', { active: selectedCategory === 'user' }]"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              <span>我的模版</span>
            </button>
          </div>
        </div>
        <div v-if="(searchQuery || selectedCategory) && templates.length > 0" class="search-result-info">
          找到 {{ templates.length }} 个模板
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="animate-spin"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
        </div>
        <p>加载模板中...</p>
      </div>

      <div v-else-if="templates.length === 0" class="empty-state">
        <div class="empty-icon">
          <svg v-if="searchQuery" xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.35-4.35"/>
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>
        </div>
        <p>{{ searchQuery ? '未找到匹配的模板' : '暂无模板' }}</p>
        <button v-if="!searchQuery" @click="goToEditor" class="btn btn-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
          创建第一个模板
        </button>
        <button v-else @click="clearSearch" class="btn btn-secondary">
          清除搜索
        </button>
      </div>

      <div v-else class="templates-grid">
        <div 
          v-for="template in templates" 
          :key="template.id" 
          class="template-card"
        >
          <div class="card-preview" @click="useTemplate(template.id)">
            <div class="preview-content" v-html="sanitizeHtml(getTemplatePreviewFirstPage(template.content))"></div>
          </div>
          <div class="card-footer">
            <div class="card-info">
              <h3 class="card-title">
                {{ template.name }}
                <span v-if="template.is_system" class="system-badge" title="系统模版">系统</span>
              </h3>
            </div>
            <div class="card-actions">
              <button @click="editTemplate(template)" class="btn-icon" title="编辑">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>
              </button>
              <button 
                v-if="!template.is_system"
                @click="deleteTemplate(template.id)" 
                class="btn-icon delete" 
                title="删除"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { templateApi } from '@/api/templates';
import { sanitizeHtml } from '@/utils/sanitize';

const getTemplatePreviewFirstPage = (html: string): string => {
  const raw = html || '';
  if (!raw.trim()) return raw;

  try {
    const parser = new DOMParser();
    const fullHtml = raw.includes('<html') || raw.includes('<body')
      ? raw
      : `<html><body>${raw}</body></html>`;
    const doc = parser.parseFromString(fullHtml, 'text/html');

    const templateRoot = doc.getElementById('template-root') as HTMLElement | null;
    if (!templateRoot) {
      return raw;
    }

    // 如果是多页结构，只取第一页预览
    const allPages = templateRoot.querySelectorAll('.template-page');
    if (allPages.length > 0) {
      // 保留第一页
      const firstPage = allPages[0];
      templateRoot.innerHTML = '';
      templateRoot.appendChild(firstPage);
    }

    return templateRoot.outerHTML;
  } catch (e) {
    return raw;
  }
};
import { useUser } from '@/composables/useUser';

const router = useRouter();
const route = useRoute();
const { initUser } = useUser();

const templates = ref<any[]>([]);
const loading = ref(true);
const searchQuery = ref('');
const selectedCategory = ref<string | null>('normal'); // 默认选中"模版"分类
let searchTimeout: ReturnType<typeof setTimeout> | null = null;

const loadTemplates = async (search?: string, templateType?: string, owner?: string) => {
  loading.value = true;
  try {
    const data = await templateApi.getAll(search, templateType, owner);
    templates.value = data;
  } catch (error) {
    console.error('加载模板失败:', error);
    ElMessage.error('加载模板失败');
  } finally {
    loading.value = false;
  }
};

const selectCategory = (category: string | null) => {
  // 如果点击的是已选中的分类，则取消选择（显示全部）
  if (selectedCategory.value === category) {
    selectedCategory.value = null;
  } else {
    selectedCategory.value = category;
  }
  const query = searchQuery.value.trim();
  if (selectedCategory.value === 'user') {
    loadTemplates(query || undefined, undefined, 'me');
  } else {
    loadTemplates(query || undefined, selectedCategory.value || undefined);
  }
};

const handleSearch = () => {
  // 防抖处理，避免频繁请求
  if (searchTimeout) {
    clearTimeout(searchTimeout);
  }
  
  searchTimeout = setTimeout(() => {
    const query = searchQuery.value.trim();
    if (selectedCategory.value === 'user') {
      loadTemplates(query || undefined, undefined, 'me');
    } else {
      loadTemplates(query || undefined, selectedCategory.value || undefined);
    }
  }, 300);
};

const clearSearch = () => {
  searchQuery.value = '';
  if (selectedCategory.value === 'user') {
    loadTemplates(undefined, undefined, 'me');
  } else {
    loadTemplates(undefined, selectedCategory.value || undefined);
  }
};

const useTemplate = (templateId: number) => {
  router.push({ name: 'editor', query: { templateId: String(templateId) } });
};

const handleCreateTemplate = () => {
  router.push({ name: 'editor', query: { mode: 'create' } });
};

const editTemplate = (template: any) => {
  router.push({ name: 'editor', query: { templateId: String(template.id), mode: 'edit' } });
};

const deleteTemplate = async (templateId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除此模板吗？', '删除模板', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });

    await templateApi.delete(templateId);
    ElMessage.success('模板已删除');
    const query = searchQuery.value.trim();
    if (selectedCategory.value === 'user') {
      loadTemplates(query || undefined, undefined, 'me');
    } else {
      loadTemplates(query || undefined, selectedCategory.value || undefined);
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除模板失败:', error);
      const errorMessage = error?.response?.data?.detail || '删除模板失败';
      ElMessage.error(errorMessage);
    }
  }
};

const goToEditor = () => {
  router.push('/editor');
};

const goBack = () => {
  router.push('/');
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN');
};

onMounted(async () => {
  try {
    // 初始化用户（确保有 session_token）
    await initUser();
    
    // 检查 token 是否存在
    const token = localStorage.getItem('session_token');
    
    if (!token) {
      console.error('[TemplateLibrary] 初始化后仍然没有 token!');
      ElMessage.error('用户认证失败，请刷新页面重试');
      return;
    }
    
    // 检查路由查询参数，如果有category参数则使用它，否则默认使用'normal'
    const categoryFromQuery = route.query.category as string | undefined;
    const initialCategory = categoryFromQuery || 'normal';
    selectedCategory.value = initialCategory;
    
    // 等待初始化完成后再加载模板
    if (initialCategory === 'user') {
      await loadTemplates(undefined, undefined, 'me');
    } else {
      await loadTemplates(undefined, initialCategory);
    }
  } catch (error) {
    console.error('[TemplateLibrary] 初始化失败:', error);
    ElMessage.error('初始化失败，请刷新页面重试');
  }
});
</script>

<style scoped>
.template-library {
  min-height: 100vh;
  background-color: #ffffff;
}

.library-header {
  background-color: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 1rem 2rem;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
}

.header-left {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-start;
}

.header-center {
  text-align: center;
}

.header-right {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.library-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.25rem 0;
  letter-spacing: -0.025em;
}

.library-subtitle {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0;
}

/* 统一按钮基础样式 */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.btn:active {
  transform: scale(0.98);
}

.btn-primary {
  background-color: #0f172a;
  color: white;
  border-color: #0f172a;
}

.btn-primary:hover {
  background-color: #1e293b;
  border-color: #1e293b;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.btn-outline {
  background-color: white;
  color: #0f172a;
  border: 1px solid #0f172a;
}

.btn-outline:hover {
  background-color: #f8fafc;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.btn-secondary {
  background-color: white;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.btn-secondary:hover {
  background-color: #f8fafc;
  border-color: #cbd5e1;
  color: #0f172a;
}

.library-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem;
}

.filter-section {
  margin-bottom: 2rem;
  padding: 0 0.5rem;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.category-tabs {
  display: flex;
  gap: 0.75rem;
  flex-shrink: 0;
}

.category-tab {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #64748b;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.category-tab:hover {
  background-color: #f8fafc;
  border-color: #cbd5e1;
  color: #334155;
}

.category-tab.active {
  background-color: #0f172a;
  border-color: #0f172a;
  color: white;
  font-weight: 600;
}

.category-tab svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.search-section {
  margin-bottom: 0;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 500px;
  display: flex;
  align-items: center;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  transition: all 0.2s;
}

.search-box:focus-within {
  border-color: #0f172a;
  box-shadow: 0 0 0 3px rgba(15, 23, 42, 0.1);
}

.search-icon {
  color: #94a3b8;
  flex-shrink: 0;
  margin-right: 0.75rem;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 0.875rem;
  color: #0f172a;
  background: transparent;
}

.search-input::placeholder {
  color: #94a3b8;
}

.clear-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
  flex-shrink: 0;
  margin-left: 0.5rem;
}

.clear-btn:hover {
  background-color: #f1f5f9;
  color: #0f172a;
}

.search-result-info {
  text-align: center;
  margin-top: 0.75rem;
  font-size: 0.875rem;
  color: #64748b;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #64748b;
}

.loading-icon {
  margin-bottom: 1rem;
  color: #0f172a;
}

.empty-icon {
  margin-bottom: 1rem;
  color: #cbd5e1;
}

.empty-state p {
  font-size: 1.125rem;
  margin-bottom: 1.5rem;
  color: #64748b;
}

.empty-state .btn {
  margin-top: 0.5rem;
}

/* 旋转动画 */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}


.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, 180px); /* Reduced card width */
  gap: 1.5rem;
  justify-content: center;
}

.template-card {
  background-color: #f1f5f9; /* Light gray background for concave feel */
  border-radius: 0;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  margin: 0;
  padding: 6px; /* 6px gap */
  width: 180px; /* Reduced width */
}

.template-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  border-color: #cbd5e1;
}

.card-preview {
  height: 237.5px; /* A4比例: 168px / (210/297) = 237.5px */
  overflow: hidden;
  background-color: white;
  position: relative;
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  margin: 0;
  padding: 0;
  width: 100%;
}

.preview-content {
  position: absolute;
  top: 0;
  left: 0;
  width: 210mm;
  min-height: 297mm; /* 改为 min-height，让短内容也能撑满 */
  transform: scale(0.2117); /* 精确A4比例: 168px / 793.7px ≈ 0.2117 */
  transform-origin: top left;
  pointer-events: none;
  background: white;
  padding: 0 !important;
  margin: 0 !important;
  box-sizing: border-box;
  color: #1f2937;
  overflow: hidden; /* 确保内容不溢出 */
}

.preview-content :deep(*) {
  color: inherit;
}

.preview-content :deep(#template-root) {
  /* 统一与编辑器 Editor.vue 中 TEMPLATE_ROOT_STYLE 保持一致 */
  width: 100% !important;
  min-height: 297mm !important; /* 预览需要填满 A4 高度 */
  padding: 0 !important; /* 修复：移除多余的 padding，避免内容被挤小 */
  margin: 0 !important;
  box-sizing: border-box !important;
  background-size: cover !important;
  background-position: center !important;
  background-repeat: no-repeat !important;
}

.preview-content :deep(.template-page) {
  margin: 0 !important;
  box-shadow: none !important;
  width: 100% !important;
  border: none !important;
}

.preview-content :deep(body) {
  margin: 0 !important;
  padding: 0 !important;
}

.preview-content :deep(table) {
  border-color: #d1d5db !important;
  width: 100% !important;
}

.preview-content :deep(td),
.preview-content :deep(th) {
  border-color: #d1d5db !important;
  color: #000000 !important;
}


.card-footer {
  padding: 0.75rem;
  background-color: white;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-info {
  flex: 1;
  min-width: 0;
  margin-right: 0.5rem;
}

.card-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #334155;
  margin: 0;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.system-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.375rem;
  font-size: 0.625rem;
  font-weight: 500;
  color: #0f172a;
  background-color: #e0e7ff;
  border-radius: 4px;
  flex-shrink: 0;
  line-height: 1;
}

.card-actions {
  display: flex;
  gap: 0.25rem;
  flex-shrink: 0;
}

.btn-icon {
  width: 28px;
  height: 28px;
  padding: 0;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 4px;
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background-color: #f1f5f9;
  color: #0f172a;
}

.btn-icon.delete:hover {
  background-color: #fee2e2;
  color: #ef4444;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .filter-row {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }
  
  .search-box {
    max-width: 100%;
  }
  
  .category-tabs {
    justify-content: flex-start;
  }
}
</style>
