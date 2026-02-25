<template>
  <div class="signature-dialog-overlay" @click.self="handleCancel">
    <div class="signature-dialog">
      <div class="signature-header">
        <h3>手写签名</h3>
        <button class="btn-close" @click="handleCancel">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
        </button>
      </div>
      
      <div class="signature-body">
        <div class="signature-canvas-wrapper">
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
          <div v-if="isEmpty" class="signature-placeholder">
            请在此处签名
          </div>
        </div>
        
        <div class="signature-options">
          <div class="color-picker">
            <span>颜色：</span>
            <button 
              v-for="color in colors" 
              :key="color"
              class="color-btn"
              :class="{ active: currentColor === color }"
              :style="{ backgroundColor: color }"
              @click="currentColor = color"
            ></button>
          </div>
          <div class="stroke-picker">
            <span>粗细：</span>
            <button 
              v-for="width in strokeWidths" 
              :key="width"
              class="stroke-btn"
              :class="{ active: currentStrokeWidth === width }"
              @click="currentStrokeWidth = width"
            >
              <span :style="{ width: width + 'px', height: width + 'px' }"></span>
            </button>
          </div>
        </div>
      </div>
      
      <div class="signature-footer">
        <button class="btn btn-secondary" @click="clearCanvas">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
          清除
        </button>
        <div class="btn-group">
          <button class="btn btn-outline" @click="handleCancel">取消</button>
          <button class="btn btn-primary" @click="handleConfirm" :disabled="isEmpty">确认签名</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';

const emit = defineEmits(['confirm', 'cancel']);

const canvasRef = ref<HTMLCanvasElement | null>(null);
let ctx: CanvasRenderingContext2D | null = null;
let isDrawing = false;
let lastX = 0;
let lastY = 0;

const isEmpty = ref(true);
const currentColor = ref('#000000');
const currentStrokeWidth = ref(2);

const colors = ['#000000', '#1e40af', '#166534', '#991b1b'];
const strokeWidths = [1, 2, 3, 4];

onMounted(() => {
  nextTick(() => {
    initCanvas();
  });
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
    ctx.strokeStyle = currentColor.value;
    ctx.lineWidth = currentStrokeWidth.value;
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
  
  ctx.strokeStyle = currentColor.value;
  ctx.lineWidth = currentStrokeWidth.value;
  
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
  
  ctx.strokeStyle = currentColor.value;
  ctx.lineWidth = currentStrokeWidth.value;
  
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

const handleConfirm = () => {
  const canvas = canvasRef.value;
  if (!canvas || isEmpty.value || !ctx) return;
  
  // 获取签名的边界，裁剪掉多余的空白区域
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const { data, width, height } = imageData;
  
  let minX = width, minY = height, maxX = 0, maxY = 0;
  
  // 找到签名的边界
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
  
  // 添加一些padding
  const padding = 5;
  minX = Math.max(0, minX - padding);
  minY = Math.max(0, minY - padding);
  maxX = Math.min(width, maxX + padding);
  maxY = Math.min(height, maxY + padding);
  
  // 创建裁剪后的canvas
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
  emit('confirm', dataUrl);
};

const handleCancel = () => {
  emit('cancel');
};
</script>

<style scoped>
.signature-dialog-overlay {
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

.signature-dialog {
  background: white;
  border-radius: 4px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.signature-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
}

.signature-header h3 {
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

.signature-body {
  padding: 1.25rem;
}

.signature-canvas-wrapper {
  position: relative;
  width: 100%;
  height: 200px;
  border: 2px dashed #cbd5e1;
  border-radius: 4px;
  background-color: #fafafa;
  cursor: crosshair;
  overflow: hidden;
}

.signature-canvas-wrapper canvas {
  width: 100%;
  height: 100%;
}

.signature-placeholder {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #94a3b8;
  font-size: 0.875rem;
  pointer-events: none;
}

.signature-options {
  display: flex;
  gap: 1.5rem;
  margin-top: 1rem;
}

.color-picker,
.stroke-picker {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.color-picker span,
.stroke-picker span {
  font-size: 0.875rem;
  color: #64748b;
}

.color-btn {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.color-btn.active {
  border-color: #0f172a;
  transform: scale(1.1);
}

.stroke-btn {
  width: 32px;
  height: 32px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.stroke-btn span {
  background-color: #0f172a;
  border-radius: 50%;
}

.stroke-btn.active {
  border-color: #0f172a;
  background-color: #f1f5f9;
}

.signature-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-top: 1px solid #e2e8f0;
  background-color: #f8fafc;
}

.btn-group {
  display: flex;
  gap: 0.75rem;
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

.btn-secondary {
  background-color: white;
  color: #ef4444;
  border-color: #fecaca;
}

.btn-secondary:hover {
  background-color: #fef2f2;
}
</style>
