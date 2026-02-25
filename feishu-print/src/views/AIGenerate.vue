<template>
  <div class="ai-generate-page">
    <!-- 顶部导航 -->
    <nav class="top-nav">
      <button @click="goBack" class="nav-back">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
      </button>
      <div class="nav-title">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>
        <span>智能模板工坊</span>
      </div>
    </nav>

    <div class="workspace">
      <!-- 左侧面板 -->
      <Transition name="slide-fade">
        <aside v-show="showLeftPanel" class="left-panel">
        <!-- 面板标题栏 -->
        <div class="panel-header">
          <div class="panel-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>
            <span>配置</span>
          </div>

        </div>
        




        <!-- 模式切换 -->
        <div class="mode-toggle">
          <button 
            @click="selectedMode = 'traditional'"
            class="mode-btn"
            :class="{ active: selectedMode === 'traditional' }"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
            传统
          </button>
          <button 
            @click="selectedMode = 'design'"
            class="mode-btn"
            :class="{ active: selectedMode === 'design' }"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
            现代
          </button>
        </div>

        <!-- 分类选择 -->
        <div class="category-tabs">
          <button 
            v-for="cat in categories" 
            :key="cat.id"
            @click="selectedCategory = cat.id"
            class="category-tab"
            :class="{ active: selectedCategory === cat.id }"
          >
            <span class="cat-icon" v-html="sanitizeHtml(cat.icon)"></span>
            <span>{{ cat.label }}</span>
          </button>
        </div>

        <!-- 场景选择 -->
        <div class="panel-section">
          <div class="section-header">
            <span class="section-label">选择场景</span>
            <span class="section-hint">{{ filteredPrompts.length }} 个模板</span>
          </div>
          <div class="scene-grid">
            <button 
              v-for="(prompt, index) in filteredPrompts" 
              :key="prompt.label"
              @click="selectPrompt(prompt)"
              class="scene-card"
              :class="{ active: selectedPrompt === prompt.label }"
              :style="{ animationDelay: `${index * 30}ms` }"
            >
              <span class="scene-icon" v-html="sanitizeHtml(getSceneIcon(prompt.label))"></span>
              <span class="scene-name">{{ prompt.label }}</span>
            </button>
          </div>
        </div>

        <!-- 字段选择 -->
        <div class="panel-section" v-if="availableFields.length > 0">
          <div class="section-header">
            <span class="section-label">选择字段</span>
            <span class="section-hint">{{ selectedFields.length }}/{{ availableFields.length }} 已选</span>
          </div>
          <div class="field-select-actions">
            <button @click="selectAllFields" class="field-action-btn">全选</button>
            <button @click="clearAllFields" class="field-action-btn">清空</button>
          </div>
          <div class="field-list">
            <label 
              v-for="field in availableFields" 
              :key="field.id"
              class="field-item"
              :class="{ selected: selectedFields.includes(field.id) }"
            >
              <input 
                type="checkbox" 
                :value="field.id"
                v-model="selectedFields"
                class="field-checkbox"
              />
              <span class="field-name">{{ field.name }}</span>
            </label>
          </div>
        </div>

        <!-- 需求描述 -->
        <div class="panel-section flex-1">
          <div class="section-header">
            <span class="section-label">描述需求</span>
          </div>
          <div class="input-wrapper">
            <textarea 
              v-model="description"
              placeholder="描述你想要的模板，例如：&#10;&#10;• 需要哪些字段&#10;• 表格的结构&#10;• 签名区域位置&#10;• 特殊格式要求"
              class="desc-textarea"
              :disabled="isGenerating"
            ></textarea>
            <div class="input-meta">
              <span class="word-count">{{ description.length }}/500</span>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-bar">
          <button 
            v-if="isGenerating" 
            @click="stopGenerate" 
            class="action-btn stop-btn"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>
            停止
          </button>
          <div 
            v-else
            @click="!description.trim() ? null : generateTemplate()" 
            class="ai-generate-btn-wrapper"
            :class="{ disabled: !description.trim() }"
          >
            <div class="glow-shadow"></div>
            <div class="ai-generate-btn-content">
              <svg class="ai-generate-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L14.4 9.6L22 12L14.4 14.4L12 22L9.6 14.4L2 12L9.6 9.6L12 2Z" />
              </svg>
              <span class="btn-text">生成模板</span>
            </div>
          </div>
        </div>

        <!-- 进度指示 -->
        <div v-if="isGenerating" class="progress-bar">
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: (currentStep / 4) * 100 + '%' }"></div>
          </div>
          <span class="progress-text">{{ getStepText() }}</span>
        </div>
      </aside>
      </Transition>

      <!-- 右侧预览区 -->
      <main class="preview-area" :class="{ 'full-width': !showLeftPanel }">
        <div class="preview-toolbar">
          <div class="toolbar-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
            <span>预览</span>
          </div>
          <div class="toolbar-actions">
            <button @click="showLeftPanel = !showLeftPanel" class="tool-btn" :class="{ active: showLeftPanel }">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="3" x2="9" y2="21"/></svg>
              {{ showLeftPanel ? '隐藏配置' : '显示配置' }}
            </button>

            <button v-if="generatedHtml && !isGenerating" @click="regenerate" class="tool-btn">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/></svg>
              重新生成
            </button>
            <button v-if="generatedHtml && !isGenerating" @click="saveTemplate" class="tool-btn primary">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15.2 3a2 2 0 0 1 1.4.6l3.8 3.8a2 2 0 0 1 .6 1.4V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/><path d="M17 21v-8H7v8"/><path d="M7 3v5h8"/></svg>
              保存使用
            </button>
          </div>
        </div>
        
        <div class="preview-canvas">
          <!-- 空状态 -->
          <div v-if="!generatedHtml && !isGenerating" class="empty-state">
            <div class="empty-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><line x1="3" x2="21" y1="9" y2="9"/><line x1="9" x2="9" y1="21" y2="9"/></svg>
            </div>
            <h3 class="empty-title">开始创建模板</h3>
            <p class="empty-desc">选择场景或输入描述，点击生成按钮</p>
          </div>
          
          <!-- 生成中 -->
          <div v-else-if="isGenerating && !generatedHtml" class="loading-state">
            <div class="loading-animation">
              <div class="loading-dot"></div>
              <div class="loading-dot"></div>
              <div class="loading-dot"></div>
            </div>
            <p class="loading-text">{{ generatingStatus || '正在生成模板...' }}</p>
            <p v-if="receivedChars > 0" class="loading-desc">已接收 {{ receivedChars }} 字符</p>
          </div>
          
          <!-- 预览内容 -->
          <div v-else class="preview-document">
            <div 
              class="a4-container" 
              v-html="sanitizeHtml(displayHtml)"
            ></div>
            <span v-if="isGenerating" class="cursor-blink">|</span>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { templateApi } from '@/api/templates';
import { useUser } from '@/composables/useUser';
import { bitable } from '@lark-base-open/js-sdk';
import { sanitizeHtml } from '@/utils/sanitize';

const router = useRouter();
const { initUser, checkAndUseFeature, userStatus, refreshStatus } = useUser();

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

onMounted(async () => {
  initUser();
  await loadFieldList();
});

// 加载字段列表
const loadFieldList = async () => {
  try {
    const table = await bitable.base.getActiveTable();
    const fieldMetaList = await table.getFieldMetaList();
    availableFields.value = fieldMetaList
      .filter(field => field.name && field.name.trim() !== '')
      .map(field => ({
        name: field.name,
        id: field.id,
        type: field.type.toString()
      }));
    // 默认全选
    selectedFields.value = availableFields.value.map(f => f.id);
  } catch (error) {
    console.warn('获取字段列表失败:', error);
  }
};

const description = ref('');
const generatedHtml = ref('');
const cleanedHtml = ref(''); // 最终清理后的HTML
const isGenerating = ref(false);
const currentStep = ref(0);
const selectedPrompt = ref('');
const selectedCategory = ref('all');
const selectedMode = ref('traditional'); // 传统模式 'traditional' 或 设计模式 'design'

const abortController = ref<AbortController | null>(null);
const showLeftPanel = ref(true); // 控制左侧面板显示/隐藏
const generatingStatus = ref(''); // 生成状态消息
const receivedChars = ref(0); // 已接收字符数
const isPreviewMode = ref(false); // 预览模式状态
const availableFields = ref<{ name: string; id: string; type: string }[]>([]); // 可用字段列表
const selectedFields = ref<string[]>([]); // 选中的字段ID列表
const recordData = ref<any>(null); // 当前记录数据

// 简单清理：生成过程中只做基本清理
const simpleCleanHtml = computed(() => {
  let html = generatedHtml.value;
  // 只移除 markdown 标记和开头文字
  html = html.replace(/```html/g, '').replace(/```/g, '');
  const firstTag = html.indexOf('<');
  if (firstTag > 0) {
    html = html.slice(firstTag);
  }
  return html;
});

// 完整清理：只在生成完成后执行一次
const cleanGeneratedHtml = computed(() => {
  // 如果正在生成，使用简单清理
  if (isGenerating.value) {
    return simpleCleanHtml.value;
  }
  // 生成完成后，使用清理后的HTML
  return cleanedHtml.value || simpleCleanHtml.value;
});

