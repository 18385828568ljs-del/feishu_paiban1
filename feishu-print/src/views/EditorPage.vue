<script setup lang="ts">
import FieldList from '@/components/FieldList.vue';
import Editor from '@/components/Editor.vue';
import SignaturePad from '@/components/SignaturePad.vue';
import SendSignatureDialog from '@/components/SendSignatureDialog.vue';
import { ref, type Ref, onMounted, onUnmounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { ArrowDown } from '@element-plus/icons-vue';
import { bitable, FieldType, type IAttachmentField } from '@lark-base-open/js-sdk';
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';
import { exportWord, getWordBlob } from '@/api/export';
import { useUser } from '@/composables/useUser';
import QRCode from 'qrcode';
import JsBarcode from 'jsbarcode';

// Composables
import { useTemplates } from '@/composables/useTemplates';
import { templateApi } from '@/api/templates';
import { useBackfill } from '@/composables/useBackfill';
import { useExportLogic } from '@/composables/useExportLogic';
import { useEditorMapping } from '@/composables/useEditorMapping';
import { insertCoverPage, removeCoverPage } from '@/utils/editor-dom-utils';
import { Upload, Plus, Select, UploadFilled } from '@element-plus/icons-vue';

const route = useRoute();
const router = useRouter();
const { initUser, checkAndUseFeature, pdfExportsRemaining } = useUser();

// --- Template Logic ---
const {
  selectedTemplate,
  templates,
  editorContent,
  loadTemplates,
  handleNewTemplate,
  handleSaveTemplate,
  handleSaveAsNewTemplate,
  handleDeleteTemplate
} = useTemplates();

// --- Backfill Logic ---
const {
  targetFieldId,
  attachmentFields,
  backfillFormat,
  selectedRecordIds,
  isBackfilling,
  backfillProgress,
  showBackfillDialog,
  backfillCancelled,
  loadAttachmentFields,
  handleBackfillCurrent,
  handleBackfillSelected,
  cancelBackfill
} = useBackfill();

const { buildNormalizedMap, findValueByFieldName } = useEditorMapping();

const editorRef: Ref | null = ref(null);
const isLoadingEditor = ref(true);
const isLoadingRecords = ref(false);
const recordList = ref<{ id: string; title: string }[]>([]);
const selectedRecordId = ref('__placeholder__');
const currentRowData = ref<any>(null);
const fieldNameToIdMap = ref<Record<string, string>>({});
const availableFieldNames = ref<string[]>([]);
const fieldTypes = ref<Record<string, number>>({});
const insertCodeDialogVisible = ref(false);
const insertCodeType = ref<'qrcode' | 'barcode'>('qrcode');
const insertCodeForm = ref({ source: 'custom', text: '', field: '', width: 100, height: 100 });
const currentInsertEditor: any = null;

// 批量回填相关
const selectedRecordIdsForBackfill = ref<string[]>([]);
const backfillRangeInput = ref('');

/**
 * 解析范围输入，如 "1-30" 或 "1,3,5-10"，转换为记录序号集合
 */
const parseRange = (input: string): Set<number> => {
  const indices = new Set<number>();
  const parts = input.split(',').map(s => s.trim()).filter(Boolean);
  for (const part of parts) {
    if (part.includes('-')) {
      const [startStr, endStr] = part.split('-').map(s => s.trim());
      const start = parseInt(startStr);
      const end = parseInt(endStr);
      if (!isNaN(start) && !isNaN(end)) {
        for (let i = Math.min(start, end); i <= Math.max(start, end); i++) {
          indices.add(i);
        }
      }
    } else {
      const num = parseInt(part);
      if (!isNaN(num)) indices.add(num);
    }
  }
  return indices;
};

const applyBackfillRange = () => {
  const input = backfillRangeInput.value.trim();
  if (!input) return;
  const indices = parseRange(input);
  const validRecords = recordList.value.filter(r => r.id !== '__placeholder__');
  const selected: string[] = [];
  indices.forEach(i => {
    // 序号从 1 开始，数组索引从 0 开始
    if (i >= 1 && i <= validRecords.length) {
      selected.push(validRecords[i - 1].id);
    }
  });
  if (selected.length === 0) {
    ElMessage.warning('输入的范围没有匹配到任何记录');
    return;
  }
  selectedRecordIdsForBackfill.value = selected;
  ElMessage.success(`已选择 ${selected.length} 条记录`);
};

// --- Cover Page Logic ---
const coverDialogVisible = ref(false);
const coverType = ref<'preset' | 'image'>('preset');
const coverPreset = ref('business');
const coverImageUrl = ref('');

const handleOpenCoverSettings = () => {
  coverDialogVisible.value = true;
};

const handleApplyCover = () => {
  if (coverType.value === 'image' && !coverImageUrl.value) {
    ElMessage.warning('请上传或输入图片地址');
    return;
  }
  // @ts-ignore
  insertCoverPage(editorRef.value?.getEditorInstance(), {
    type: coverType.value,
    value: coverType.value === 'image' ? coverImageUrl.value : coverPreset.value
  });
  coverDialogVisible.value = false;
  ElMessage.success('封页已更新');
};

const handleRemoveCover = () => {
  // @ts-ignore
  removeCoverPage(editorRef.value?.getEditorInstance());
  coverDialogVisible.value = false;
  ElMessage.success('封页已移除');
};

const handleCoverImageUpload = (file: any) => {
  const reader = new FileReader();
  reader.onload = (e) => {
    coverImageUrl.value = e.target?.result as string;
  };
  reader.readAsDataURL(file.raw);
};

onMounted(() => {
  window.addEventListener('openCoverSettings', handleOpenCoverSettings);
  window.addEventListener('openSignaturePad', handleOpenSignaturePad as EventListener);
  window.addEventListener('openSendSignatureDialog', handleOpenSendSignatureDialog as EventListener);
  window.addEventListener('openInsertCodeDialog', handleOpenInsertCodeDialog as EventListener);
});

onUnmounted(() => {
  window.removeEventListener('openCoverSettings', handleOpenCoverSettings);
  window.removeEventListener('openSignaturePad', handleOpenSignaturePad as EventListener);
  window.removeEventListener('openSendSignatureDialog', handleOpenSendSignatureDialog as EventListener);
  window.removeEventListener('openInsertCodeDialog', handleOpenInsertCodeDialog as EventListener);
});

// --- QR/Barcode Insertion Logic ---
const handleOpenInsertCodeDialog = (e: CustomEvent) => {
  const { type, editor } = e.detail;
  insertCodeType.value = type;
  // Set default dimensions based on type
  if (type === 'qrcode') {
    insertCodeForm.value = { source: 'custom', text: '', field: '', width: 100, height: 100 };
  } else {
    insertCodeForm.value = { source: 'custom', text: '', field: '', width: 200, height: 60 };
  }
  insertCodeDialogVisible.value = true;
};

const handleInsertCodeConfirm = async () => {
  const { source, text, field, width, height } = insertCodeForm.value;
  const style = `width:${width}px;height:${height}px;vertical-align:middle;background-color:#f8fafc;`;
  
  // Use the editor reference since we are in parent context
  const editor = editorRef.value?.getEditorInstance();
  if (!editor) return;

  // Helper to create placeholder image
  const createPlaceholder = (type: 'qrcode' | 'barcode', w: number, h: number, text: string) => {
    const canvas = document.createElement('canvas');
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.fillStyle = '#f8fafc';
      ctx.fillRect(0, 0, w, h);
      ctx.strokeStyle = '#cbd5e1';
      ctx.lineWidth = 2;
      ctx.strokeRect(0, 0, w, h);
      
      ctx.fillStyle = '#94a3b8';
      ctx.font = '12px sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(type === 'qrcode' ? '二维码' : '条形码', w / 2, h / 2);
    }
    return canvas.toDataURL();
  };

  if (source === 'field' && field) {
      if (!currentRowData.value) {
        ElMessage.warning('请先在预览区选择一条具体的记录（不是"占位符"）');
        return;
      }
      
      let imgSrc = '';
      
      // Try to get real value
      if (fieldNameToIdMap.value && currentRowData.value.fields) {
          buildNormalizedMap(fieldNameToIdMap.value);
          let { value } = findValueByFieldName(field, currentRowData.value.fields);
          // Strip HTML tags (e.g. <br>) for barcode/qrcode value
          if (value) {
              value = value.replace(/<[^>]*>/g, '').trim();
          }
          
          if (value) {
              try {
                  if (insertCodeType.value === 'qrcode') {
                       imgSrc = await QRCode.toDataURL(value, { width: 300, margin: 0 });
                  } else {
                       // CODE128 only supports ASCII characters
                       if (/[^\x00-\x7F]/.test(value)) {
                            ElMessage.error(`该字段"${field}"的值包含非ASCII字符（如中文），条形码仅支持英文和数字，请更换字段`);
                            return;
                       }
                       const canvas = document.createElement('canvas');
                       JsBarcode(canvas, value, { format: 'CODE128', displayValue: true, width: 3, height: 80, margin: 0 });
                       imgSrc = canvas.toDataURL();
                  }
              } catch (e) {
                  console.error('Generation failed', e);
                  imgSrc = createPlaceholder(insertCodeType.value, width, height, '生成失败');
              }
          }
      }
      
      // Fallback if no value or generation failed
      if (!imgSrc) {
          imgSrc = createPlaceholder(insertCodeType.value, width, height, field);
      }

      const imgClass = insertCodeType.value === 'qrcode' ? 'dynamic-qrcode' : 'dynamic-barcode';
      const altText = insertCodeType.value === 'qrcode' ? '二维码' : '条形码';
      
      // Remove background-color from style since it's in the generated image (if real) or handled
      // Actually real generated images provided by lib usually transparent or white background.
      // JSBarcode: white background default? usually transparent.
      // QRCode: white background default? we used margin:0, usually transparent.
      // Let's add white background to style to be safe for transparency
      const imgStyle = `width:${width}px;height:${height}px;vertical-align:middle;`;
      
      editor.insertContent(`<img class="${imgClass}" data-fieldname="${field}" src="${imgSrc}" width="${width}" height="${height}" style="${imgStyle}" alt="${altText}: ${field}" />`);
      
      // Trigger mapping update (still needed for when record changes)
      setTimeout(() => {
        if (currentRowData.value && fieldNameToIdMap.value) {
           editorRef.value?.applyLiveMapping?.(editor, currentRowData.value, fieldNameToIdMap.value);
        }
      }, 100);
  } else if (source === 'field' && !field) {
    ElMessage.warning('请选择一个字段');
    return;
  } else {
    // Custom Content
    if (!text?.trim()) {
      ElMessage.warning(`请输入${insertCodeType.value === 'qrcode' ? '二维码' : '条形码'}内容`);
      return;
    }
    
    try {
      let url = '';
      if (insertCodeType.value === 'qrcode') {
         url = await QRCode.toDataURL(text, { width: 300, margin: 0 });
         editor.insertContent(`<img src="${url}" width="${width}" height="${height}" style="${style.replace('background-color:#f8fafc;', '')}" />`);
      } else {
         const canvas = document.createElement('canvas');
         JsBarcode(canvas, text, { format: 'CODE128', displayValue: true, width: 3, height: 80, margin: 0 });
         url = canvas.toDataURL();
         editor.insertContent(`<img src="${url}" width="${width}" height="${height}" style="${style.replace('background-color:#f8fafc;', '')}" />`);
      }
    } catch (e) {
      ElMessage.error('生成失败，请检查内容是否包含不支持的字符');
      return;
    }
  }
  insertCodeDialogVisible.value = false;
};

