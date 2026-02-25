<template>
  <div class="signature-page">
    <div class="signature-container">
      <!-- 加载中 -->
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>正在加载签名请求...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-state">
        <div class="error-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>
        </div>
        <h2>{{ error }}</h2>
        <p>请联系发送方获取新的签名链接</p>
      </div>

      <!-- 已签名状态 -->
      <div v-else-if="signatureData?.status === 'signed'" class="signed-state">
        <div class="success-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>
        </div>
        <h2>签名已完成</h2>
        <p>签名人：{{ signatureData.signer_name }}</p>
        <p>签名时间：{{ formatDate(signatureData.signed_at) }}</p>
        <div class="signature-preview">
          <img :src="signatureData.signature_data" alt="签名" />
        </div>
      </div>

      <!-- 待签名状态 -->
      <div v-else-if="signatureData" class="pending-state">
        <div class="header">
          <h1>电子签名</h1>
          <p class="subtitle">{{ signatureData.document_title || '请在下方完成签名' }}</p>
        </div>

        <div class="signer-info">
          <div class="info-item">
            <span class="label">签名人</span>
            <span class="value">{{ signatureData.signer_name }}</span>
          </div>
          <div class="info-item">
            <span class="label">有效期至</span>
            <span class="value">{{ formatDate(signatureData.expires_at) }}</span>
          </div>
        </div>

        <!-- 文档预览 -->
        <div v-if="signatureData.document_html" class="document-preview">
          <div class="preview-header">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
            <span>文档预览</span>
            <button class="btn-toggle" @click="showPreview = !showPreview">
              {{ showPreview ? '收起' : '展开' }}
            </button>
          </div>
          <div v-if="showPreview" class="preview-viewport">
            <iframe
              ref="previewIframeRef"
              class="preview-iframe"
              sandbox="allow-same-origin"
              frameborder="0"
              scrolling="no"
            ></iframe>
          </div>
        </div>

        <div class="signature-area">
          <div class="canvas-wrapper">
            <canvas 
              ref="canvasRef"
              @mousedown="startDrawing"
              @mousemove="draw"
              @mouseup="stopDrawing"
              @mouseleave="stopDrawing"
              @touchstart.prevent="handleTouchStart"
              @touchmove.prevent="handleTouchMove"
              @touchend="stopDrawing"
            ></canvas>
            <div v-if="isEmpty" class="placeholder">
              请在此处签名
            </div>
          </div>
        </div>

        <div class="actions">
          <button class="btn btn-secondary" @click="clearCanvas">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
            清除
          </button>
          <button class="btn btn-primary" @click="submitSignature" :disabled="isEmpty || isSubmitting">
            <span v-if="isSubmitting">提交中...</span>
            <span v-else>确认签名</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue';
import { useRoute } from 'vue-router';
import { signatureApi, type SignatureData } from '@/api/signature';

const route = useRoute();

const isLoading = ref(true);
const error = ref('');
const signatureData = ref<SignatureData | null>(null);
const isSubmitting = ref(false);
const showPreview = ref(true);

const previewIframeRef = ref<HTMLIFrameElement | null>(null);

/**
 * 将编辑器 HTML 写入 iframe，注入编辑器页面样式，实现真实纸张预览。
 */