// 显示用的HTML：预览模式下替换占位符，编辑模式下显示原始HTML
const displayHtml = computed(() => {
  if (!isPreviewMode.value || !recordData.value) {
    // 编辑模式：确保占位符有蓝色背景样式
    let html = cleanGeneratedHtml.value;
    // 使用DOM解析确保占位符样式正确
    try {
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      const fieldElements = doc.querySelectorAll('.template-field.field-block');
      fieldElements.forEach((element: Element) => {
        const htmlElement = element as HTMLElement;
        // 默认不设置任何 style，保持默认样式（或透明）
        // htmlElement.setAttribute('style', '...');
      });
      html = doc.body.innerHTML;
    } catch (e) {
      if (import.meta.env.DEV) {
        console.warn('DOM解析失败:', e);
      }
    }
    return html;
  }
  
  // 预览模式：替换占位符为实际数据
  return renderPreviewHtml(cleanGeneratedHtml.value);
});

// 完整清理函数（只在生成完成后调用）
const performFullClean = (inputHtml: string): string => {
  let html = inputHtml;
  
  // 1. 移除 markdown 标记
  html = html.replace(/```html/g, '').replace(/```/g, '');

  // 2. 移除可能的开头文字（如 "好的..."）- 找到第一个 < 并截取
  const firstTag = html.indexOf('<');
  if (firstTag > 0) {
    html = html.slice(firstTag);
  }
  
  // 3. 移除不完整的HTML标签（更保守的策略）
  // 只在确实有未闭合标签的情况下才删除
  const lastOpenTag = html.lastIndexOf('<');
  const lastCloseTag = html.lastIndexOf('>');
  if (lastOpenTag > lastCloseTag) {
    // 检查最后一个未闭合标签是否是真正的不完整标签
    const incompleteTag = html.substring(lastOpenTag);
    // 如果包含完整的属性（有引号闭合），可能是正常的，不删除
    // 只有在明显不完整的情况下才删除
    if (!incompleteTag.includes('>') && incompleteTag.length < 100) {
      html = html.substring(0, lastOpenTag);
    }
  }
  
  // 4. 移除 height:100% 设置（保守策略：只处理根div，避免破坏复杂背景样式）
  // 先找到根div（template-root或第一个div），只处理它的style属性
  const rootDivMatch = html.match(/<div\s+([^>]*id\s*=\s*["']template-root["'][^>]*)>/i) || 
                                 html.match(/^<div\s+([^>]*)>/i);
  
  if (rootDivMatch) {
    const rootDivAttrs = rootDivMatch[1];
    const fullRootDiv = rootDivMatch[0];
    
    // 使用更智能的方法查找style属性：找到 style= 后，使用状态机解析引号内容
    const styleAttrStart = rootDivAttrs.search(/style\s*=\s*/i);
    if (styleAttrStart >= 0) {
      let i = styleAttrStart;
      // 跳过 style= 和空白
      while (i < rootDivAttrs.length && rootDivAttrs[i] !== '=') i++;
      i++; // 跳过 =
      while (i < rootDivAttrs.length && /\s/.test(rootDivAttrs[i])) i++;
      
      if (i < rootDivAttrs.length && (rootDivAttrs[i] === '"' || rootDivAttrs[i] === "'")) {
        const quote = rootDivAttrs[i];
        i++; // 跳过开始引号
        const styleStart = i;
        let styleEnd = -1;
        
        // 查找闭合引号（考虑转义）
        while (i < rootDivAttrs.length) {
          if (rootDivAttrs[i] === quote && (i === 0 || rootDivAttrs[i - 1] !== '\\')) {
            styleEnd = i;
            break;
          }
          i++;
        }
        
        if (styleEnd > styleStart) {
          const styleValue = rootDivAttrs.substring(styleStart, styleEnd);
          // 只移除 height:100%，保留所有其他样式
          let cleaned = styleValue.replace(/height\s*:\s*100%\s*;?/gi, '');
          cleaned = cleaned.replace(/;\s*;/g, ';').replace(/^\s*;\s*|\s*;\s*$/g, '');
          
          // 重建属性字符串
          const beforeStyle = rootDivAttrs.substring(0, styleAttrStart);
          const afterStyle = rootDivAttrs.substring(styleEnd + 1);
          const newAttrs = beforeStyle + `style=${quote}${cleaned}${quote}` + afterStyle;
          const newRootDiv = fullRootDiv.replace(rootDivAttrs, newAttrs);
          html = html.replace(fullRootDiv, newRootDiv);
        }
      }
    }
  }
  
  // 5. 清理多余的空白和换行
  html = html.trim();
  
  // 6. 确保至少有一个完整的HTML标签
  if (!html.includes('<') || !html.includes('>')) {
    if (import.meta.env.DEV) {
      console.warn('清理后没有有效的HTML标签，返回空字符串');
    }
    return '';
  }

  // 7. 确保最外层容器有max-height限制（使用更智能的解析，支持包含引号的复杂样式）
  const firstDivMatch = html.match(/^<div\s+([^>]*)>/i);
  if (firstDivMatch) {
    const styleAttr = firstDivMatch[1];
    const fullMatch = firstDivMatch[0]; // 完整的匹配，包括 <div 和属性
    if (styleAttr.includes('style=')) {
      // 使用更智能的正则表达式来匹配style属性，支持嵌套引号
      const styleMatch = styleAttr.match(/style\s*=\s*(["'])((?:(?=(\\?))\3.)*?)\1/i);
      if (styleMatch) {
        const quote = styleMatch[1];
        let styleValue = styleMatch[2];
        // 只移除 height:100%，保留所有其他样式（包括背景渐变、纹理等）
        styleValue = styleValue.replace(/height\s*:\s*100%\s*;?/gi, '');
        styleValue = styleValue.replace(/;\s*;/g, ';').replace(/^\s*;\s*|\s*;\s*$/g, '');
        
        if (!styleValue.includes('max-height')) {
          styleValue += '; max-height: 277mm';
        }
        if (!styleValue.includes('overflow')) {
          styleValue += '; overflow: hidden';
        }
        if (!styleValue.includes('box-sizing')) {
          styleValue += '; box-sizing: border-box';
        }
        // 只替换第一个div标签中的style属性，而不是整个HTML中的第一个style属性
        const newStyleAttr = styleAttr.replace(/style\s*=\s*(["'])((?:(?=(\\?))\3.)*?)\1/i, `style=${quote}${styleValue}${quote}`);
        const newFullMatch = fullMatch.replace(styleAttr, newStyleAttr);
        html = html.replace(fullMatch, newFullMatch);
      }
    } else {
      html = html.replace(/^<div\s+([^>]*)>/i, '<div $1 style="max-height: 277mm; overflow: hidden; box-sizing: border-box;">');
    }
  }

  // 8. 高亮占位符：将 {$字段名} 格式转换为带样式的span标签
  // 使用DOM解析来避免重复包装已经在span标签中的占位符
  try {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    
    // 【修复表格样式丢失】在处理节点之前，先保存所有元素的内联样式和属性
    // 特别是表格元素（table、tr、td、th）的样式和属性
    const preserveElementAttributes = (element: Element) => {
      if (element.nodeType === 1) { // ELEMENT_NODE
        const htmlElement = element as HTMLElement;
        // 保存 style 属性到 data-preserved-style，防止在处理过程中丢失
        const style = htmlElement.getAttribute('style');
        if (style && !htmlElement.hasAttribute('data-preserved-style')) {
          htmlElement.setAttribute('data-preserved-style', style);
        }
        // 递归处理所有子元素
        Array.from(htmlElement.children).forEach(preserveElementAttributes);
      }
    };
    
    // 递归处理所有文本节点
    const processNode = (node: any) => {
      if (node.nodeType === 3) { // TEXT_NODE
        const text = node.textContent || '';
        // 检查是否包含占位符格式，且不在template-field标签内
        const parent = node.parentNode;
        const isInTemplateField = parent && parent.classList && parent.classList.contains('template-field');
        
        if (/\{\$[^}]+\}/.test(text) && !isInTemplateField) {
          const fragment = doc.createDocumentFragment();
          let lastIndex = 0;
          const placeholderRegex = /\{\$([^}]+)\}/g;
          let match;
          
          while ((match = placeholderRegex.exec(text)) !== null) {
            // 添加占位符前的文本
            if (match.index > lastIndex) {
              fragment.appendChild(doc.createTextNode(text.substring(lastIndex, match.index)));
            }
            
            // 创建占位符span
            const span = doc.createElement('span');
            span.className = 'template-field field-block';
            
            const fieldName = match[1].trim();
            span.setAttribute('data-fieldname', fieldName);
            
            // 从可用字段列表中查找对应的字段ID，用于精确匹配
            const matchingField = availableFields.value.find(f => f.name === fieldName);
            if (matchingField) {
              span.setAttribute('data-fieldid', matchingField.id);
            }
            
            // 不添加蓝色背景样式，只保留基本显示样式
            span.setAttribute('style', 'display: inline;');
            
            span.textContent = match[0];
            fragment.appendChild(span);
            
            lastIndex = match.index + match[0].length;
          }
          
          // 添加剩余的文本
          if (lastIndex < text.length) {
            fragment.appendChild(doc.createTextNode(text.substring(lastIndex)));
          }
          
          // 替换原文本节点
          if (node.parentNode) {
            node.parentNode.replaceChild(fragment, node);
          }
        }
      } else if (node.nodeType === 1) { // ELEMENT_NODE
        // 递归处理子节点（但跳过template-field元素）
        if (!node.classList || !node.classList.contains('template-field')) {
          const children = Array.from(node.childNodes);
          children.forEach(processNode);
        }
      }
    };
    
    // 提取所有的 style 标签（解决样式丢失问题）
    const styleTags = doc.querySelectorAll('style');
    let stylesHtml = '';
    styleTags.forEach(style => {
        stylesHtml += style.outerHTML;
    });

    // 【修复表格样式丢失】在处理节点之前，先保存所有元素的内联样式
    const body = doc.body || doc.documentElement;
    if (body) {
      // 先保存所有元素的内联样式
      Array.from(body.querySelectorAll('*')).forEach(preserveElementAttributes);
      
      // 处理body中的所有节点
      const children = Array.from(body.childNodes);
      children.forEach(processNode);
      
      // 【修复表格样式丢失】恢复所有元素的内联样式
      // 确保所有元素的 style 属性都被正确设置，特别是表格元素
      const allElements = body.querySelectorAll('*');
      allElements.forEach((element: Element) => {
        const htmlElement = element as HTMLElement;
        const preservedStyle = htmlElement.getAttribute('data-preserved-style');
        if (preservedStyle) {
          // 如果元素已经有 style 属性，合并；否则直接设置
          const currentStyle = htmlElement.getAttribute('style') || '';
          if (currentStyle && currentStyle !== preservedStyle) {
            // 合并样式：先应用保存的样式，再添加新样式（避免覆盖）
            // 使用更智能的合并方式：如果新样式不包含保存的样式，则合并
            const mergedStyle = preservedStyle + (currentStyle ? '; ' + currentStyle : '');
            htmlElement.setAttribute('style', mergedStyle);
          } else if (!currentStyle) {
            // 如果没有当前样式，直接使用保存的样式
            htmlElement.setAttribute('style', preservedStyle);
          }
          // 移除临时属性
          htmlElement.removeAttribute('data-preserved-style');
        }
        
        // 【额外保护】对于表格元素，确保关键属性被保留
        const tagName = htmlElement.tagName.toLowerCase();
        if (['table', 'tr', 'td', 'th'].includes(tagName)) {
          // 确保表格元素的 border、cellpadding、cellspacing 等属性被保留
          // 这些属性在 innerHTML 中应该会被保留，但为了安全起见，我们显式检查
          const border = htmlElement.getAttribute('border');
          const cellpadding = htmlElement.getAttribute('cellpadding');
          const cellspacing = htmlElement.getAttribute('cellspacing');
          // 如果这些属性存在但丢失了，我们需要从原始 HTML 中恢复
          // 但由于我们已经保存了 style，这些应该已经包含在 HTML 中了
        }
      });
      
      // 将样式拼接到 body 内容前面
      // 使用 innerHTML 获取处理后的内容，此时所有样式应该已经被正确设置
      html = stylesHtml + body.innerHTML;
    }
  } catch (e) {
    // 如果DOM解析失败，使用简单的正则替换（作为兜底方案）
    if (import.meta.env.DEV) {
      console.warn('DOM解析失败，使用正则替换:', e);
    }
    html = html.replace(/\{\$([^}]+)\}/g, (match, fieldNameRaw) => {
      const fieldName = fieldNameRaw.trim();
      // 从可用字段列表中查找对应的字段ID
      const matchingField = availableFields.value.find(f => f.name === fieldName);
      const fieldIdAttr = matchingField ? ` data-fieldid="${matchingField.id}"` : '';
      // 不添加蓝色背景样式
      return `<span class="template-field field-block" data-fieldname="${fieldName}"${fieldIdAttr}>${match}</span>`;
    });
  }

  // 【新增】处理 AI 直接生成的 template-field span 标签
  // AI 可能直接生成 <span class="template-field" data-fieldname="字段名">{$字段名}</span> 格式
  // 这些 span 缺少 data-fieldid 和内联样式，需要补充
  try {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const existingFieldElements = doc.querySelectorAll('.template-field');
    
    existingFieldElements.forEach((element: Element) => {
      const htmlElement = element as HTMLElement;
      const fieldName = htmlElement.getAttribute('data-fieldname');
      
      // 如果没有 data-fieldid，尝试从可用字段列表中查找并添加
      if (fieldName && !htmlElement.getAttribute('data-fieldid')) {
        const matchingField = availableFields.value.find(f => f.name === fieldName);
        if (matchingField) {
          htmlElement.setAttribute('data-fieldid', matchingField.id);
        }
      }
      
      // 不设置蓝色背景样式，保持原有样式或透明
      // 只移除可能存在的蓝色背景相关样式
      const existingStyle = htmlElement.getAttribute('style') || '';
      const cleanedStyle = existingStyle.replace(/background-color\s*:\s*#e0e9ff[^;]*;?/gi, '').replace(/box-shadow\s*:[^;]*;?/gi, '').trim();
      if (cleanedStyle) {
        htmlElement.setAttribute('style', cleanedStyle);
      } else {
        htmlElement.removeAttribute('style');
      }
    });
    
    if (existingFieldElements.length > 0) {
      html = doc.body.innerHTML;
      if (import.meta.env.DEV) {
        console.log(`处理了 ${existingFieldElements.length} 个已存在的 template-field 元素`);
      }
    }
  } catch (e) {
    if (import.meta.env.DEV) {
      console.warn('处理已存在的 template-field 元素失败:', e);
    }
  }

  return html.trim();
};

// 传统模式分类
const traditionalCategories = [
  { id: 'all', label: '全部', icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z" fill="currentColor"/></svg>` },
  { id: 'form', label: '日常表单', icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/></svg>` },
  { id: 'admin', label: '行政人事', icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/></svg>` },
  { id: 'finance', label: '财务单据', icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>` },
];

// 计算属性：两个模式使用相同的分类
const categories = computed(() => {
  return traditionalCategories;
});

// 传统场景列表
const traditionalScenes = [
  { label: '入职申请表', category: 'admin', value: '员工入职申请表，包含姓名、身份证号、部门、职位、入职日期、学历、联系方式、紧急联系人等字段，底部有员工签名和HR审批区域' },
  { label: '请假申请', category: 'admin', value: '请假申请单，包含申请人、部门、请假类型、开始结束日期、请假天数、请假事由、部门主管和HR审批签字' },
  { label: '办公用品领用', category: 'admin', value: '办公用品领用登记表，包含领用日期、部门、领用人、物品名称、规格、数量、用途、管理员签字' },
  { label: '报销单', category: 'finance', value: '费用报销单，包含报销人、部门、报销日期、费用明细表（项目、金额、发票号）、合计金额、审批流程签字区' },
  { label: '工资条', category: 'finance', value: '员工工资条，包含员工姓名、工号、部门、基本工资、绩效、补贴、扣款明细、实发工资、发放日期' },
  { label: '出库单', category: 'form', value: '仓库出库单，包含出库日期、单号、领用部门、物品明细表（名称、规格、数量、单价、金额）、经办人、审批人签字' },
  { label: '采购合同', category: 'form', value: '采购合同，包含甲乙双方信息、采购物品明细表、金额、付款方式、交货日期、违约责任、双方签章区域' },
  { label: '会议签到表', category: 'admin', value: '会议签到表，包含会议主题、时间、地点、主持人、参会人员列表（序号、姓名、部门、签到时间、备注）' },
  { label: '工作证明', category: 'admin', value: '在职证明/工作证明，包含员工姓名、身份证号、部门、职位、入职日期、工作年限、月薪范围（可选）、公司盖章区、开具日期' },
  { label: '离职证明', category: 'admin', value: '离职证明，包含员工姓名、身份证号、部门、职位、入职日期、离职日期、离职原因、公司盖章区' },
  { label: '入库单', category: 'form', value: '仓库入库单，包含入库日期、单号、供应商、物品明细表（名称、规格、数量、单价、金额）、验收人、仓管员签字' },
  { label: '借款申请', category: 'finance', value: '借款申请单，包含申请人、部门、借款金额、借款事由、预计还款日期、审批流程签字区' },
  { label: '加班申请', category: 'admin', value: '加班申请单，包含申请人、部门、加班日期、加班时长、加班事由、部门主管审批签字' },
  { label: '设备领用', category: 'form', value: '设备领用登记表，包含领用日期、领用人、部门、设备名称、设备编号、规格型号、数量、用途、归还日期、管理员签字' },
  { label: '合同签收单', category: 'form', value: '合同签收确认单，包含合同编号、合同名称、甲乙双方、签收人、签收日期、合同份数、备注' },
  { label: '培训签到表', category: 'admin', value: '培训签到表，包含培训主题、培训时间、培训地点、讲师、参训人员列表（序号、姓名、部门、签到时间）' },
];

// 计算属性：两个模式使用相同的场景
const quickPrompts = computed(() => {
  return traditionalScenes;
});

// 监听模式变化，重置选择
watch(selectedMode, () => {
  selectedCategory.value = 'all';
  selectedPrompt.value = '';
});

// 根据分类筛选模板
const filteredPrompts = computed(() => {
  if (selectedCategory.value === 'all') return quickPrompts.value;
  return quickPrompts.value.filter(p => p.category === selectedCategory.value);
});

const selectPrompt = (prompt: { label: string; value: string }) => {
  selectedPrompt.value = prompt.label;
  description.value = prompt.value;
};

// 字段选择方法
const selectAllFields = () => {
  selectedFields.value = availableFields.value.map(f => f.id);
};

const clearAllFields = () => {
  selectedFields.value = [];
};

// 获取选中的字段列表（用于传递给 AI）
const getSelectedFieldsForAI = () => {
  return availableFields.value.filter(f => selectedFields.value.includes(f.id));
};

const goBack = () => {
  router.push('/');
};

const getSceneIcon = (label: string) => {
  const icons: Record<string, string> = {
    '入职申请表': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#6366f1"/><stop offset="100%" style="stop-color:#a855f7"/></linearGradient></defs>
      <rect x="4" y="2" width="16" height="20" rx="2" stroke="url(#grad1)" stroke-width="1.5" fill="none"/>
      <path d="M8 7h8M8 11h8M8 15h5" stroke="url(#grad1)" stroke-width="1.5" stroke-linecap="round"/>
      <circle cx="17" cy="17" r="3" fill="url(#grad1)"/><path d="M16 17h2M17 16v2" stroke="white" stroke-width="1.2" stroke-linecap="round"/>
    </svg>`,
    '采购合同': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#f59e0b"/><stop offset="100%" style="stop-color:#ef4444"/></linearGradient></defs>
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="url(#grad2)" stroke-width="1.5" fill="none"/>
      <path d="M14 2v6h6" stroke="url(#grad2)" stroke-width="1.5" stroke-linecap="round"/>
      <path d="M8 13h8M8 17h6" stroke="url(#grad2)" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`,
    '报销单': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="grad3" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#10b981"/><stop offset="100%" style="stop-color:#06b6d4"/></linearGradient></defs>
      <rect x="3" y="4" width="18" height="16" rx="2" stroke="url(#grad3)" stroke-width="1.5" fill="none"/>
      <circle cx="12" cy="12" r="4" stroke="url(#grad3)" stroke-width="1.5" fill="none"/>
      <path d="M12 10v4M10.5 11.5l1.5 1 1.5-1" stroke="url(#grad3)" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
    '请假申请': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="grad4" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#3b82f6"/><stop offset="100%" style="stop-color:#8b5cf6"/></linearGradient></defs>
      <rect x="3" y="4" width="18" height="18" rx="2" stroke="url(#grad4)" stroke-width="1.5" fill="none"/>
      <path d="M3 10h18" stroke="url(#grad4)" stroke-width="1.5"/>
      <path d="M8 2v4M16 2v4" stroke="url(#grad4)" stroke-width="1.5" stroke-linecap="round"/>
      <circle cx="12" cy="15" r="2" fill="url(#grad4)"/>
    </svg>`,
    '工资条': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="grad5" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#22c55e"/><stop offset="100%" style="stop-color:#16a34a"/></linearGradient></defs>
      <rect x="2" y="6" width="20" height="12" rx="2" stroke="url(#grad5)" stroke-width="1.5" fill="none"/>
      <circle cx="12" cy="12" r="3" stroke="url(#grad5)" stroke-width="1.5" fill="none"/>
      <path d="M6 9v6M18 9v6" stroke="url(#grad5)" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`,
    '出库单': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="grad6" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#f97316"/><stop offset="100%" style="stop-color:#eab308"/></linearGradient></defs>
      <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" stroke="url(#grad6)" stroke-width="1.5" fill="none"/>
      <path d="M3.27 6.96L12 12.01l8.73-5.05M12 22.08V12" stroke="url(#grad6)" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`,
    '会议纪要': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="grad7" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#8b5cf6"/><stop offset="100%" style="stop-color:#d946ef"/></linearGradient></defs>
      <rect x="3" y="3" width="18" height="18" rx="2" stroke="url(#grad7)" stroke-width="1.5" fill="none"/>
      <path d="M7 8h10M7 12h10M7 16h7" stroke="url(#grad7)" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`,
    '保密协议': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="grad8" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#64748b"/><stop offset="100%" style="stop-color:#475569"/></linearGradient></defs>
      <rect x="5" y="11" width="14" height="10" rx="2" stroke="url(#grad8)" stroke-width="1.5" fill="none"/>
      <path d="M7 11V7a5 5 0 0 1 10 0v4" stroke="url(#grad8)" stroke-width="1.5" stroke-linecap="round"/>
      <circle cx="12" cy="16" r="1.5" fill="url(#grad8)"/>
    </svg>`,
    '劳动合同': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="grad9" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#0ea5e9"/><stop offset="100%" style="stop-color:#6366f1"/></linearGradient></defs>
      <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" stroke="url(#grad9)" stroke-width="1.5" fill="none"/>
      <rect x="8" y="2" width="8" height="4" rx="1" stroke="url(#grad9)" stroke-width="1.5" fill="none"/>
      <path d="M9 12h6M9 16h4" stroke="url(#grad9)" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`,
    '租赁协议': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="grad10" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#14b8a6"/><stop offset="100%" style="stop-color:#0d9488"/></linearGradient></defs>
      <path d="M3 21h18M5 21V7l7-4 7 4v14" stroke="url(#grad10)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
      <rect x="9" y="13" width="6" height="8" stroke="url(#grad10)" stroke-width="1.5" fill="none"/>
      <path d="M9 9h6" stroke="url(#grad10)" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`,
    '周报': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="grad11" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#06b6d4"/><stop offset="100%" style="stop-color:#3b82f6"/></linearGradient></defs>
      <rect x="3" y="4" width="18" height="18" rx="2" stroke="url(#grad11)" stroke-width="1.5" fill="none"/>
      <path d="M3 10h18M9 4v6" stroke="url(#grad11)" stroke-width="1.5"/>
      <circle cx="7" cy="14" r="1" fill="url(#grad11)"/><circle cx="12" cy="14" r="1" fill="url(#grad11)"/><circle cx="17" cy="14" r="1" fill="url(#grad11)"/>
      <circle cx="7" cy="18" r="1" fill="url(#grad11)"/><circle cx="12" cy="18" r="1" fill="url(#grad11)"/>
    </svg>`,
    '项目报告': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="grad12" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#f43f5e"/><stop offset="100%" style="stop-color:#e11d48"/></linearGradient></defs>
      <rect x="3" y="3" width="18" height="18" rx="2" stroke="url(#grad12)" stroke-width="1.5" fill="none"/>
      <path d="M12 8v8M8 12v4M16 6v10" stroke="url(#grad12)" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`,
    '数据分析': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="grad13" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#8b5cf6"/><stop offset="100%" style="stop-color:#6366f1"/></linearGradient></defs>
      <circle cx="12" cy="12" r="9" stroke="url(#grad13)" stroke-width="1.5" fill="none"/>
      <path d="M12 12L16 8M12 12V6" stroke="url(#grad13)" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`,
    '活动邀请': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="grad14" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#ec4899"/><stop offset="100%" style="stop-color:#f472b6"/></linearGradient></defs>
      <rect x="3" y="5" width="18" height="16" rx="2" stroke="url(#grad14)" stroke-width="1.5" fill="none"/>
      <path d="M3 9h18" stroke="url(#grad14)" stroke-width="1.5"/>
      <path d="M8 3v4M16 3v4" stroke="url(#grad14)" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`,
    '产品介绍': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="grad15" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#f59e0b"/><stop offset="100%" style="stop-color:#d97706"/></linearGradient></defs>
      <path d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3z" stroke="url(#grad15)" stroke-width="1.5" fill="none"/>
      <path d="M12 12l8-4.5M12 12v9M12 12L4 7.5" stroke="url(#grad15)" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`,
    '公司简介': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="grad16" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#3b82f6"/><stop offset="100%" style="stop-color:#2563eb"/></linearGradient></defs>
      <rect x="4" y="4" width="16" height="16" rx="2" stroke="url(#grad16)" stroke-width="1.5" fill="none"/>
      <path d="M9 21v-6a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v6" stroke="url(#grad16)" stroke-width="1.5"/>
      <path d="M9 10h.01M15 10h.01M9 14h.01M15 14h.01" stroke="url(#grad16)" stroke-width="2" stroke-linecap="round"/>
    </svg>`,
    '证书奖状': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="grad17" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#fcd34d"/><stop offset="100%" style="stop-color:#fbbf24"/></linearGradient></defs>
      <rect x="4" y="3" width="16" height="18" rx="2" stroke="url(#grad17)" stroke-width="1.5" fill="none"/>
      <circle cx="12" cy="9" r="3" stroke="url(#grad17)" stroke-width="1.5"/>
      <path d="M12 14l-2 5 2-1 2 1-2-5" fill="url(#grad17)" stroke="none"/>
    </svg>`,
    // 新增图标
    '办公用品领用': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="grad_office" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#6366f1"/><stop offset="100%" style="stop-color:#8b5cf6"/></linearGradient></defs><rect x="3" y="3" width="18" height="18" rx="2" stroke="url(#grad_office)" stroke-width="1.5" fill="none"/><path d="M9 3v18M15 3v18M3 9h18M3 15h18" stroke="url(#grad_office)" stroke-width="1.5" opacity="0.5"/></svg>`,
    '会议签到表': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="grad_sign" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#10b981"/><stop offset="100%" style="stop-color:#34d399"/></linearGradient></defs><rect x="4" y="4" width="16" height="16" rx="2" stroke="url(#grad_sign)" stroke-width="1.5"/><path d="M9 12l2 2 4-4" stroke="url(#grad_sign)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    '工作证明': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="grad_cert" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#0ea5e9"/><stop offset="100%" style="stop-color:#0284c7"/></linearGradient></defs><rect x="4" y="3" width="16" height="18" rx="2" stroke="url(#grad_cert)" stroke-width="1.5" fill="none"/><circle cx="12" cy="9" r="3" stroke="url(#grad_cert)" stroke-width="1.5"/><path d="M8 16h8M9 19h6" stroke="url(#grad_cert)" stroke-width="1.5" stroke-linecap="round"/></svg>`,
    '离职证明': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="grad_leave" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#64748b"/><stop offset="100%" style="stop-color:#475569"/></linearGradient></defs><rect x="4" y="3" width="16" height="18" rx="2" stroke="url(#grad_leave)" stroke-width="1.5" fill="none"/><path d="M9 9h6M9 13h6M9 17h4" stroke="url(#grad_leave)" stroke-width="1.5" stroke-linecap="round"/><path d="M15 17l2 2 2-2" stroke="url(#grad_leave)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    '入库单': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="grad_in" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#22c55e"/><stop offset="100%" style="stop-color:#16a34a"/></linearGradient></defs><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" stroke="url(#grad_in)" stroke-width="1.5" fill="none"/><path d="M12 12v6M9 15l3 3 3-3" stroke="url(#grad_in)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    '借款申请': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="grad_loan" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#f59e0b"/><stop offset="100%" style="stop-color:#d97706"/></linearGradient></defs><circle cx="12" cy="12" r="9" stroke="url(#grad_loan)" stroke-width="1.5" fill="none"/><path d="M12 7v10M9 9.5c0-1.5 1.5-2.5 3-2.5s3 1 3 2.5-1.5 2-3 2.5c-1.5.5-3 1-3 2.5s1.5 2.5 3 2.5 3-1 3-2.5" stroke="url(#grad_loan)" stroke-width="1.5" stroke-linecap="round"/></svg>`,
    '加班申请': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="grad_ot" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#ec4899"/><stop offset="100%" style="stop-color:#be185d"/></linearGradient></defs><circle cx="12" cy="12" r="9" stroke="url(#grad_ot)" stroke-width="1.5" fill="none"/><path d="M12 7v5l3 3" stroke="url(#grad_ot)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M17 3l2 2M7 3L5 5" stroke="url(#grad_ot)" stroke-width="1.5" stroke-linecap="round"/></svg>`,
    '设备领用': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="grad_device" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#8b5cf6"/><stop offset="100%" style="stop-color:#7c3aed"/></linearGradient></defs><rect x="2" y="3" width="20" height="14" rx="2" stroke="url(#grad_device)" stroke-width="1.5" fill="none"/><path d="M8 21h8M12 17v4" stroke="url(#grad_device)" stroke-width="1.5" stroke-linecap="round"/></svg>`,
    '合同签收单': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="grad_contract" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#14b8a6"/><stop offset="100%" style="stop-color:#0d9488"/></linearGradient></defs><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="url(#grad_contract)" stroke-width="1.5" fill="none"/><path d="M14 2v6h6" stroke="url(#grad_contract)" stroke-width="1.5"/><path d="M9 15l2 2 4-4" stroke="url(#grad_contract)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    '培训签到表': `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="grad_train" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#06b6d4"/><stop offset="100%" style="stop-color:#0891b2"/></linearGradient></defs><path d="M22 10v6M2 10l10-5 10 5-10 5z" stroke="url(#grad_train)" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M6 12v5c0 2 3 3 6 3s6-1 6-3v-5" stroke="url(#grad_train)" stroke-width="1.5" fill="none"/></svg>`
  };

  // 别名映射
  if (label === '项目周报') return icons['周报'];
  if (label === '活动邀请函') return icons['活动邀请'];
  if (label === '荣誉证书') return icons['证书奖状'];
  
  return icons[label] || icons['入职申请表']; // 默认图标
};

const getStepText = () => {
  const steps = ['', '分析需求中...', '设计布局中...', '生成代码中...', '完成'];
  return steps[currentStep.value] || '';
};

const generateTemplate = async () => {
  if (!description.value.trim()) {
    ElMessage.warning('请输入模板描述');
    return;
  }

  // 检查是否选择了字段
  if (availableFields.value.length > 0 && selectedFields.value.length === 0) {
    ElMessage.warning('请至少选择一个字段');
    return;
  }

  // 检查AI生成权限
  const allowed = await checkAndUseFeature('ai_generate');
  if (!allowed) return;

  // 隐藏左侧面板
  showLeftPanel.value = false;
  
  isGenerating.value = true;
  generatedHtml.value = '';
  cleanedHtml.value = ''; // 重置清理后的HTML
  currentStep.value = 1;
  generatingStatus.value = '正在连接AI服务...';
  receivedChars.value = 0;
  
  abortController.value = new AbortController();

  // 设置超时检测（400秒，考虑重试机制，比后端300秒稍长）
  const timeoutId = setTimeout(() => {
    if (isGenerating.value) {
      abortController.value?.abort();
      ElMessage.error('生成超时，请稍后重试。如果问题持续，请尝试简化需求描述。');
      isGenerating.value = false;
    }
  }, 400000); // 400秒超时（考虑重试机制）

  try {
    // 获取当前表格的字段列表
    try {
      const table = await bitable.base.getActiveTable();
      const fieldMetaList = await table.getFieldMetaList();
      availableFields.value = fieldMetaList
        .filter(field => field.name && field.name.trim() !== '') // 只包含有名称的字段
        .map(field => ({
          name: field.name,
          id: field.id,
          type: field.type.toString()
        }));
      if (import.meta.env.DEV) {
        console.log('获取到字段列表:', availableFields.value);
      }
    } catch (error) {
      if (import.meta.env.DEV) {
        console.warn('获取字段列表失败，将不传递字段信息:', error);
      }
      // 即使获取字段失败，也继续生成，只是AI无法使用实际字段名
    }
    
    // 使用用户选中的字段列表
    const fieldsForAI = getSelectedFieldsForAI();

    // 模拟步骤进度
    setTimeout(() => { if (isGenerating.value) currentStep.value = 2; }, 800);
    setTimeout(() => { if (isGenerating.value) currentStep.value = 3; }, 1500);

    // 使用 SSE 流式请求
    generatingStatus.value = '正在发送请求...';
    
    const response = await fetch(`${API_BASE}/api/ai/generate-template-stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        description: description.value,
        mode: selectedMode.value,
        availableFields: fieldsForAI, // 传递字段列表
        feishu_user_id: userStatus.value?.feishu_user_id || ''
      }),
      signal: abortController.value.signal,
    });

    if (!response.ok) {
      let errorMsg = `HTTP error! status: ${response.status}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMsg = errorData.detail;
        }
      } catch (e) {
        // 如果无法解析JSON，保留原始错误信息
      }
      throw new Error(errorMsg);
    }

    generatingStatus.value = '已连接，等待AI响应...';
    
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('无法获取响应流');
    }

    let buffer = '';
    let lastDataTime = Date.now(); // 记录最后一次接收数据的时间
    let lastHeartbeatTime = Date.now(); // 记录最后一次心跳的时间
    const DATA_TIMEOUT = 120000; // 数据接收超时：120秒无数据则断开（考虑心跳间隔和重试）
    let dataTimeoutTriggered = false; // 数据接收超时标志
    let receivedDoneSignal = false; // 是否收到了 [DONE] 信号
    
    // 数据接收超时检测定时器（考虑心跳消息）
    const dataTimeoutId = setInterval(() => {
      const timeSinceLastData = Date.now() - lastDataTime;
      const timeSinceLastHeartbeat = Date.now() - lastHeartbeatTime;
      // 如果超过90秒没有收到任何数据（包括心跳），则超时
      if (timeSinceLastData > DATA_TIMEOUT && timeSinceLastHeartbeat > DATA_TIMEOUT && !dataTimeoutTriggered) {
        if (import.meta.env.DEV) {
          console.warn(`数据接收超时：${DATA_TIMEOUT / 1000}秒未收到任何数据或心跳`);
        }
        dataTimeoutTriggered = true;
        reader.cancel();
        clearInterval(dataTimeoutId);
      }
    }, 5000); // 每5秒检查一次

    try {
      while (true) {
        // 检查数据接收超时标志
        if (dataTimeoutTriggered) {
          throw new Error('数据接收超时，连接可能已中断');
        }
        
        const { done, value } = await reader.read();
        
        if (done) {
          // 连接结束，检查是否收到了 [DONE] 信号
          // 处理剩余的缓冲区内容
          if (buffer) {
            const lines = buffer.split('\n');
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6);
                if (data === '[DONE]') {
                  receivedDoneSignal = true;
                  break;
                }
              }
            }
          }
          
          // 如果没有收到 [DONE] 信号，检查内容是否完整
          if (!receivedDoneSignal) {
            if (import.meta.env.DEV) {
              console.warn('连接结束但未收到 [DONE] 信号，检查内容完整性...');
            }
            // 如果内容足够长，认为可能已经完成（连接中断但内容完整）
            if (generatedHtml.value && generatedHtml.value.trim().length >= 1000) {
              if (import.meta.env.DEV) {
                console.log('内容足够长，认为生成已完成');
              }
              receivedDoneSignal = true; // 假设已完成
            } else {
              // 内容不够，可能是不完整的中断
              throw new Error('连接中断，生成可能不完整。请重试。');
            }
          }
          break;
        }

        // 更新最后接收数据的时间
        lastDataTime = Date.now();

        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;
        
        // 处理 SSE 数据
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              receivedDoneSignal = true; // 标记已收到 [DONE] 信号
              clearInterval(dataTimeoutId); // 清除数据接收超时检测
              
              // 验证生成的HTML内容
              if (!generatedHtml.value || generatedHtml.value.trim().length < 200) {
                throw new Error('生成的模板内容过短或不完整，请重试');
              }
              
              // 检查是否包含template-root或div标签
              if (!generatedHtml.value.includes('<div') && !generatedHtml.value.includes('<DIV')) {
                throw new Error('生成的模板缺少必需的HTML结构，请重试');
              }
              
              // 检查是否包含占位符或文本内容
              const textContent = generatedHtml.value.replace(/<[^>]+>/g, '').trim();
              const hasPlaceholder = /\{\$[^}]+\}/.test(generatedHtml.value);
              if (textContent.length < 50 && !hasPlaceholder) {
                throw new Error('生成的模板内容过少，请重试或调整描述');
              }
              
              currentStep.value = 4;
              break;
            }
            try {
              const parsed = JSON.parse(data);
              // 处理心跳消息（更新心跳时间，并显示状态）
              if (parsed.type === 'heartbeat') {
                lastHeartbeatTime = Date.now(); // 更新心跳时间
                lastDataTime = Date.now(); // 心跳也算作数据接收
                generatingStatus.value = parsed.message || '正在生成模板...';
                if (import.meta.env.DEV) {
                  console.log('收到心跳:', parsed.message);
                }
                continue;
              }
              // 处理重试消息
              if (parsed.type === 'retry') {
                lastHeartbeatTime = Date.now(); // 更新心跳时间
                lastDataTime = Date.now(); // 重试消息也算作数据接收
                generatingStatus.value = parsed.message || '正在重试生成...';
                ElMessage.info(parsed.message || '连接中断，正在自动重试...');
                if (import.meta.env.DEV) {
                  console.log('收到重试消息:', parsed.message);
                }
                continue;
              }
              if (parsed.content) {
                lastDataTime = Date.now(); // 更新最后接收时间
                lastHeartbeatTime = Date.now(); // 内容也算作心跳
                const content = parsed.content;
                receivedChars.value += content.length;
                
                // 估算进度（假设平均模板约2000-3000字符）
                const estimatedTotal = 2500;
                const progressPercent = Math.min(95, Math.floor((receivedChars.value / estimatedTotal) * 100));
                generatingStatus.value = `正在生成... (${progressPercent}%, 已接收 ${receivedChars.value} 字符)`;
                if (import.meta.env.DEV) {
                  console.log(`收到内容片段: ${content.length} 字符，累计: ${receivedChars.value} 字符`);
                }
                
                // 直接添加到 generatedHtml，清理由 computed 属性处理
                generatedHtml.value += content;
              }
              if (parsed.error) {
                clearInterval(dataTimeoutId); // 清除数据接收超时检测
                generatingStatus.value = `生成失败: ${parsed.error}`;
                throw new Error(parsed.error);
              }
            } catch (e) {
              // 如果不是 JSON，直接添加内容
              if (data && data !== '[DONE]') {
                lastDataTime = Date.now(); // 更新最后接收时间
                receivedChars.value += data.length;
                generatingStatus.value = `正在生成... (已接收 ${receivedChars.value} 字符)`;
                if (import.meta.env.DEV) {
                  console.log(`收到非JSON内容: ${data.length} 字符`);
                }
                generatedHtml.value += data;
              }
            }
          }
        }
      }
    } finally {
      clearInterval(dataTimeoutId); // 确保清除数据接收超时检测
    }

    // 生成结束，执行完整清理
    // 再次确认收到了 [DONE] 信号或内容足够完整
    if (!receivedDoneSignal) {
      // 如果内容足够长，认为可能已经完成
      if (generatedHtml.value && generatedHtml.value.trim().length >= 1000) {
        if (import.meta.env.DEV) {
          console.log('未收到 [DONE] 但内容足够长，认为生成已完成');
        }
        receivedDoneSignal = true;
      } else {
        throw new Error('生成未完成，请重试');
      }
    }
    
    if (import.meta.env.DEV) {
      console.log(`生成完成，共接收 ${receivedChars.value} 字符`);
    }
    generatingStatus.value = '正在清理和优化模板...';
    
    // 使用 nextTick 确保在下一个事件循环中执行清理，避免阻塞UI
    await new Promise(resolve => setTimeout(resolve, 0));
    cleanedHtml.value = performFullClean(generatedHtml.value);
    
    generatingStatus.value = '生成完成！';
    currentStep.value = 4;
    isGenerating.value = false;
    clearTimeout(timeoutId); // 清除超时定时器
    ElMessage.success('模板生成完成！');

  } catch (error: any) {
    clearTimeout(timeoutId); // 清除超时定时器
    console.error('生成过程出错:', error);
    generatingStatus.value = `生成失败: ${error.message || '未知错误'}`;
    isGenerating.value = false;
    if (error.name === 'AbortError') {
      ElMessage.info('已停止生成');
    } else {
      console.error('生成失败:', error);
      // 根据错误类型提供更友好的提示
      let errorMessage = error.message || '未知错误';
      if (errorMessage.includes('timeout') || errorMessage.includes('超时') || errorMessage.includes('数据接收超时')) {
        errorMessage = '生成超时，请稍后重试。如果问题持续，请尝试简化需求描述。';
      } else if (errorMessage.includes('fetch') || errorMessage.includes('network')) {
        errorMessage = '网络连接失败，请检查网络连接后重试。';
      } else if (errorMessage.includes('aborted') || errorMessage.includes('canceled')) {
        errorMessage = '请求已取消';
        ElMessage.info(errorMessage);
        return; // 取消操作不需要显示错误
      }
      ElMessage.error('生成失败: ' + errorMessage);
    }
  } finally {
    isGenerating.value = false;
    abortController.value = null;
    refreshStatus();
  }
};