// --- Utilities (Internal for positioning/capturing) ---

const readPageMarginFromIframe = (): [number, number, number, number] => {
  const editorElement = document.querySelector('.custom-editor-container iframe') as HTMLIFrameElement | null;
  const defaultMargins: [number, number, number, number] = [10, 10, 10, 10];
  
  if (!editorElement?.contentDocument) return defaultMargins;
  
  const pageContent = editorElement.contentDocument.querySelector('.template-page-content') as HTMLElement | null;
  if (!pageContent) return defaultMargins;
  
  const computedStyle = window.getComputedStyle(pageContent);
  const padding = computedStyle.padding;
  
  // 优先尝试解析 mm 单位
  let match = padding.match(/(\d+\.?\d*)mm/g);
  if (match && match.length > 0) {
    const values = match.map(m => parseFloat(m));
    if (values.length === 1) {
      return [values[0], values[0], values[0], values[0]];
    } else if (values.length === 2) {
      return [values[0], values[1], values[0], values[1]];
    } else if (values.length === 4) {
      return [values[0], values[1], values[2], values[3]];
    }
  }
  
  // 回退：尝试解析 px 单位并转换为 mm
  match = padding.match(/(\d+\.?\d*)px/g);
  if (match && match.length > 0) {
    const values = match.map(m => Math.round(parseFloat(m) * 0.2645833));
    if (values.length === 1) {
      return [values[0], values[0], values[0], values[0]];
    } else if (values.length === 2) {
      return [values[0], values[1], values[0], values[1]];
    } else if (values.length === 4) {
      return [values[0], values[1], values[2], values[3]];
    }
  }
  
  return defaultMargins;
};