const renderPreviewIframe = () => {
  const iframe = previewIframeRef.value;
  if (!iframe || !signatureData.value?.document_html) return;

  const html = signatureData.value.document_html;

  // 判断是否包含编辑器页面结构，如果没有则自动包裹一层纸张容器
  const hasPageStructure = html.includes('template-page-content');
  const bodyContent = hasPageStructure
    ? html
    : `<div id="template-root"><div class="template-page-content">${html}</div></div>`;

  const iframeDoc = `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: sans-serif;
    font-size: 14px;
    color: #1e293b;
    background: #f1f5f9;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 8px 0;
  }
  #template-root {
    width: 100% !important;
    min-height: auto !important;
    padding: 0 !important;
    margin: 0 !important;
    background: transparent !important;
  }
  .template-page-content {
    width: 210mm;
    min-height: 297mm;
    background: #fff;
    padding: 10mm;
    box-sizing: border-box;
    margin: 8px auto;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1);
    position: relative;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
  .template-page-content img { max-width: 100%; height: auto; }
  .template-page-content table { max-width: 100%; border-collapse: collapse; }
  .template-page-content td, .template-page-content th { border: 1px solid #94a3b8; padding: 0.5rem; }
  .template-page-content th { background: #e2e8f0; font-weight: 600; }
  .template-field.is-mapped { display: none !important; }
  .mapped-shadow { display: inline; line-height: inherit; }
  p.mapped-shadow { display: block; }
  .template-field { padding: 0 2px; border-radius: 2px; color: #1e40af; background: #dbeafe; }
  /* 隐藏编辑器辅助元素 */
  .mce-pagebreak, .page-break-visual { display: none; }
</style>
</head>
<body>${bodyContent}</body>
</html>`;

  // 写入 iframe
  const doc = iframe.contentDocument;
  if (!doc) return;
  doc.open();
  doc.write(iframeDoc);
  doc.close();

  // 等待渲染完成后自适应高度
  const adjustHeight = () => {
    if (!iframe.contentDocument?.body) return;
    const contentHeight = iframe.contentDocument.body.scrollHeight;
    iframe.style.height = contentHeight + 'px';
  };

  // 多次调整以等待图片加载
  setTimeout(adjustHeight, 50);
  setTimeout(adjustHeight, 300);
  setTimeout(adjustHeight, 1000);
};

watch(showPreview, async (val) => {
  if (val) {
    await nextTick();
    renderPreviewIframe();
  }
});

const canvasRef = ref<HTMLCanvasElement | null>(null);
let ctx: CanvasRenderingContext2D | null = null;
let isDrawing = false;
let lastX = 0;
let lastY = 0;
const isEmpty = ref(true);

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleString('zh-CN');
};