const stopGenerate = () => {
  if (abortController.value) {
    abortController.value.abort();
  }
};

const regenerate = () => {
  generateTemplate();
};

const saveTemplate = async () => {
  try {
    const { value: templateName } = await ElMessageBox.prompt(
      '请输入模板名称',
      '保存模板',
      {
        confirmButtonText: '保存',
        cancelButtonText: '取消',
        inputValue: '', // 用户必须手动输入
        inputPlaceholder: '例如：员工入职申请表',
        inputValidator: (value) => {
          if (!value || value.trim().length === 0) {
            return '请输入模板名称';
          }
          return true;
        }
      }
    );

    await templateApi.create({
      name: templateName,
      content: cleanGeneratedHtml.value, // 使用清理后的HTML
      template_type: 'ai' // 标记为AI生成的模板
    });

    ElMessage.success('模板已保存到模板库');
    // 跳转到模板库的AI模板分类，并显示提示
    router.push({ path: '/templates', query: { category: 'ai' } });
    
    // 延迟显示提示，确保路由跳转完成
    setTimeout(() => {
      ElMessage.info({
        message: '已自动切换到"AI模版"分类，您可以在这里找到刚才保存的模板',
        duration: 5000,
        showClose: true
      });
    }, 500);

  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('保存失败:', error);
      // axios 错误的响应数据在 error.response.data
      let errorMsg = '保存失败';
      if (error.response && error.response.data && error.response.data.detail) {
        errorMsg = error.response.data.detail;
      } else if (error.message) {
        errorMsg = error.message;
      }
      ElMessage.error(errorMsg);
    }
  }
};