const elementToHtmlWithStyles = (element: HTMLElement, sourceDocument?: Document): string => {
  const clone = element.cloneNode(true) as HTMLElement;
  let sourceRoot: HTMLElement | null = sourceDocument?.body || null;
  let cloneRoot: HTMLElement | null = clone;

  if (sourceDocument) {
    const templateRootInClone = clone.id === 'template-root' ? clone : clone.querySelector('#template-root') as HTMLElement | null;
    if (templateRootInClone) {
      sourceRoot = sourceDocument.querySelector('#template-root') as HTMLElement | null;
      cloneRoot = templateRootInClone;
    }
  }

  // CSS属性白名单：只复制Word能正确支持且对布局有实际影响的属性
  const cssWhitelist = [
    // 尺寸和布局
    'width', 'height', 'min-width', 'max-width', 'min-height', 'max-height',
    // 内外边距
    'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
    'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
    // 边框
    'border', 'border-width', 'border-style', 'border-color',
    'border-top', 'border-right', 'border-bottom', 'border-left',
    'border-collapse', 'border-spacing',
    // 字体和文本
    'font-family', 'font-size', 'font-weight', 'font-style',
    'color', 'text-align', 'text-decoration', 'text-indent',
    'line-height', 'letter-spacing', 'word-spacing',
    // 背景
    'background', 'background-color', 'background-image',
    // 表格特定
    'vertical-align', 'table-layout',
    // 显示和定位（有限支持）
    'display', 'position', 'top', 'left', 'right', 'bottom'
  ];

  const calculatePath = (targetEl: HTMLElement): number[] => {
    if (!cloneRoot || targetEl === cloneRoot) return [];
    const path: number[] = [];
    let current: HTMLElement | null = targetEl;
    while (current && current !== cloneRoot && current.parentElement) {
      const parent = current.parentElement as HTMLElement;
      path.unshift(Array.from(parent.children).indexOf(current));
      current = parent;
    }
    return path;
  };

  const findSourceElement = (path: number[]): HTMLElement | null => {
    if (!sourceRoot) return null;
    let current = sourceRoot;
    for (const index of path) {
      const children = Array.from(current.children) as HTMLElement[];
      if (index >= 0 && index < children.length) current = children[index];
      else return null;
    }
    return current;
  };

  const processElement = (el: HTMLElement) => {
    const path = calculatePath(el);
    const sourceEl = findSourceElement(path);
    const computedStyle = sourceEl ? sourceDocument?.defaultView?.getComputedStyle(sourceEl) : window.getComputedStyle(el);
    
    if (computedStyle) {
      // 只复制白名单中的属性
      const styleParts: string[] = [];
      cssWhitelist.forEach(prop => {
        const value = computedStyle.getPropertyValue(prop);
        // 跳过空值和默认值
        if (value && value !== 'none' && value !== 'normal' && value !== 'auto' && value !== '0px') {
          styleParts.push(`${prop}:${value}`);
        }
      });
      
      // 保留原有的内联样式（优先级更高）
      const inlineStyle = el.getAttribute('style') || '';
      if (inlineStyle) {
        styleParts.push(inlineStyle);
      }
      
      el.style.cssText = styleParts.join(';');
    }
    
    Array.from(el.children).forEach(child => processElement(child as HTMLElement));
  };

  processElement(clone);
  return clone.outerHTML;
};

const createExportRoot = (options?: { includePageNumbers?: boolean }) => {
  const iframe = document.querySelector('.custom-editor-container iframe') as HTMLIFrameElement | null;
  if (!iframe?.contentDocument?.body) throw new Error('未找到编辑器内容');
  const doc = iframe.contentDocument;
  const contentWrapper = document.createElement('div');
  contentWrapper.innerHTML = doc.body.innerHTML;
  
  const styleElement = document.createElement('style');
  styleElement.innerHTML = Array.from(doc.head.querySelectorAll('style')).map(s => s.innerHTML).join('\n');
  contentWrapper.insertBefore(styleElement, contentWrapper.firstChild);
  
  contentWrapper.style.cssText = 'background:#fff;position:relative;overflow:visible;';
  const exportRoot = document.createElement('div');
  exportRoot.style.cssText = 'position:absolute;left:-9999px;top:0;';
  exportRoot.appendChild(contentWrapper);
  document.body.appendChild(exportRoot);

  // 导出前重置编辑器页面容器的样式
  const allPages = contentWrapper.querySelectorAll('.template-page-content');
  allPages.forEach((page) => {
    const el = page as HTMLElement;
    // 保持页面原有尺寸和样式，只移除编辑器装饰
    el.style.boxShadow = 'none';
    el.style.borderRadius = '0';
    el.style.margin = '0';
  });
  // 浮动图片：移除 UI 辅助元素，保留图片本身
  contentWrapper.querySelectorAll('.floating-image .fi-handle').forEach(el => el.remove());
  contentWrapper.querySelectorAll('.floating-image.fi-selected').forEach(el => el.classList.remove('fi-selected'));
  // template-root 也重置
  const tplRoot = contentWrapper.querySelector('#template-root') as HTMLElement | null;
  if (tplRoot) {
    tplRoot.style.minHeight = 'auto';
    tplRoot.style.padding = '0';
    tplRoot.style.margin = '0';
    tplRoot.style.background = 'transparent';
  }

  if (options?.includePageNumbers) {
    const templateRoot = contentWrapper.querySelector('#template-root') as HTMLElement | null;
    if (templateRoot?.getAttribute('data-show-page-number') === '1') {
      contentWrapper.querySelectorAll('.template-page').forEach(page => {
        const pageNum = page.getAttribute('data-page');
        if (!pageNum) return;
        const el = document.createElement('div');
        el.className = 'export-page-number';
        el.textContent = `第${pageNum}页`;
        el.style.cssText = 'position:absolute;left:50%;bottom:10px;transform:translateX(-50%);font-size:14px;color:rgba(55,65,81,0.75);';
        page.appendChild(el);
      });
    }
  }

  return { iframe, doc, exportRoot, contentWrapper, cleanup: () => document.body.contains(exportRoot) && document.body.removeChild(exportRoot) };
};

const generateWordExportData = async (contentWrapper: HTMLElement, doc: Document | null) => {
  await new Promise(res => requestAnimationFrame(() => requestAnimationFrame(res)));
  const wrapper = (contentWrapper.querySelector('#template-root') as HTMLElement | null) ?? contentWrapper;
  return { htmlString: elementToHtmlWithStyles(wrapper, doc || undefined), margins: readPageMarginFromIframe() };
};

const generateExportCanvas = async (exportRoot: HTMLElement) => {
  await new Promise(res => requestAnimationFrame(() => requestAnimationFrame(res)));
  return html2canvas(exportRoot, { scale: 2, useCORS: true, backgroundColor: '#ffffff' });
};

/**
 * 获取当前记录的首列索引值，用于构建导出文件名。
 * 优先取 availableFieldNames 的第一个字段对应的值。
 */
const getRecordIndexValue = (): string => {
  if (!currentRowData.value?.fields || availableFieldNames.value.length === 0) return '';
  const firstFieldName = availableFieldNames.value[0];
  const firstFieldId = fieldNameToIdMap.value[firstFieldName];
  if (!firstFieldId) return '';
  const val = currentRowData.value.fields[firstFieldId];
  if (val == null) return '';
  // 处理数组类型（如多选、人员等）
  if (Array.isArray(val)) {
    const texts = val.map((v: any) => (typeof v === 'object' ? (v.text || v.name || '') : String(v))).filter(Boolean);
    return texts.join(',');
  }
  return String(val);
};

/**
 * 构建导出文件名：模板名-首列值
 */
const buildExportName = (): string => {
  const tplName = templates.value.find(t => t.id === selectedTemplate.value)?.name || '导出';
  const indexVal = getRecordIndexValue();
  return indexVal ? `${tplName}-${indexVal}` : tplName;
};