onMounted(async () => {
  const token = route.params.token as string;
  
  if (!token) {
    error.value = '无效的签名链接';
    isLoading.value = false;
    return;
  }

  try {
    signatureData.value = await signatureApi.getByToken(token);
    isLoading.value = false;
    
    if (signatureData.value.status === 'pending') {
      await nextTick();
      initCanvas();
      renderPreviewIframe();
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || '签名链接无效或已过期';
    isLoading.value = false;
  }
});

const initCanvas = () => {
  const canvas = canvasRef.value;
  if (!canvas) return;
  
  const wrapper = canvas.parentElement;
  if (!wrapper) return;
  
  canvas.width = wrapper.clientWidth;
  canvas.height = wrapper.clientHeight;
  
  ctx = canvas.getContext('2d');
  if (ctx) {
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 2;
  }
};

const getCoordinates = (e: MouseEvent | Touch) => {
  const canvas = canvasRef.value;
  if (!canvas) return { x: 0, y: 0 };
  
  const rect = canvas.getBoundingClientRect();
  return {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
  };
};

const startDrawing = (e: MouseEvent) => {
  isDrawing = true;
  const { x, y } = getCoordinates(e);
  lastX = x;
  lastY = y;
};

const draw = (e: MouseEvent) => {
  if (!isDrawing || !ctx) return;
  
  const { x, y } = getCoordinates(e);
  
  ctx.beginPath();
  ctx.moveTo(lastX, lastY);
  ctx.lineTo(x, y);
  ctx.stroke();
  
  lastX = x;
  lastY = y;
  isEmpty.value = false;
};

const stopDrawing = () => {
  isDrawing = false;
};

const handleTouchStart = (e: TouchEvent) => {
  if (e.touches.length === 1) {
    isDrawing = true;
    const { x, y } = getCoordinates(e.touches[0]);
    lastX = x;
    lastY = y;
  }
};

const handleTouchMove = (e: TouchEvent) => {
  if (!isDrawing || !ctx || e.touches.length !== 1) return;
  
  const { x, y } = getCoordinates(e.touches[0]);
  
  ctx.beginPath();
  ctx.moveTo(lastX, lastY);
  ctx.lineTo(x, y);
  ctx.stroke();
  
  lastX = x;
  lastY = y;
  isEmpty.value = false;
};

const clearCanvas = () => {
  const canvas = canvasRef.value;
  if (!canvas || !ctx) return;
  
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  isEmpty.value = true;
};

const submitSignature = async () => {
  const canvas = canvasRef.value;
  if (!canvas || isEmpty.value || !signatureData.value || !ctx) return;
  
  const token = route.params.token as string;
  
  // 获取签名的边界，裁剪掉多余的空白区域
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const { data, width, height } = imageData;
  
  let minX = width, minY = height, maxX = 0, maxY = 0;
  
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const alpha = data[(y * width + x) * 4 + 3];
      if (alpha > 0) {
        minX = Math.min(minX, x);
        minY = Math.min(minY, y);
        maxX = Math.max(maxX, x);
        maxY = Math.max(maxY, y);
      }
    }
  }
  
  const padding = 5;
  minX = Math.max(0, minX - padding);
  minY = Math.max(0, minY - padding);
  maxX = Math.min(width, maxX + padding);
  maxY = Math.min(height, maxY + padding);
  
  const croppedWidth = maxX - minX;
  const croppedHeight = maxY - minY;
  
  const croppedCanvas = document.createElement('canvas');
  croppedCanvas.width = croppedWidth;
  croppedCanvas.height = croppedHeight;
  
  const croppedCtx = croppedCanvas.getContext('2d');
  if (croppedCtx) {
    croppedCtx.drawImage(canvas, minX, minY, croppedWidth, croppedHeight, 0, 0, croppedWidth, croppedHeight);
  }
  
  const dataUrl = croppedCanvas.toDataURL('image/png');
  
  isSubmitting.value = true;
  
  try {
    signatureData.value = await signatureApi.submit(token, dataUrl);
  } catch (err: any) {
    error.value = err.response?.data?.detail || '提交签名失败';
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.signature-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.signature-container {
  background: white;
  border-radius: 4px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  padding: 2rem;
}

.loading-state,
.error-state,
.signed-state {
  text-align: center;
  padding: 2rem 0;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #0f172a;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  color: #ef4444;
  margin-bottom: 1rem;
}

.success-icon {
  color: #22c55e;
  margin-bottom: 1rem;
}

.error-state h2,
.signed-state h2 {
  margin: 0 0 0.5rem;
  color: #0f172a;
}

.error-state p,
.signed-state p {
  color: #64748b;
  margin: 0.25rem 0;
}

.signature-preview {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 4px;
}

.signature-preview img {
  max-width: 100%;
  max-height: 100px;
}

.header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.25rem;
}

.subtitle {
  color: #64748b;
  margin: 0;
}

.signer-info {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 4px;
}

.info-item {
  flex: 1;
}

.info-item .label {
  display: block;
  font-size: 0.75rem;
  color: #64748b;
  margin-bottom: 0.25rem;
}

.info-item .value {
  font-weight: 600;
  color: #0f172a;
}

.signature-area {
  margin-bottom: 1.5rem;
}

.canvas-wrapper {
  position: relative;
  width: 100%;
  height: 200px;
  border: 2px dashed #cbd5e1;
  border-radius: 4px;
  background: #fafafa;
  cursor: crosshair;
  overflow: hidden;
}

.canvas-wrapper canvas {
  width: 100%;
  height: 100%;
}

.placeholder {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #94a3b8;
  pointer-events: none;
}

.actions {
  display: flex;
  gap: 1rem;
}

.btn {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
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

.btn-secondary {
  background-color: white;
  color: #ef4444;
  border: 1px solid #fecaca;
}

.btn-secondary:hover {
  background-color: #fef2f2;
}

.document-preview {
  margin-bottom: 1.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.875rem;
  color: #64748b;
}

.btn-toggle {
  margin-left: auto;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  color: #0f172a;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  cursor: pointer;
}

.btn-toggle:hover {
  background: #f1f5f9;
}

.preview-viewport {
  max-height: 500px;
  overflow-y: auto;
  overflow-x: hidden;
  background: #f1f5f9;
}

.preview-iframe {
  width: 100%;
  border: none;
  display: block;
  min-height: 200px;
}
</style>