// 切换预览模式
const togglePreviewMode = async () => {
  if (!isPreviewMode.value) {
    // 切换到预览模式：需要获取记录数据
    try {
      await loadRecordData();
      isPreviewMode.value = true;
    } catch (error) {
      console.error('加载记录数据失败:', error);
      ElMessage.error('无法加载记录数据，请确保已选择记录');
    }
  } else {
    // 切换到编辑模式
    isPreviewMode.value = false;
  }
};

// 加载记录数据
const loadRecordData = async () => {
  try {
    const table = await bitable.base.getActiveTable();
    const view = await table.getActiveView();
    const recordIdList = await view.getVisibleRecordIdList();
    
    if (recordIdList.length === 0) {
      ElMessage.warning('当前视图没有记录，请先添加记录');
      return;
    }
    
    // 获取第一条记录的ID
    const firstRecordId = recordIdList[0];
    if (!firstRecordId) {
      ElMessage.warning('无法获取记录ID');
      return;
    }
    
    const fields = await table.getFieldMetaList();
    
    // 构建记录数据
    const fieldsData: Record<string, any> = {};
    for (const field of fields) {
      try {
        const value = await table.getCellValue(firstRecordId, field.id);
        fieldsData[field.id] = value;
      } catch (e) {
        if (import.meta.env.DEV) {
          console.warn(`获取字段 ${field.name} 的值失败:`, e);
        }
      }
    }
    
    recordData.value = {
      fields: fieldsData
    };
    
    // 同时更新可用字段列表
    availableFields.value = fields
      .filter(field => field.name && field.name.trim() !== '')
      .map(field => ({
        name: field.name,
        id: field.id,
        type: field.type.toString()
      }));
    
  } catch (error) {
    console.error('加载记录数据失败:', error);
    throw error;
  }
};