// --- Export Flow Integration ---
const { handleExportPDF: pdfAction, handleExportImage: imgAction, handleExportLongImage: longImgAction, handleExportWordAction: wordAction } = useExportLogic(
  checkAndUseFeature as any, readPageMarginFromIframe, createExportRoot, generateWordExportData, generateExportCanvas
);

// 辅助函数：清除内容容器的 padding，用于 PDF/Word 导出（边距由外部参数控制）
const clearContentPadding = (wrapper: HTMLElement) => {
  wrapper.querySelectorAll('.template-page-content').forEach((page) => {
    (page as HTMLElement).style.padding = '0';
  });
};

const handleExportPDF = () => {
  const { contentWrapper, cleanup } = createExportRoot({ includePageNumbers: true });
  clearContentPadding(contentWrapper);
  pdfAction(contentWrapper, cleanup, buildExportName());
};

const handleExportImage = () => {
  const { contentWrapper, cleanup } = createExportRoot({ includePageNumbers: true });
  // 图片导出保留 padding，逐页导出
  imgAction(contentWrapper, cleanup, buildExportName());
};

const handleExportLongImage = () => {
  const { contentWrapper, cleanup } = createExportRoot({ includePageNumbers: true });
  // 长图导出：所有页面拼成一张
  longImgAction(contentWrapper, cleanup, buildExportName());
};

const handleExportWord = () => {
  const { contentWrapper, cleanup, doc } = createExportRoot({ includePageNumbers: true });
  clearContentPadding(contentWrapper);
  wordAction(contentWrapper, doc, cleanup, buildExportName());
};

const handleExportCommand = (cmd: string) => {
  if (cmd === 'pdf') handleExportPDF();
  else if (cmd === 'image') handleExportImage();
  else if (cmd === 'longImage') handleExportLongImage();
  else if (cmd === 'word') handleExportWord();
};

const handleRenameTemplate = async () => {
  if (!selectedTemplate.value) return;
  const currentTpl = templates.value.find(t => t.id === selectedTemplate.value);
  if (!currentTpl || currentTpl.is_system) {
    if (currentTpl?.is_system) ElMessage.info('系统模板不支持重命名');
    return;
  }
  try {
    const { value: newName } = await ElMessageBox.prompt('请输入新的模板名称', '重命名模板', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValue: currentTpl.name,
      inputPattern: /.+/,
      inputErrorMessage: '模板名称不能为空'
    });
    if (newName && newName !== currentTpl.name) {
      await templateApi.update(Number(selectedTemplate.value), {
        name: newName
      });
      currentTpl.name = newName;
      ElMessage.success('模板名称已更新');
    }
  } catch (e: any) {
    if (e !== 'cancel') {
      console.error('重命名失败:', e);
      ElMessage.error(e?.response?.data?.detail || '重命名失败');
    }
  }
};

// --- 模板导入导出 ---