// 渲染预览HTML（保持占位符显示）
const renderPreviewHtml = (html: string): string => {
  // 预览模式下保持占位符显示，字段映射功能在 EditorPage 中处理
  return html;
};
</script>

<style scoped>
.ai-generate-page {
  min-height: 100vh;
  background: #f8fafc;
  background-image: 
    radial-gradient(ellipse 80% 50% at 50% -20%, rgba(120, 119, 198, 0.15), transparent),
    radial-gradient(ellipse 60% 40% at 100% 100%, rgba(139, 92, 246, 0.08), transparent);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* 装饰性光斑 */
.ai-generate-page::before,
.ai-generate-page::after {
  content: '';
  position: absolute;
  width: 500px;
  height: 500px;
  border-radius: 50%;
  filter: blur(80px);
  z-index: 0;
  pointer-events: none;
  opacity: 0.6;
}

.ai-generate-page::before {
  top: -100px;
  right: -100px;
  background: radial-gradient(circle, #fbcfe8 0%, rgba(251, 207, 232, 0) 70%);
  animation: float 20s ease-in-out infinite;
}

.ai-generate-page::after {
  bottom: -100px;
  left: -100px;
  background: radial-gradient(circle, #c7d2fe 0%, rgba(199, 210, 254, 0) 70%);
  animation: float 20s ease-in-out infinite reverse;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, 20px); }
}

/* 顶部导航 */
.top-nav {
  height: 64px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.5);
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 16px;
  position: relative;
  z-index: 10;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.nav-back {
  width: 36px;
  height: 36px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  background: rgba(255, 255, 255, 0.5);
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-back:hover {
  background: white;
  color: #334155;
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.nav-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: -0.01em;
}

.nav-title svg {
  color: #8b5cf6;
  filter: drop-shadow(0 2px 4px rgba(139, 92, 246, 0.2));
}

.nav-badge {
  padding: 4px 10px;
  background: linear-gradient(135deg, #8b5cf6 0%, #d946ef 100%);
  color: white;
  font-size: 11px;
  font-weight: 700;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 6px rgba(139, 92, 246, 0.25);
}

/* 工作区 */
.workspace {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
  z-index: 5;
  padding: 20px;
  gap: 20px;
  transition: gap 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 左侧面板 */
.left-panel {
  width: 400px;
  flex-shrink: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  padding: 20px;
  gap: 16px;
  box-shadow: 0 4px 24px -4px rgba(0, 0, 0, 0.06), 0 0 1px rgba(0, 0, 0, 0.08);
  animation: fade-slide-up 0.5s cubic-bezier(0.16, 1, 0.3, 1);
  overflow-y: auto;
}

/* 面板标题栏 */
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: -4px -4px 8px -4px;
  padding: 12px 16px;
  border-bottom: 1px solid #f1f5f9;
  background: #fafbfc;
  border-radius: 4px 4px 0 0;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.panel-title svg {
  color: #64748b;
  flex-shrink: 0;
}

.panel-hide-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  border: none;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.panel-hide-btn:hover {
  background: #f1f5f9;
  color: #334155;
}

.panel-hide-btn:active {
  background: #e2e8f0;
  transform: scale(0.95);
}

.panel-hide-btn:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

.panel-hide-btn svg {
  width: 16px;
  height: 16px;
}

/* 左侧面板过渡动画 */
.slide-fade-enter-active {
  transition: opacity 0.35s cubic-bezier(0.4, 0, 0.2, 1),
              transform 0.35s cubic-bezier(0.4, 0, 0.2, 1),
              width 0.35s cubic-bezier(0.4, 0, 0.2, 1),
              margin 0.35s cubic-bezier(0.4, 0, 0.2, 1),
              padding 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-leave-active {
  transition: opacity 0.35s cubic-bezier(0.4, 0, 0.2, 1),
              transform 0.35s cubic-bezier(0.4, 0, 0.2, 1),
              width 0.35s cubic-bezier(0.4, 0, 0.2, 1),
              margin 0.35s cubic-bezier(0.4, 0, 0.2, 1),
              padding 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(-100%);
  width: 0 !important;
  margin-right: 0 !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
  overflow: hidden;
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-100%);
  width: 0 !important;
  margin-right: 0 !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
  overflow: hidden;
}

.slide-fade-enter-to,
.slide-fade-leave-from {
  opacity: 1;
  transform: translateX(0);
}

/* 模式切换 - 分段控制器风格 */
.mode-toggle {
  display: flex;
  background: #f1f5f9;
  padding: 4px;
  border-radius: 4px;
  margin-bottom: 20px;
  width: 100%;
}

.mode-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 0; /* 上下 padding，左右由 flex 控制 */
  background: transparent;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.mode-btn:hover {
  background: rgba(255, 255, 255, 0.6);
}

.mode-btn.active {
  background: white;
  color: #0f172a;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
  font-weight: 600;
}

/* 选中状态下图标颜色更明显 */
.mode-btn.active svg {
  stroke: #6366f1;
  stroke-width: 2.5;
}

.mode-btn svg {
  width: 18px;
  height: 18px;
  transition: all 0.2s;
}

/* 样式选择器 */
.style-selector {
  margin-bottom: 16px;
}

.style-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 6px;
}

.style-card {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 26px;
  padding: 0 2px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.style-card:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  color: #334155;
}

.style-card.active {
  background: #f5f3ff;
  border-color: #8b5cf6;
  color: #7c3aed;
  font-weight: 600;
  box-shadow: 0 0 0 1px rgba(139, 92, 246, 0.5);
}

.style-name {
  font-size: 11px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transform: scale(0.95); /* 微调紧凑度 */
}


/* 分类标签 */
.category-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.category-tab {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px; /* 减小内边距 */
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 4px; /* 减小圆角 */
  font-size: 12px; /* 减小字号 */
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
  height: 28px; /* 固定高度使其更紧凑 */
}

.category-tab:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #475569;
}

.category-tab.active {
  background: #eff6ff;
  border-color: #3b82f6; /* 选中时使用蓝色边框 */
  color: #2563eb;
  font-weight: 500;
}

/* 调整图标大小 */
.category-tab .cat-icon svg {
  width: 14px;
  height: 14px;
}

.cat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.cat-icon svg {
  width: 14px;
  height: 14px;
}

/* 风格选择 */
.style-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 6px;
}

.style-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px 2px; /* 极致内边距 */
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  height: 48px; /* 固定极小高度 */
}

.style-card:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  transform: translateY(-1px); /* 微动 */
}

.style-card.active {
  background: white;
  border-color: #8b5cf6;
  box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.1);
}

.style-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.style-name {
  font-size: 11px;
  font-weight: 600;
  color: #334155;
  line-height: 1;
}

.style-desc {
  display: none; /* 隐藏描述文字以最大化节省空间 */
}

@keyframes fade-slide-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.panel-section {
  display: flex;
  flex-direction: column;
}

.panel-section.flex-1 {
  flex: 1;
  min-height: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-label {
  font-size: 14px;
  font-weight: 700;
  color: #334155;
  display: flex;
  align-items: center;
  gap: 6px;
}

.section-label::before {
  content: '';
  width: 4px;
  height: 14px;
  background: linear-gradient(to bottom, #8b5cf6, #d946ef);
  border-radius: 4px;
}

.section-hint {
  font-size: 12px;
  color: #94a3b8;
}

/* 字段选择 */
.field-select-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.field-action-btn {
  padding: 4px 12px;
  font-size: 12px;
  color: #64748b;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.field-action-btn:hover {
  background: #e2e8f0;
  color: #334155;
}

.field-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  max-height: 120px;
  overflow-y: auto;
  padding: 4px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 6px;
}

.field-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 12px;
}