const handleExportTemplate = () => {
  const currentTpl = templates.value.find(t => t.id === selectedTemplate.value);
  if (!currentTpl) {
    ElMessage.warning('请先选择一个模板');
    return;
  }
  
  // 从编辑器获取当前完整内容
  const editorInstance = editorRef.value?.getEditorInstance?.();
  let exportContent = currentTpl.content; // 兜底：数据库内容
  
  if (editorInstance) {
    // 方案：直接从 iframe body 获取原始 HTML（保留所有 inline style、属性）
    // editor.getContent() 会经过 TinyMCE serializer，可能规范化某些内容
    const iframeDoc = editorInstance.getDoc();
    if (iframeDoc?.body) {
      // 克隆 body 以便清理 TinyMCE 内部标记
      const clone = iframeDoc.body.cloneNode(true) as HTMLElement;
      
      // 移除 TinyMCE 内部元素
      clone.querySelectorAll('[data-mce-bogus]').forEach(el => {
        // 保留分页符（它们也有 data-mce-bogus）
        if (el.classList.contains('mce-pagebreak') || el.classList.contains('page-break-visual')) {
          // 移除 data-mce-bogus 属性，防止导入时被 TinyMCE 删除
          el.removeAttribute('data-mce-bogus');
          return;
        }
        el.remove();
      });
      clone.querySelectorAll('.mce-visual-caret').forEach(el => el.remove());
      clone.querySelectorAll('.mce-offscreen-selection').forEach(el => el.remove());
      
      // 移除 data-mce-style 属性（TinyMCE 的内部缓存，导入时会重新生成）
      clone.querySelectorAll('[data-mce-style]').forEach(el => {
        el.removeAttribute('data-mce-style');
      });
      // 移除 data-mce-href / data-mce-src（TinyMCE 内部缓存）
      clone.querySelectorAll('[data-mce-href]').forEach(el => el.removeAttribute('data-mce-href'));
      clone.querySelectorAll('[data-mce-src]').forEach(el => el.removeAttribute('data-mce-src'));
      
      // 移除映射相关的临时元素和状态
      clone.querySelectorAll('.mapped-shadow').forEach(el => el.remove());
      clone.querySelectorAll('.mapped-shadow-origin').forEach(el => {
        el.classList.remove('mapped-shadow-origin');
        (el as HTMLElement).style.display = '';
      });
      clone.querySelectorAll('.template-field.is-mapped').forEach(el => {
        el.classList.remove('is-mapped');
        (el as HTMLElement).style.display = '';
      });
      
      // 移除浮动图片的 UI 辅助元素（缩放手柄、选中状态），保留图片本身
      clone.querySelectorAll('.floating-image .fi-handle').forEach(el => el.remove());
      clone.querySelectorAll('.floating-image.fi-selected').forEach(el => el.classList.remove('fi-selected'));
      
      exportContent = clone.innerHTML;
    }
  }
  
  const data = {
    version: 1,
    name: currentTpl.name,
    template_type: (currentTpl as any).template_type || 'normal',
    content: exportContent
  };
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${currentTpl.name}.json`;
  link.click();
  URL.revokeObjectURL(url);
  ElMessage.success('模板文件已导出');
};

const handleImportTemplate = () => {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.json';
  input.onchange = async (e: Event) => {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (!file) return;
    try {
      const text = await file.text();
      const data = JSON.parse(text);
      if (!data.name || !data.content) {
        ElMessage.error('模板文件格式不正确，缺少 name 或 content 字段');
        return;
      }
      
      // 先在本地检查重名，预先生成不冲突的名称，避免不必要的 400 请求
      const existingNames = new Set(templates.value.map(t => t.name));
      let name = data.name;
      if (existingNames.has(name)) {
        for (let i = 2; i <= 20; i++) {
          const candidate = `${data.name} (${i})`;
          if (!existingNames.has(candidate)) {
            name = candidate;
            break;
          }
        }
      }
      
      // 尝试创建，如果仍然重名（服务端有其他数据）则自动加后缀重试
      let created = false;
      for (let i = 0; i < 10; i++) {
        try {
          const newTemplate = await templateApi.create({
            name,
            content: data.content,
            template_type: data.template_type || 'normal'
          });
          templates.value.push({
            id: String(newTemplate.id),
            name: newTemplate.name,
            content: newTemplate.content,
            is_system: newTemplate.is_system,
            owner_id: newTemplate.owner_id as number
          });
          selectedTemplate.value = String(newTemplate.id);
          ElMessage.success(`模板「${newTemplate.name}」导入成功`);
          created = true;
          break;
        } catch (err: any) {
          const detail = err?.response?.data?.detail || '';
          if (detail.includes('已存在')) {
            // 服务端重名，加后缀重试
            name = `${data.name} (${i + 2})`;
          } else {
            throw err;
          }
        }
      }
      if (!created) {
        ElMessage.error('导入失败：多次重命名仍然冲突');
      }
    } catch (err: any) {
      if (!err?.response) {
        ElMessage.error('导入模板失败：文件解析错误');
      } else {
        ElMessage.error('导入模板失败：' + (err?.response?.data?.detail || err.message));
      }
    }
  };
  input.click();
};

const handleTemplateCommand = (cmd: string) => {
  if (cmd === 'save') handleSaveTemplate();
  else if (cmd === 'saveAs') handleSaveAsNewTemplate(() => editorContent.value);
  else if (cmd === 'exportTpl') handleExportTemplate();
  else if (cmd === 'importTpl') handleImportTemplate();
};

// --- Records & Data Handling ---

const loadRecordList = async () => {
  isLoadingRecords.value = true;
  try {
    const table = await bitable.base.getActiveTable();
    const view = await table.getActiveView();
    const ids = await view.getVisibleRecordIdList();
    recordList.value = [{ id: '__placeholder__', title: '占位符' }, ...ids.filter((id): id is string => !!id).map((id, i) => ({ id, title: `记录 ${i + 1}` }))];
  } finally { isLoadingRecords.value = false; }
};

const loadFieldMeta = async () => {
  try {
    const table = await bitable.base.getActiveTable();
    const view = await table.getActiveView();
    const meta = await table.getFieldMetaList();
    const viewMeta = await view.getFieldMetaList();

    const map: Record<string, string> = {};
    const types: Record<string, number> = {};
    const names: string[] = [];

    // Build map from ALL fields (for mapping engine)
    meta.forEach(f => {
      if (f.name) {
        map[f.name] = f.id;
        types[f.name] = f.type;
      }
    });

    // Build names from VIEW fields (for dropdown UI, to match sidebar)
    viewMeta.forEach(f => {
      if (f.name) names.push(f.name);
    });

    fieldNameToIdMap.value = map;
    fieldTypes.value = types;
    availableFieldNames.value = names;
    return meta;
  } catch (e) {
    console.error('加载字段元数据失败:', e);
    return [];
  }
};

const loadRecordData = async (recordId: string) => {
  if (recordId === '__placeholder__') { currentRowData.value = null; return; }
  try {
    const table = await bitable.base.getActiveTable();
    const record = await table.getRecordById(recordId);
    if (!record?.fields) return;

    // 获取字段元数据（如果之前没加载成功，这里重新获取）
    let meta = await table.getFieldMetaList();
    // 确保 availableFieldNames 即使在还没调用 loadFieldMeta 的情况下也能更新（虽然 onMounted 会调用）
    // 但为了性能，如果我们已经有了 map，其实可以不重新构建 map，只是为了附件解析需要 meta
    
    // 预解析附件（直接附件字段）
    await Promise.all(meta.filter(f => f.type === FieldType.Attachment).map(async (f) => {
      const val = record.fields[f.id];
      if (Array.isArray(val) && val.length > 0) {
        const field = await table.getField<IAttachmentField>(f.id);
        const urls = await field.getAttachmentUrls(recordId);
        val.forEach((item: any, i: number) => { if (urls[i]) item.tmp_url = urls[i]; });
      }
    }));

    // 解析非附件字段（Lookup/Formula等）中的附件 URL
    const attachmentFieldIds = new Set(meta.filter(f => f.type === FieldType.Attachment).map(f => f.id));
    const unresolvedTokenItems: any[] = [];
    for (const f of meta) {
      if (attachmentFieldIds.has(f.id)) continue;
      const val = record.fields[f.id];
      if (!Array.isArray(val)) continue;
      for (const item of val) {
        if (item && typeof item === 'object' && (item as any).token && !(item as any).tmp_url) {
          unresolvedTokenItems.push(item);
        }
      }
    }
    if (unresolvedTokenItems.length > 0) {
      await Promise.all(unresolvedTokenItems.map(async (item: any) => {
        try {
          const url = await table.getAttachmentUrl(item.token);
          if (url) item.tmp_url = url;
        } catch (_) {}
      }));
    }

    currentRowData.value = record;
    // 如果 loadFieldMeta 失败或未执行，这里作为兜底更新 map
    if (availableFieldNames.value.length === 0) {
         try {
           const view = await table.getActiveView();
           const viewMeta = await view.getFieldMetaList();
           
           const map: Record<string, string> = {};
           const names: string[] = [];
           const types: Record<string, number> = {};
           // Build map from ALL fields (meta from table)
           meta.forEach(f => {
             if (f.name) {
               map[f.name] = f.id;
               types[f.name] = f.type;
             }
           });
           
           // Build names from VIEW fields
           viewMeta.forEach(f => { if (f.name) names.push(f.name); });

           fieldNameToIdMap.value = map;
           fieldTypes.value = types;
           availableFieldNames.value = names;
         } catch (e) {
           console.error('Fallback load view meta failed:', e);
           // Absolute fallback: Table fields
           const map: Record<string, string> = {};
           const types: Record<string, number> = {};
           const names: string[] = [];
           meta.forEach(f => {
             if (f.name) {
               map[f.name] = f.id;
               names.push(f.name);
               types[f.name] = f.type;
             }
           });
           fieldNameToIdMap.value = map;
           fieldTypes.value = types;
           availableFieldNames.value = names;
         }
    }
  } catch (e) {
    console.error('加载记录数据失败:', e);
    ElMessage.error('加载记录数据失败，请检查网络或刷新页面');
  }
};

const getContentAsFile = async (format: string, recordId: string): Promise<File> => {
  const { exportRoot, contentWrapper, cleanup, doc } = createExportRoot({ includePageNumbers: true });
  const tplName = templates.value.find(t => t.id === selectedTemplate.value)?.name || '导出';
  
  // 获取当前记录的首列值作为文件名后缀
  const indexVal = getRecordIndexValue();
  const exportName = indexVal ? `${tplName}-${indexVal}` : tplName;
  
  let blob: Blob;
  let fileName: string;
  let mime: string;

  if (format === 'image') {
    const canvas = await generateExportCanvas(exportRoot);
    cleanup();
    blob = await new Promise<Blob>((res, rej) => canvas.toBlob(b => b ? res(b) : rej(), 'image/png'));
    fileName = `${exportName}.png`; mime = 'image/png';
  } else if (format === 'pdf') {
    // 逐页渲染 PDF
    const pages = contentWrapper.querySelectorAll('.template-page-content');
    const pdf = new jsPDF({ unit: 'mm', format: 'a4', orientation: 'portrait' });
    const pdfWidth = 210;
    const pdfHeight = 297;

    for (let i = 0; i < pages.length; i++) {
      const page = pages[i] as HTMLElement;
      const canvas = await html2canvas(page, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff'
      });

      if (i > 0) pdf.addPage();
      const imgData = canvas.toDataURL('image/jpeg', 0.95);
      const imgHeight = (canvas.height * pdfWidth) / canvas.width;
      pdf.addImage(imgData, 'JPEG', 0, 0, pdfWidth, Math.min(imgHeight, pdfHeight));
    }
    cleanup();
    blob = pdf.output('blob');
    fileName = `${exportName}.pdf`; mime = 'application/pdf';
  } else {
    clearContentPadding(contentWrapper);
    const { htmlString, margins } = await generateWordExportData(contentWrapper, doc);
    cleanup();
    blob = await getWordBlob(htmlString, exportName, margins);
    fileName = `${exportName}.doc`; mime = 'application/msword';
  }
  return new File([blob], fileName, { type: mime });
};

// 回填确认处理
const handleBackfillConfirm = async () => {
  if (!targetFieldId.value) {
    ElMessage.warning('请先选择回填字段');
    return;
  }
  
  try {
    const targetRecords = selectedRecordIdsForBackfill.value;
    
    if (targetRecords.length === 0) {
      ElMessage.warning('请至少选择一条记录');
      return;
    }
    
    selectedRecordIds.value = targetRecords;
    await handleBackfillSelected(getContentAsFile, loadRecordData);
    
    showBackfillDialog.value = false;
  } catch (error) {
    console.error('[EditorPage] 回填失败:', error);
  }
};



// --- Lifecycle & Watches ---

watch(showBackfillDialog, (val) => {
  if (val) {
    if (selectedRecordId.value && selectedRecordId.value !== '__placeholder__') {
      selectedRecordIdsForBackfill.value = [selectedRecordId.value];
    } else {
      selectedRecordIdsForBackfill.value = [];
    }
  }
});

watch(selectedRecordId, id => loadRecordData(id));


onMounted(async () => {
  isLoadingEditor.value = true;
  await Promise.all([initUser(), loadTemplates(), loadRecordList(), loadAttachmentFields(), loadFieldMeta()]);
  
  // 检查路由参数，从模板库跳转时自动加载模板
  const templateIdFromQuery = route.query.templateId as string | undefined;
  if (templateIdFromQuery) {
    // 等待templates加载完成后再选择
    const template = templates.value.find(t => t.id === templateIdFromQuery);
    if (template) {
      selectedTemplate.value = templateIdFromQuery;
    } else {
      ElMessage.warning('模板不存在，请重新选择');
    }
  }
  
  isLoadingEditor.value = false;
});

// 其他 UI 状态
const showSignaturePad = ref(false);
const showSendSignatureDialog = ref(false);
let currentSignatureEditor: any = null;

const handleOpenSignaturePad = (e: CustomEvent) => { currentSignatureEditor = e.detail.editor; showSignaturePad.value = true; };
const handleOpenSendSignatureDialog = (e: CustomEvent) => { currentSignatureEditor = e.detail.editor; showSendSignatureDialog.value = true; };

const handleSignatureConfirm = (url: string) => { if (currentSignatureEditor) currentSignatureEditor.insertContent(`<img src="${url}" style="height:60px;" />`); showSignaturePad.value = false; };
const handleSendSignatureConfirm = (url: string) => { if (currentSignatureEditor) currentSignatureEditor.insertContent(`<img src="${url}" style="height:60px;" />`); }; // 这里的 dialog 自己处理了关闭

// 处理字段插入（支持占位符和纯文本）
const handleInsertField = (fieldData: any) => {
  if (fieldData.type === 'text') {
    // 系统字段：直接插入纯文本
    editorRef.value?.insertContent(fieldData.content);
  } else if (fieldData.type === 'placeholder') {
    // 用户字段：插入占位符对象，触发 Editor.vue 渲染特殊样式
    const fieldObj = { id: fieldData.data.id, name: fieldData.data.name };
    editorRef.value?.insertContent(fieldObj);
  }
};
</script>

<template>
  <div class="editor-page">
    <!-- 顶部导航栏 -->
    <header class="page-header">
      <div class="header-left">
        <el-button link class="btn-home" @click="router.push('/')">
          <el-icon><ArrowDown style="transform: rotate(90deg)" /></el-icon>
          返回首页
        </el-button>
        <el-divider direction="vertical" />
        <span 
          class="document-title" 
          :title="'点击修改模板名称'"
          @click="handleRenameTemplate"
          :style="{ cursor: selectedTemplate && !templates.find(t => t.id === selectedTemplate)?.is_system ? 'pointer' : 'default' }"
        >{{ templates.find(t => t.id === selectedTemplate)?.name || '未命名文档' }}</span>
      </div>
      <div class="header-right">
          <el-dropdown @command="handleTemplateCommand" trigger="click">
            <el-button class="btn-save-template">
              保存模板<el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="save">保存</el-dropdown-item>
                <el-dropdown-item command="saveAs">另存为</el-dropdown-item>
                <el-dropdown-item divided command="exportTpl">导出模板文件</el-dropdown-item>
                <el-dropdown-item command="importTpl">导入模板文件</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-dropdown @command="handleExportCommand">
            <el-button class="btn-export">
              导出文档<el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="word">导出 Word</el-dropdown-item>
                <el-dropdown-item command="pdf">导出 PDF</el-dropdown-item>
                <el-dropdown-item command="image">导出图片</el-dropdown-item>
                <el-dropdown-item command="longImage">导出长图</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        <el-button type="primary" class="btn-backfill" @click="showBackfillDialog = true">一键回填</el-button>
      </div>
    </header>

    <main class="editor-container">
      <div class="sidebar-left">
        <div class="sidebar-section flex-1 overflow-hidden">
          <FieldList 
            :is-readonly="false"
            :template-name="templates.find(t => t.id === selectedTemplate)?.name || '未命名模板'"
            @insert-field="handleInsertField" 
          >
            <template #header>
              <div class="section-header">
                <h3>预览记录</h3>
                <el-button link type="primary" @click="loadRecordList" :loading="isLoadingRecords">刷新</el-button>
              </div>
              <el-select v-model="selectedRecordId" placeholder="预览数据记录" class="record-selector">
                <el-option v-for="r in recordList" :key="r.id" :label="r.title" :value="r.id" />
              </el-select>
            </template>
          </FieldList>
        </div>
      </div>

      <div class="editor-main">
        <Editor
          ref="editorRef"
          v-model="editorContent"
          :record-data="currentRowData"
          :field-name-to-id-map="fieldNameToIdMap"
          :field-types="fieldTypes"
          :available-field-names="availableFieldNames"
          @open-signature="handleOpenSignaturePad"
        />
      </div>
    </main>

    <!-- 回填弹窗 -->
    <el-dialog v-model="showBackfillDialog" title="一键回填到多维表格" width="500px">
      <el-form label-position="top">
        <el-form-item label="回填字段 (附件类型)">
          <el-select v-model="targetFieldId" placeholder="请选择附件字段" class="w-full">
            <el-option v-for="f in attachmentFields" :key="f.id" :label="f.name" :value="f.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="导出格式">
          <el-radio-group v-model="backfillFormat">
            <el-radio label="word">Word</el-radio>
            <el-radio label="pdf">PDF</el-radio>
            <el-radio label="image">图片</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <!-- 记录选择列表 -->
        <el-form-item label="选择记录">
          <div class="record-select-container" style="width: 100%;">
            <!-- 操作栏 -->
            <div class="backfill-toolbar">
              <el-checkbox 
                :indeterminate="selectedRecordIdsForBackfill.length > 0 && selectedRecordIdsForBackfill.length < recordList.filter(r => r.id !== '__placeholder__').length"
                :model-value="selectedRecordIdsForBackfill.length > 0 && selectedRecordIdsForBackfill.length === recordList.filter(r => r.id !== '__placeholder__').length"
                @change="(val: any) => {
                  if (val) {
                    selectedRecordIdsForBackfill = recordList.filter(r => r.id !== '__placeholder__').map(r => r.id);
                  } else {
                    selectedRecordIdsForBackfill = [];
                  }
                }"
              >
                全选
              </el-checkbox>
              <div class="text-xs text-gray-500">
                已选 <span class="text-primary font-bold">{{ selectedRecordIdsForBackfill.length }}</span> / {{ recordList.filter(r => r.id !== '__placeholder__').length }}
              </div>
            </div>
            
            <!-- 范围输入 -->
            <div class="range-input-row">
              <el-input
                v-model="backfillRangeInput"
                placeholder="输入范围，如 1-30 或 1,3,5-10"
                size="small"
                clearable
                @clear="selectedRecordIdsForBackfill = []"
              >
                <template #prepend>范围</template>
              </el-input>
              <el-button size="small" type="primary" @click="applyBackfillRange">应用</el-button>
            </div>
            
            <!-- 列表区域 -->
            <div class="record-select-list custom-scrollbar">
              <el-checkbox-group v-model="selectedRecordIdsForBackfill">
                <div class="grid-layout">
                  <div v-for="record in recordList.filter(r => r.id !== '__placeholder__')" :key="record.id" class="grid-item">
                    <el-checkbox :label="record.id" :title="record.title">
                      {{ record.title }}
                    </el-checkbox>
                  </div>
                </div>
              </el-checkbox-group>
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <div v-if="isBackfilling" class="progress-bar">
          <el-progress :percentage="Math.round((backfillProgress.current / backfillProgress.total) * 100)" />
          <el-button @click="cancelBackfill" size="small" type="danger" plain mt-2>取消回填</el-button>
        </div>
        <div v-else>
          <el-button @click="showBackfillDialog = false">取消</el-button>
          <el-button type="primary" @click="handleBackfillConfirm">开始回填</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 签名板 -->
    <SignaturePad
      v-if="showSignaturePad"
      @confirm="handleSignatureConfirm"
      @cancel="showSignaturePad = false"
    />
    
    <!-- 远程签字弹窗 -->
    <SendSignatureDialog
      v-if="showSendSignatureDialog"
      :document-title="templates.find(t => t.id === selectedTemplate)?.name"
      :document-html="editorRef?.getTemplateShellContent() || ''"
      @insert-signature="handleSendSignatureConfirm"
      @close="showSendSignatureDialog = false"
    />

    <!-- 封页设置弹窗 -->
    <el-dialog v-model="coverDialogVisible" title="设置封页" width="600px" append-to-body>
      <div class="cover-settings">
        <!-- 封页类型切换 -->
        <div class="mb-4" style="margin-bottom: 20px;">
          <el-radio-group v-model="coverType">
            <el-radio-button label="preset">预设样式</el-radio-button>
            <el-radio-button label="image">自定义图片</el-radio-button>
          </el-radio-group>
        </div>

        <!-- 预设选择 -->
        <div v-if="coverType === 'preset'" class="preset-list" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; padding: 4px;">
           <!-- 商务风格 -->
           <div class="preset-item" 
                :class="{ active: coverPreset === 'business' }"
                @click="coverPreset = 'business'">
              <div class="preset-preview business-preview">
                <div class="mini-header-line"></div>
                <div class="mini-title"></div>
                <div class="mini-meta-group">
                  <div class="mini-meta"></div>
                  <div class="mini-meta"></div>
                </div>
              </div>
              <div class="preset-name">商务风格</div>
              <div class="selection-check" v-if="coverPreset === 'business'"><el-icon><Select /></el-icon></div>
           </div>

           <!-- 现代简约 -->
           <div class="preset-item" 
                :class="{ active: coverPreset === 'modern' }"
                @click="coverPreset = 'modern'">
              <div class="preset-preview modern-preview">
                 <div class="mini-accent-bar"></div>
                 <div class="mini-content-col">
                    <div class="mini-title-lg"></div>
                    <div class="mini-sub"></div>
                 </div>
              </div>
              <div class="preset-name">现代简约</div>
              <div class="selection-check" v-if="coverPreset === 'modern'"><el-icon><Select /></el-icon></div>
           </div>

           <!-- 极简线条 -->
           <div class="preset-item" 
                :class="{ active: coverPreset === 'simple' }"
                @click="coverPreset = 'simple'">
              <div class="preset-preview simple-preview">
                 <div class="mini-border-box">
                    <div class="mini-center-title"></div>
                 </div>
                 <div class="mini-btm-text"></div>
              </div>
              <div class="preset-name">极简线条</div>
              <div class="selection-check" v-if="coverPreset === 'simple'"><el-icon><Select /></el-icon></div>
           </div>
        </div>

        <!-- 图片上传 -->
        <div v-else class="image-upload-container">
           <el-upload
              class="avatar-uploader"
              drag
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handleCoverImageUpload"
            >
              <div v-if="coverImageUrl" class="preview-image-wrapper">
                 <img :src="coverImageUrl" class="cover-image-preview" />
                 <div class="reupload-mask">
                    <el-icon><Upload /></el-icon>
                    <span>更换图片</span>
                 </div>
              </div>
              <div v-else class="upload-placeholder">
                 <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                 <div class="el-upload__text">
                    将文件拖到此处，或 <em>点击上传</em>
                 </div>
                 <div class="el-upload__tip">支持 JPG/PNG，建议尺寸 A4 (210x297mm)</div>
              </div>
            </el-upload>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer" style="display: flex; justify-content: space-between;">
           <el-button type="danger" plain @click="handleRemoveCover">移除封页</el-button>
           <div>
              <el-button @click="coverDialogVisible = false">取消</el-button>
              <el-button type="primary" @click="handleApplyCover">插入/更新</el-button>
           </div>
        </div>
      </template>
    </el-dialog>
    <!-- 插入二维码/条形码弹窗 -->
    <el-dialog v-model="insertCodeDialogVisible" :title="insertCodeType === 'qrcode' ? '插入二维码' : '插入条形码'" width="480px" append-to-body>
      <el-form label-position="top">
        <el-form-item label="内容来源">
          <el-radio-group v-model="insertCodeForm.source">
            <el-radio-button label="custom">自定义内容</el-radio-button>
            <el-radio-button label="field">绑定字段</el-radio-button>
          </el-radio-group>
        </el-form-item>
        
        <template v-if="insertCodeForm.source === 'custom'">
          <el-form-item :label="insertCodeType === 'qrcode' ? '二维码内容 (URL 或文本)' : '条形码内容 (仅支持英文、数字)'">
            <el-input v-model="insertCodeForm.text" :placeholder="insertCodeType === 'qrcode' ? '请输入...' : '例如: NO.123456'" />
          </el-form-item>
        </template>
        
        <template v-else>
          <el-form-item label="选择字段">
            <el-select v-model="insertCodeForm.field" placeholder="请选择字段" filterable class="w-full">
              <el-option 
                v-for="name in availableFieldNames.filter(f => {
                   if (insertCodeType === 'qrcode') return true; 
                   // Filter logic for barcode (CODE128 only supports ASCII):
                   if (insertCodeType === 'barcode') {
                      const type = fieldTypes[f];
                      // Only allow field types whose values are reliably ASCII:
                      // 1=Text, 2=Number, 13=Phone, 15=Url, 1005=AutoNumber
                      const allowed = [1, 2, 13, 15, 1005]; 
                      return type !== undefined ? allowed.includes(type) : true;
                   }
                   return true;
                })" 
                :key="name" 
                :label="name" 
                :value="name" 
              />
            </el-select>
          </el-form-item>
        </template>
        
        <div class="flex gap-4">
          <el-form-item label="宽度 (px)" class="flex-1">
            <el-input-number v-model="insertCodeForm.width" :min="20" :max="500" controls-position="right" class="w-full" />
          </el-form-item>
          <el-form-item label="高度 (px)" class="flex-1">
             <el-input-number v-model="insertCodeForm.height" :min="20" :max="500" controls-position="right" class="w-full" />
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="insertCodeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleInsertCodeConfirm">插入</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.editor-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8fafc;
}

.page-header {
  height: 60px;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  z-index: 100;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1; /* 允许占据剩余空间 */
  min-width: 0; /* 允许 flex item 缩小 */
  white-space: nowrap; /* 防止换行 */
  overflow: hidden;
}

.document-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding: 2px 6px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.document-title:hover {
  background-color: #f1f5f9;
}

/* 响应式适配：窄屏下隐藏部分文字 */
@media (max-width: 768px) {
  .btn-home span, .btn-export span {
    display: none; /* 隐藏按钮文字，只留图标 */
  }
  .page-header {
    padding: 0 10px;
  }
}

.editor-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sidebar-left {
  width: 180px;
  background: white;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  padding: 4px;
  gap: 4px;
}

.sidebar-section h3 {
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.editor-main {
  flex: 1;
  padding: 0;
  overflow-y: auto;
  display: flex;
  justify-content: center;
}

.w-full { width: 100%; }
.flex-1 { flex: 1; }
.overflow-hidden { overflow: hidden; }


.backfill-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding: 0 4px;
}

.range-input-row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.range-input-row .el-input {
  flex: 1;
}

.record-select-list {
  background-color: #fafafa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 12px;
  max-height: 240px;
  overflow-y: auto;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}

.grid-layout {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px 12px;
}

.grid-item {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.text-primary {
  color: #3370ff;
}

.font-bold {
  font-weight: 600;
}

.mb-2 { margin-bottom: 8px; }
.px-1 { padding-left: 4px; padding-right: 4px; }
.flex { display: flex; }
.justify-between { justify-content: space-between; }
.items-center { align-items: center; }
.text-xs { font-size: 12px; }

/* 滚动条样式 */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #f5f7fa;
}

:deep(.el-button--primary) { background-color: #0f172a; border-color: #0f172a; }
:deep(.el-button--primary:hover) { background-color: #1e293b; border-color: #1e293b; }

/* 封页设置弹窗样式 */
.preset-list {
  user-select: none;
}

.preset-item {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  background: white;
}

.preset-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border-color: #cbd5e1;
}

.preset-item.active {
  border-color: #3b82f6;
  box-shadow: 0 0 0 1px #3b82f6;
  background-color: #eff6ff;
}

.preset-name {
  text-align: center;
  padding: 8px 0;
  font-size: 13px;
  color: #475569;
  font-weight: 500;
  border-top: 1px solid #f1f5f9;
}

.preset-item.active .preset-name {
  color: #2563eb;
  background-color: #dbeafe;
  border-top-color: #bfdbfe;
}

.selection-check {
  position: absolute;
  top: 6px;
  right: 6px;
  background: #3b82f6;
  color: white;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

/* 缩略图通用样式 */
.preset-preview {
  height: 140px;
  background: white;
  position: relative;
  overflow: hidden;
  padding: 12px;
  box-sizing: border-box;
}

/* Business Style Preview */
.business-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.mini-header-line { width: 100%; height: 2px; background: #333; margin-bottom: 2px; }
.mini-title { width: 70%; height: 6px; background: #333; margin-top: 25px; margin-bottom: 8px; }
.mini-meta-group { width: 60%; margin-top: auto; margin-bottom: 10px; }
.mini-meta { width: 100%; height: 1px; background: #ddd; margin-bottom: 4px; }

/* Modern Style Preview */
.modern-preview {
  display: flex;
  align-items: center;
  padding-left: 20px;
}
.mini-accent-bar { position: absolute; left: 20px; top: 30px; bottom: 30px; width: 4px; background: #2563eb; }
.mini-content-col { margin-left: 10px; flex: 1; }
.mini-title-lg { width: 80%; height: 12px; background: #333; margin-bottom: 6px; }
.mini-sub { width: 50%; height: 4px; background: #94a3b8; }

/* Simple Style Preview */
.simple-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  padding: 16px;
}
.mini-border-box { border: 2px double #333; padding: 15px 20px; margin-bottom: 15px; }
.mini-center-title { width: 60px; height: 6px; background: #333; }
.mini-btm-text { width: 40px; height: 3px; background: #64748b; }


/* 图片上传样式 */
.image-upload-container {
  padding: 10px;
}
.avatar-uploader .el-upload {
  width: 100%;
}
.avatar-uploader .el-upload-dragger {
  width: 100%;
  height: 280px;
  display: flex;
  justify-content: center;
  align-items: center;
}
.preview-image-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f8fafc;
}
.cover-image-preview {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}
.reupload-mask {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  opacity: 0;
  transition: opacity 0.2s;
  cursor: pointer;
}
.preview-image-wrapper:hover .reupload-mask {
  opacity: 1;
}
.upload-placeholder {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #64748b;
}
.upload-placeholder .el-icon {
  font-size: 48px;
  color: #94a3b8;
  margin-bottom: 10px;
}
</style>