.field-item:hover {
  border-color: #8b5cf6;
  background: #faf5ff;
}

.field-item.selected {
  border-color: #8b5cf6;
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
}

.field-checkbox {
  width: 14px;
  height: 14px;
  accent-color: #8b5cf6;
  cursor: pointer;
}

.field-name {
  color: #334155;
  white-space: nowrap;
}

/* 场景卡片 */
.scene-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
}

.scene-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 4px 6px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.scene-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px -4px rgba(100, 116, 139, 0.15);
  border-color: #c7d2fe;
}

.scene-card.active {
  background: linear-gradient(135deg, #f5f3ff 0%, #fdf4ff 100%);
  border-color: #a78bfa;
  box-shadow: 0 2px 8px -2px rgba(139, 92, 246, 0.2);
}

.scene-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.scene-icon :deep(svg) {
  width: 18px;
  height: 18px;
}

.scene-card:hover .scene-icon {
  transform: scale(1.1);
}

.scene-name {
  font-size: 10px;
  color: #475569;
  text-align: center;
  line-height: 1.2;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.scene-card.active .scene-name {
  color: #6d28d9;
  font-weight: 600;
}

/* 输入区域 */
.input-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  position: relative;
}

.desc-textarea {
  flex: 1;
  min-height: 160px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.5);
  border: 2px solid transparent;
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.6;
  resize: none;
  font-family: inherit;
  color: #334155;
  transition: all 0.3s;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
}

.desc-textarea:focus {
  outline: none;
  background: white;
  box-shadow: 0 10px 15px -3px rgba(139, 92, 246, 0.1);
}

.desc-textarea:disabled {
  background: rgba(241, 245, 249, 0.5);
  color: #94a3b8;
  cursor: not-allowed;
}

.desc-textarea::placeholder {
  color: #94a3b8;
}

.input-meta {
  position: absolute;
  bottom: 16px;
  right: 16px;
  pointer-events: none;
}

.word-count {
  font-size: 11px;
  color: #cbd5e1;
  background: rgba(255, 255, 255, 0.8);
  padding: 2px 6px;
  border-radius: 4px;
}

/* 操作按钮 */
.action-bar {
  padding-top: 12px;
}

.action-btn {
  width: 100%;
  height: 52px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* AI 生成按钮 - 流光效果 */
.ai-generate-btn-wrapper {
  position: relative;
  display: block;
  width: 100%;
  padding: 3px;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.ai-generate-btn-wrapper::before {
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
  animation: ai-btn-rotate 3s linear infinite;
}

.ai-generate-btn-wrapper .glow-shadow {
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

.ai-generate-btn-wrapper:hover .glow-shadow {
  opacity: 0.5;
}

.ai-generate-btn-content {
  position: relative;
  background: linear-gradient(135deg, #1f2937 0%, #4b5563 50%, #f9fafb 100%);
  padding: 14px 24px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  z-index: 1;
  transition: background 0.3s ease;
}

.ai-generate-btn-wrapper:hover .ai-generate-btn-content {
  background: linear-gradient(135deg, #374151 0%, #6b7280 50%, #ffffff 100%);
}

.ai-generate-btn-content .btn-text {
  font-weight: 600;
  font-size: 16px;
  color: white;
}

.ai-generate-icon {
  width: 20px;
  height: 20px;
  fill: #8b5cf6;
  filter: drop-shadow(0 0 4px #8b5cf6);
  animation: ai-icon-pulse 2s ease-in-out infinite;
}

.ai-generate-btn-content::after {
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

.ai-generate-btn-wrapper:hover .ai-generate-btn-content::after {
  left: 100%;
  transition: 0.7s;
}

.ai-generate-btn-wrapper:active {
  transform: scale(0.96);
}

/* 禁用状态 */
.ai-generate-btn-wrapper.disabled {
  cursor: not-allowed;
  pointer-events: none;
}

.ai-generate-btn-wrapper.disabled::before {
  background: #cbd5e1;
  animation: none;
}

.ai-generate-btn-wrapper.disabled .glow-shadow {
  display: none;
}

.ai-generate-btn-wrapper.disabled .ai-generate-btn-content {
  background: #e2e8f0;
}

.ai-generate-btn-wrapper.disabled .ai-generate-btn-content .btn-text {
  color: #94a3b8;
}

.ai-generate-btn-wrapper.disabled .ai-generate-icon {
  fill: #94a3b8;
  filter: none;
  animation: none;
}

@keyframes ai-btn-rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes ai-icon-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(0.9); }
}

/* 进度条 */
.progress-bar {
  margin-top: 16px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 4px;
}

.progress-track {
  height: 6px;
  background: rgba(226, 232, 240, 0.6);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8b5cf6, #d946ef);
  border-radius: 4px;
  transition: width 0.3s ease;
  position: relative;
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
  transform: translateX(-100%);
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  100% { transform: translateX(100%); }
}

.progress-text {
  display: block;
  margin-top: 8px;
  font-size: 12px;
  color: #64748b;
  text-align: center;
  font-weight: 500;
}

/* 预览区域 */
.preview-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 4px 24px -4px rgba(0, 0, 0, 0.06), 0 0 1px rgba(0, 0, 0, 0.08);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.preview-area.full-width {
  margin-left: 0;
}

.preview-toolbar {
  height: 52px;
  background: #fafbfc;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.toolbar-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #475569;
}

.toolbar-title svg {
  color: #8b5cf6;
}

.toolbar-actions {
  display: flex;
  gap: 10px;
}

.tool-btn {
  height: 34px;
  padding: 0 16px;
  border: 1px solid rgba(203, 213, 225, 0.5);
  background: rgba(255, 255, 255, 0.8);
  border-radius: 4px;
  font-size: 13px;
  color: #475569;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
  font-weight: 500;
}

.tool-btn:hover {
  background: white;
  border-color: #cbd5e1;
  transform: translateY(-1px);
}

.tool-btn.active {
  background: #0f172a !important;
  border-color: #0f172a !important;
  color: white !important;
}

.tool-btn.primary {
  background: #1e293b;
  border-color: #1e293b;
  color: white;
  box-shadow: 0 4px 12px rgba(30, 41, 59, 0.2);
}

.tool-btn.primary:hover {
  background: #334155;
  transform: translateY(-1px);
}

/* 预览画布 */
.preview-canvas {
  flex: 1;
  min-height: 0;
  padding: 20px;
  overflow: auto;
  background: 
    linear-gradient(rgba(255,255,255,0.3) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.3) 1px, transparent 1px);
  background-size: 20px 20px;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

/* 空状态 */
.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.empty-icon {
  width: 96px;
  height: 96px;
  background: white;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
  margin-bottom: 24px;
  position: relative;
}

.empty-icon::after {
  content: '';
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  border-radius: 4px;
  background: linear-gradient(135deg, #f0f9ff, #fdf2f8);
  z-index: -1;
  opacity: 0.5;
}

.empty-icon svg {
  color: #94a3b8;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.empty-title {
  font-size: 18px;
  font-weight: 700;
  color: #334155;
  margin: 0 0 8px 0;
}

.empty-desc {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

/* 加载状态 */
.loading-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.loading-animation {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  padding: 16px 24px;
  background: white;
  border-radius: 4px;
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.1);
}

.loading-dot {
  width: 12px;
  height: 12px;
  background: #8b5cf6;
  border-radius: 50%;
  animation: loading-bounce 1.4s ease-in-out infinite;
}

.loading-dot:nth-child(1) { animation-delay: 0s; background: #8b5cf6; }
.loading-dot:nth-child(2) { animation-delay: 0.2s; background: #d946ef; }
.loading-dot:nth-child(3) { animation-delay: 0.4s; background: #ec4899; }

@keyframes loading-bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

.loading-text {
  font-size: 15px;
  color: #64748b;
  margin: 0;
  font-weight: 500;
}

/* 文档预览 */
.preview-document {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  overflow: visible;
}

/* A4容器样式 */
.a4-container {
  width: 210mm;
  max-width: 210mm;
  min-height: 100px; /* 最小高度，防止空内容时太矮 */
  max-height: 297mm; /* 最大 A4 高度 */
  margin: 0 auto;
  background: transparent; /* 透明背景，显示生成内容的背景 */
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  overflow: auto; /* 超出时可滚动 */
  box-sizing: border-box;
  transform-origin: top center;
  position: relative;
}

/* 响应式适配：在小屏幕上缩放预览内容 */
@media (max-width: 1200px) {
  .a4-container {
    transform: scale(0.85);
    width: 210mm; /* 保持原始宽度，通过transform缩放 */
  }
}

@media (max-width: 900px) {
  .a4-container {
    transform: scale(0.7);
    width: 210mm; /* 保持原始宽度，通过transform缩放 */
  }
}

/* 超小屏幕：进一步缩放 */
@media (max-width: 600px) {
  .a4-container {
    transform: scale(0.5);
    width: 210mm;
  }
}


/* 占位符样式 - 不使用蓝色背景，保持模板原样 */
.a4-container :deep(.template-field.field-block) {
  display: inline;
}

/* 深度选择器：处理生成的HTML内容 */
/* 移除全局 max-width: 100% 限制，以免破坏绝对定位布局 */
.a4-container :deep(img) {
  max-width: 100%;
  height: auto;
  display: block;
}

.a4-container :deep(table) {
  max-width: 100%;
  table-layout: auto;
  width: 100% !important;
  border-collapse: collapse;
}

/* 仅限制非绝对定位的直接子元素，或者是为了防止文本溢出 */
.a4-container :deep(p),
.a4-container :deep(h1),
.a4-container :deep(h2),
.a4-container :deep(h3),
.a4-container :deep(ul),
.a4-container :deep(ol) {
  max-width: 100%;
  box-sizing: border-box;
}



/* 确保所有div元素不超出容器 */


/* 支持flex布局 */
.a4-container :deep([style*="display: flex"]),
.a4-container :deep([style*="display:flex"]) {
  display: flex !important;
}

/* 支持grid布局 */
.a4-container :deep([style*="display: grid"]),
.a4-container :deep([style*="display:grid"]) {
  display: grid !important;
}

/* 支持渐变背景 - 移除覆盖规则，让生成的HTML背景样式正常显示 */
/* 不再使用 background-image: inherit，避免覆盖生成的背景样式 */

/* 支持圆角和阴影 */
.a4-container :deep([style*="border-radius"]),
.a4-container :deep([style*="box-shadow"]) {
  border-radius: inherit;
  box-shadow: inherit;
}

/* 确保创意元素正确显示 */
/* 确保内容不溢出 A4 容器，但允许内部元素绝对定位 */
.a4-container {
  overflow: hidden; 
}

/* 处理flex布局，确保不超出 */
.a4-container :deep([style*="display: flex"]),
.a4-container :deep([style*="display:flex"]) {
  max-width: 100%;
  flex-wrap: wrap;
}

/* 处理grid布局，确保不超出 */
.a4-container :deep([style*="display: grid"]),
.a4-container :deep([style*="display:grid"]) {
  max-width: 100%;
}

/* 打印样式优化 */
@media print {
  .preview-canvas {
    padding: 0;
    background: white;
  }
  
  .preview-document {
    box-shadow: none;
  }
  
  .a4-container {
    max-width: 210mm;
    width: 210mm;
    margin: 0;
    box-shadow: none;
    border-radius: 0;
    page-break-after: always;
    /* 打印时不缩放 */
    transform: none !important;
  }
}

.cursor-blink {
  display: inline;
  color: #8b5cf6;
  font-weight: bold;
  animation: cursor-blink 1s step-end infinite;
}

@keyframes cursor-blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* 工具栏按钮激活状态 */
.tool-btn.active {
  background: #36a1ff;
  color: white;
}

.tool-btn.active:hover {
  background: #2d8ce6;
}
</style>
