<template>
  <div class="custom-editor-container">
    <textarea :id="editorId"></textarea>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, type PropType } from 'vue';
import type { Editor, RawEditorOptions } from 'tinymce';
import { ElMessage } from 'element-plus';
import QRCode from 'qrcode';
import JsBarcode from 'jsbarcode';
import { FieldType } from '@lark-base-open/js-sdk';

import { styleManager, TEMPLATE_ROOT_STYLE, FIELD_BLOCK_STYLE, LIVE_MAPPING_STYLE } from '@/utils/editor-style-manager';
import { 
  ensureTemplateRoot, enforceTemplateBodyLayout, normalizePageMargin, 
  PAGE_CLASS, PAGE_CONTENT_CLASS, PAGE_BREAK_SELECTOR, PAGE_BREAK_HTML,
  updatePageNumbers, insertNewPageAtCursor, autoPageBreak 
} from '@/utils/editor-dom-utils';
import { useEditorMapping } from '@/composables/useEditorMapping';

// @ts-ignore
declare const tinymce: any;

const props = defineProps({
  recordData: { type: Object as PropType<Record<string, any> | null>, default: null },
  modelValue: { type: String, default: '' },
  id: { type: String, default: () => `tinymce-editor-${Math.random().toString(36).substring(7)}` },
  options: { type: Object as PropType<Partial<RawEditorOptions>>, default: () => ({}) },
  readonly: { type: Boolean, default: false },
  fieldNameToIdMap: { type: Object as PropType<Record<string, string>>, default: () => ({}) },
  fieldTypes: { type: Object as PropType<Record<string, number>>, default: () => ({}) },
  availableFieldNames: { type: Array as PropType<string[]>, default: () => [] }
});

const emit = defineEmits(['update:modelValue']);
const editorId = ref(props.id);
let editorInstance: Editor | null = null;
const pageMargin = ref('10mm');
const showPageNumber = ref(false);
let lastEmittedContent = '';
let isUserEditing = false;
let originalContent = ref('');

const { buildNormalizedMap, restorePlaceholders, applyLiveMapping, findValueByFieldName, scanAndWrapPlaceholders } = useEditorMapping();

// 标志位：插入预映射内容时跳过 restorePlaceholders，防止映射被撤销
let skipRestoreOnNextInsert = false;
// 标志位：applyLiveMapping 执行期间暂停内容发射，防止映射结果触发循环更新
let isMappingInProgress = false;

// --- Dynamic Loader for TinyMCE ---
const loadTinymceScript = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    if (typeof tinymce !== 'undefined') {
      resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = '/tinymce/tinymce.min.js';
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Failed to load TinyMCE'));
    document.head.appendChild(script);
  });
};

// (图片缩放使用 TinyMCE 原生 object_resizing)

// --- TinyMCE setup ---
const setupEditor = (editor: Editor) => {
  editor.on('init', () => {
    styleManager.setEditor(editor);
    styleManager.injectStyle(TEMPLATE_ROOT_STYLE(pageMargin.value), 'base-template-style');
    styleManager.injectStyle(FIELD_BLOCK_STYLE, 'field-block-style');
    styleManager.injectStyle(LIVE_MAPPING_STYLE, 'live-mapping-style');
    
    if (props.modelValue) {
      const styles = styleManager.extractStyles(props.modelValue);
      styleManager.injectMultipleStyles(styles);
    }

    // 点击图片时编程式选中，触发 TinyMCE 显示原生缩放手柄
    // 浮动图片内的 img 不触发选中（由拖拽逻辑处理）
    editor.on('click', (e: any) => {
      const target = e.target as HTMLElement;
      if (target.closest('.floating-image')) return;
      let img: HTMLElement | null = null;
      if (target.nodeName === 'IMG') {
        img = target;
      } else if (target.classList?.contains('mapped-shadow')) {
        img = target.querySelector('img');
      }
      if (img) {
        editor.selection.select(img);
      }
    });

    // 回车换行后重置新段落格式为默认样式（类似 Word 行为）
    editor.on('NewBlock', (e: any) => {
      const newBlock = e.newBlock as HTMLElement;
      if (!newBlock) return;
      // 重置块级格式（对齐等）
      newBlock.style.textAlign = '';
      newBlock.removeAttribute('data-mce-style');
      // 重置内联格式：空新行清除所有格式 span，确保后续输入用默认样式
      const isEmpty = !newBlock.textContent?.trim();
      if (isEmpty) {
        newBlock.innerHTML = '<br data-mce-bogus="1">';
        editor.execCommand('RemoveFormat');
      }
    });

    // 格式命令（字体颜色、背景色等）应用到选区后，将光标移到格式 span 外部
    // 防止后续输入继承已设置的格式
    // 格式命令（字体颜色、背景色等）应用后，将光标移到格式 span 外部
    editor.on('ExecCommand', (e: any) => {
      const FORMAT_COMMANDS = ['ForeColor', 'HiliteColor', 'mceToggleFormat', 'FontSize', 'FontName', 'forecolor', 'hilitecolor'];
      if (!FORMAT_COMMANDS.includes(e.command)) return;
      // 在格式应用后，无论选区是否折叠，都尝试将光标移到格式 span 外部
      const rng = editor.selection.getRng();
      const node = rng.endContainer;
      // 向上查找最近的带样式的 span
      let formatSpan: HTMLElement | null = null;
      let current: HTMLElement | null = node.nodeType === 3 ? node.parentElement : node as HTMLElement;
      while (current && current.nodeName !== 'P' && current.nodeName !== 'DIV' && current.id !== 'tinymce') {
        if (current.nodeName === 'SPAN' && (current.style.color || current.style.backgroundColor || current.style.fontSize || current.style.fontFamily)) {
          formatSpan = current;
          break;
        }
        current = current.parentElement;
      }
      if (formatSpan) {
        const editorDoc = editor.getDoc();
        const zws = editorDoc.createTextNode('\u200B');
        if (formatSpan.nextSibling) {
          formatSpan.parentNode?.insertBefore(zws, formatSpan.nextSibling);
        } else {
          formatSpan.parentNode?.appendChild(zws);
        }
        const newRng = editorDoc.createRange();
        newRng.setStart(zws, 1);
        newRng.collapse(true);
        editor.selection.setRng(newRng);
      }
    });

    // Restore attachment link click handler
    const doc = editor.getDoc();
    if (doc) {
      // --- 浮动图片：拖拽移动 + 四角自由缩放 ---
      let dragTarget: HTMLElement | null = null;
      let dragOffsetX = 0;
      let dragOffsetY = 0;
      // 缩放状态
      let resizeFloat: HTMLElement | null = null; // 被缩放的 .floating-image
      let resizeCorner = ''; // tl | tr | bl | br
      let resizeStartX = 0;
      let resizeStartY = 0;
      let resizeStartW = 0;
      let resizeStartH = 0;
      let resizeStartLeft = 0;
      let resizeStartTop = 0;
      let selectedFloat: HTMLElement | null = null;

      const deselectFloat = () => {
        if (selectedFloat) {
          selectedFloat.classList.remove('fi-selected');
          selectedFloat = null;
        }
      };

      // 确保浮动图片有四个缩放手柄（兼容旧模板导入）
      const ensureHandles = (floatEl: HTMLElement) => {
        if (floatEl.querySelector('.fi-handle')) return;
        ['tl', 'tr', 'bl', 'br'].forEach(c => {
          const h = doc.createElement('div');
          h.className = `fi-handle fi-handle-${c}`;
          h.setAttribute('data-corner', c);
          floatEl.appendChild(h);
        });
      };

      doc.addEventListener('mousedown', (e: MouseEvent) => {
        const target = e.target as HTMLElement;

        // 点击缩放手柄
        if (target.classList?.contains('fi-handle')) {
          e.preventDefault();
          e.stopPropagation();
          const floatEl = target.closest('.floating-image') as HTMLElement;
          const img = floatEl?.querySelector('img') as HTMLImageElement;
          if (!floatEl || !img) return;
          resizeFloat = floatEl;
          resizeCorner = target.getAttribute('data-corner') || 'br';
          resizeStartX = e.clientX;
          resizeStartY = e.clientY;
          resizeStartW = img.offsetWidth;
          resizeStartH = img.offsetHeight;
          resizeStartLeft = floatEl.offsetLeft;
          resizeStartTop = floatEl.offsetTop;
          return;
        }

        // 点击浮动图片容器
        const floatEl = target.closest('.floating-image') as HTMLElement | null;
        if (!floatEl) {
          deselectFloat();
          return;
        }

        e.preventDefault();
        e.stopPropagation();

        // 选中状态
        deselectFloat();
        ensureHandles(floatEl);
        floatEl.classList.add('fi-selected');
        selectedFloat = floatEl;

        // 开始拖拽
        dragTarget = floatEl;
        const rect = floatEl.getBoundingClientRect();
        dragOffsetX = e.clientX - rect.left;
        dragOffsetY = e.clientY - rect.top;
        floatEl.style.opacity = '0.8';
      }, true);

      doc.addEventListener('mousemove', (e: MouseEvent) => {
        // 四角自由缩放
        if (resizeFloat) {
          e.preventDefault();
          const img = resizeFloat.querySelector('img') as HTMLImageElement;
          if (!img) return;
          const dx = e.clientX - resizeStartX;
          const dy = e.clientY - resizeStartY;

          let newW = resizeStartW;
          let newH = resizeStartH;
          let newLeft = resizeStartLeft;
          let newTop = resizeStartTop;

          if (resizeCorner === 'br') {
            newW = resizeStartW + dx;
            newH = resizeStartH + dy;
          } else if (resizeCorner === 'bl') {
            newW = resizeStartW - dx;
            newH = resizeStartH + dy;
            newLeft = resizeStartLeft + dx;
          } else if (resizeCorner === 'tr') {
            newW = resizeStartW + dx;
            newH = resizeStartH - dy;
            newTop = resizeStartTop + dy;
          } else if (resizeCorner === 'tl') {
            newW = resizeStartW - dx;
            newH = resizeStartH - dy;
            newLeft = resizeStartLeft + dx;
            newTop = resizeStartTop + dy;
          }

          newW = Math.max(20, newW);
          newH = Math.max(20, newH);
          img.style.width = newW + 'px';
          img.style.height = newH + 'px';
          resizeFloat.style.left = newLeft + 'px';
          resizeFloat.style.top = newTop + 'px';
          resizeFloat.style.right = '';
          resizeFloat.style.bottom = '';
          return;
        }
        // 拖拽
        if (!dragTarget) return;
        e.preventDefault();
        const parent = dragTarget.offsetParent as HTMLElement || doc.body;
        const parentRect = parent.getBoundingClientRect();
        let newLeft = e.clientX - parentRect.left - dragOffsetX;
        let newTop = e.clientY - parentRect.top - dragOffsetY;
        newLeft = Math.max(0, Math.min(newLeft, parent.clientWidth - dragTarget.offsetWidth));
        newTop = Math.max(0, Math.min(newTop, parent.clientHeight - dragTarget.offsetHeight));
        dragTarget.style.left = newLeft + 'px';
        dragTarget.style.top = newTop + 'px';
        dragTarget.style.right = '';
        dragTarget.style.bottom = '';
      }, true);

      doc.addEventListener('mouseup', () => {
        if (resizeFloat) {
          resizeFloat = null;
          editor.fire('change');
        }
        if (dragTarget) {
          dragTarget.style.opacity = '';
          dragTarget = null;
          editor.fire('change');
        }
      }, true);

      // 选中浮动图片后按 Delete/Backspace 删除
      doc.addEventListener('keydown', (e: KeyboardEvent) => {
        if (!selectedFloat) return;
        if (e.key === 'Delete' || e.key === 'Backspace') {
          e.preventDefault();
          e.stopPropagation();
          selectedFloat.remove();
          selectedFloat = null;
          editor.fire('change');
        }
      }, true);

      // --- 附件链接点击 ---
      const handleEditorClick = (e: MouseEvent) => {
        const target = e.target as Node;
        if (!target) return;
        
        let element: HTMLElement | null = null;
        if (target.nodeType === 1) { // Node.ELEMENT_NODE
          element = target as HTMLElement;
        } else if (target.nodeType === 3) { // Node.TEXT_NODE
          element = target.parentElement;
        }
        
        if (!element || typeof element.closest !== 'function') return;

        const link = element.closest('.attachment-file-link') as HTMLAnchorElement | null;
        if (link && link.href) {
          e.preventDefault();
          e.stopPropagation();
          window.open(link.href, '_blank');
        }
      };
      doc.removeEventListener('click', handleEditorClick, true);
      doc.addEventListener('click', handleEditorClick, true);
    }
  });

  editor.on('BeforeSetContent', (e) => {
    if (skipRestoreOnNextInsert) {
      skipRestoreOnNextInsert = false;
      return;
    }
    
    // 先提取 <style> 标签，注入到 iframe head（TinyMCE 会丢弃 body 中的 style 标签）
    const styleRegex = /<style[^>]*>([\s\S]*?)<\/style>/gi;
    let styleMatch;
    const extractedStyles: string[] = [];
    while ((styleMatch = styleRegex.exec(e.content)) !== null) {
      if (styleMatch[1]?.trim()) {
        extractedStyles.push(styleMatch[1].trim());
      }
    }
    if (extractedStyles.length > 0) {
      styleManager.injectMultipleStyles(extractedStyles, 'imported-style');
    }
    
    e.content = restorePlaceholders(e.content);
  });

  // DOM 结构维护（所有内容变更事件）
  editor.on('SetContent AfterSetContent change input undo redo', () => {
    const doc = editor.getDoc();
    if (doc) {
      // 1. 自动包裹占位符：将纯文本 {$Field} 转换为 <span class="template-field">
      scanAndWrapPlaceholders(doc.body, doc);
      // 2. 确保页面结构
      ensureTemplateRoot(doc);
      enforceTemplateBodyLayout(doc);
      // 3. 自动分页
      autoPageBreak(doc);
      // 4. 显示页码
      if (showPageNumber.value) {
        doc.getElementById('template-root')?.setAttribute('data-show-page-number', '1');
      }
    }
  });

  // undo/redo 后重新映射（在独立 handler 中，确保 ensureTemplateRoot 已执行）
  editor.on('undo redo', () => {
    if (props.recordData && props.fieldNameToIdMap && editorInstance) {
      isMappingInProgress = true;
      editorInstance.undoManager.ignore(() => {
        applyLiveMapping(editorInstance!, props.recordData, props.fieldNameToIdMap);
      });
      lastEmittedContent = editorInstance.getContent();
      isMappingInProgress = false;
    }
  });

  // 内容发射（仅在用户编辑时：change/input，不在程序触发时：setcontent/undo/redo）
  editor.on('change input', () => {
    if (!isUserEditing && !props.readonly && !isMappingInProgress) {
      const content = editor.getContent();
      if (content !== lastEmittedContent) {
        lastEmittedContent = content;
        emit('update:modelValue', content);
      }
    }
  });

  // 监听节点变化，当插入动态条形码/二维码时立即触发映射
  editor.on('NodeChange', () => {
    if (isMappingInProgress || !props.recordData || !props.fieldNameToIdMap) return;
    
    const doc = editor.getDoc();
    const dynamicBarcodes = doc.querySelectorAll('img.dynamic-barcode[data-fieldname]');
    const dynamicQRCodes = doc.querySelectorAll('img.dynamic-qrcode[data-fieldname]');
    
    // 如果发现有占位符（src 是默认的灰色图），立即触发映射
    const hasUnmappedPlaceholders = Array.from([...dynamicBarcodes, ...dynamicQRCodes]).some(img => {
      const src = (img as HTMLImageElement).src || '';
      // 检查是否是我们的默认占位符
      return src.startsWith('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAAAy');
    });
    
    if (hasUnmappedPlaceholders) {
      setTimeout(() => {
        if (editor && props.fieldNameToIdMap) {
          isMappingInProgress = true;
          editor.undoManager.ignore(() => {
            applyLiveMapping(editor, props.recordData, props.fieldNameToIdMap);
          });
          isMappingInProgress = false;
        }
      }, 100);
    }
  });


  // --- Custom Buttons ---
  editor.ui.registry.addMenuButton('paperSizeButton', {
    text: 'A4',
    tooltip: '纸张大小',
    fetch: (cb) => cb([{ type: 'menuitem', text: 'A4 (210mm × 297mm)', onAction: () => {} }])
  });

  editor.ui.registry.addMenuButton('pageMarginButton', {
    text: '页边距',
    fetch: (cb) => cb([
      { type: 'menuitem', text: '默认 (10mm)', onAction: () => editor.execCommand('mceSetPageMargin', false, '10mm') },
      { type: 'menuitem', text: '窄 (5mm)', onAction: () => editor.execCommand('mceSetPageMargin', false, '5mm') },
      { type: 'menuitem', text: '宽 (20mm)', onAction: () => editor.execCommand('mceSetPageMargin', false, '20mm') }
    ])
  });

  editor.addCommand('mceSetPageMargin', (_ui, val) => {
    pageMargin.value = val;
    const doc = editor.getDoc();
    if (doc) {
      doc.getElementById('template-root')?.style.setProperty('--template-page-padding', val);
      doc.querySelectorAll(`.${PAGE_CONTENT_CLASS}`).forEach(el => (el as HTMLElement).style.padding = val);
    }
    emit('update:modelValue', editor.getContent());
  });

  editor.ui.registry.addButton('pagebreakplus', {
    text: '分页',
    onAction: () => insertNewPageAtCursor(editor)
  });

  editor.ui.registry.addToggleButton('pagenumber', {
    text: '页码',
    onAction: (api) => {
      showPageNumber.value = !showPageNumber.value;
      api.setActive(showPageNumber.value);
      const root = editor.getDoc().getElementById('template-root');
      showPageNumber.value ? root?.setAttribute('data-show-page-number', '1') : root?.removeAttribute('data-show-page-number');
    }
  });

  editor.ui.registry.addButton('coverpage', {
    text: '封页',
    tooltip: '设置封页',
    onAction: () => window.dispatchEvent(new CustomEvent('openCoverSettings', { detail: { editor } }))
  });

  editor.ui.registry.addButton('customhr', {
    text: '分隔符',
    tooltip: '插入水平分隔线',
    onAction: () => {
      editor.windowManager.open({
        title: '插入分隔线',
        body: {
          type: 'panel',
          items: [
            {
              type: 'selectbox',
              name: 'style',
              label: '样式',
              items: [
                { value: 'solid', text: '实线' },
                { value: 'dashed', text: '虚线' },
                { value: 'dotted', text: '点线' }
              ]
            },
            {
              type: 'selectbox',
              name: 'width',
              label: '粗细',
              items: [
                { value: '1px', text: '细 (1px)' },
                { value: '2px', text: '中等 (2px)' },
                { value: '3px', text: '粗 (3px)' },
                { value: '5px', text: '很粗 (5px)' }
              ]
            },
            {
              type: 'colorinput',
              name: 'color',
              label: '颜色'
            }
          ]
        },
        initialData: {
          style: 'solid',
          width: '2px',
          color: '#d1d5db'
        },
        buttons: [
          { type: 'cancel', text: '取消' },
          { type: 'submit', text: '插入', primary: true }
        ],
        onSubmit: (api) => {
          const data = api.getData();
          const hrStyle = `border: 0; border-top: ${data.width} ${data.style} ${data.color}; margin: 16px 0;`;
          editor.insertContent(`<hr style="${hrStyle}" />`);
          api.close();
        }
      });
    }
  });



      editor.ui.registry.addButton('qrcode', {
    text: '二维码',
    tooltip: '插入二维码',
    onAction: () => window.dispatchEvent(new CustomEvent('openInsertCodeDialog', { detail: { type: 'qrcode', editor } }))
  });

  editor.ui.registry.addButton('barcode', {
    text: '条形码',
    tooltip: '插入条形码',
    onAction: () => window.dispatchEvent(new CustomEvent('openInsertCodeDialog', { detail: { type: 'barcode', editor } }))
  });

  editor.ui.registry.addMenuButton('signature', {
    text: '签字',
    tooltip: '插入签名',
    fetch: (callback) => {
      const items = [
        {
          type: 'menuitem',
          text: '手写签名',
          onAction: () => window.dispatchEvent(new CustomEvent('openSignaturePad', { detail: { editor } }))
        },
        {
          type: 'menuitem',
          text: '远程签字',
          onAction: () => window.dispatchEvent(new CustomEvent('openSendSignatureDialog', { detail: { editor } }))
        }
      ] as any;
      callback(items);
    }
  });

  // 浮动图片：插入可自由拖拽定位的图片（用于 logo、印章等）
  editor.ui.registry.addButton('floatimage', {
    text: '浮动图片',
    tooltip: '插入可自由移动的图片（如企业Logo）',
    onAction: () => {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = 'image/*';
      input.onchange = () => {
        const file = input.files?.[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = () => {
          const src = reader.result as string;
          // 插入浮动图片容器：absolute 定位，可拖拽
          const html = `<div class="floating-image" contenteditable="false" style="position: absolute; top: 10px; right: 10px; z-index: 10; cursor: move;" data-mce-resize="false"><img src="${src}" style="width: 150px; display: block;" /><div class="fi-handle fi-handle-tl" data-corner="tl"></div><div class="fi-handle fi-handle-tr" data-corner="tr"></div><div class="fi-handle fi-handle-bl" data-corner="bl"></div><div class="fi-handle fi-handle-br" data-corner="br"></div></div>`;
          editor.insertContent(html);
          editor.fire('change');
        };
        reader.readAsDataURL(file);
      };
      input.click();
    }
  });

  // 首行缩进 2 字符切换按钮
  editor.ui.registry.addToggleButton('textindent', {
    text: '首行缩进',
    tooltip: '首行缩进 2 字符',
    onAction: (api) => {
      const node = editor.selection.getNode();
      const block = editor.dom.getParent(node, 'p,div,li,h1,h2,h3,h4,h5,h6') as HTMLElement | null;
      if (!block) return;

      const current = block.style.textIndent;
      if (current && current !== '0px' && current !== '0em') {
        block.style.textIndent = '';
        api.setActive(false);
      } else {
        block.style.textIndent = '2em';
        api.setActive(true);
      }
      editor.fire('change');
    },
    onSetup: (api) => {
      const updateState = () => {
        const node = editor.selection.getNode();
        const block = editor.dom.getParent(node, 'p,div,li,h1,h2,h3,h4,h5,h6') as HTMLElement | null;
        const indent = block?.style.textIndent || '';
        api.setActive(!!indent && indent !== '0px' && indent !== '0em');
      };
      editor.on('NodeChange', updateState);
      return () => editor.off('NodeChange', updateState);
    }
  });
};

const defaultConfig: RawEditorOptions = {
  menubar: false,
  plugins: [
    'autosave', 'charmap', 'fullscreen', 'image', 'insertdatetime', 'lists', 'code',
    'nonbreaking', 'pagebreak', 'preview', 'save', 'searchreplace',
    'table', 'visualblocks', 'visualchars', 'link', 'help', 'wordcount', 'advlist', 'autolink', 'emoticons'
  ].join(' '),
  toolbar_mode: 'wrap', // 自动换行，避免隐藏功能
  toolbar: [
    'undo redo | fontfamily fontsize | bold italic underline strikethrough forecolor backcolor | align lineheight | bullist numlist indent outdent textindent',
    'table tableinsertrowbefore tableinsertrowafter tabledeleterow tableinsertcolbefore tableinsertcolafter tabledeletecol | charmap insertdatetime customhr link',
    'paperSizeButton pageMarginButton paperWatermark | coverpage pagebreakplus pagenumber | qrcode barcode signature floatimage code | fullscreen preview print'
  ].join(' | '), // 使用 join 合并为单行字符串，避免强制分行显示导致过高
  language: 'zh_CN',
  height: '100%',
  branding: false,
  font_css: './src/assets/myFont.css',
  font_family_formats: '微软雅黑=微软雅黑;方正小标宋简体=方正小标宋简体;宋体=宋体;仿宋=仿宋;黑体=黑体;楷体=楷体;Arial=Arial;sans-serif=Sans-serif;Times New Roman=Times New Roman;',
  table_column_resizing: 'preservetable',
  table_sizing_mode: 'relative',
  table_responsive_width: true,
  resize: false,
  lineheight_formats: '1 1.1 1.2 1.3 1.4 1.5 2 2.5 3 4 5',
  line_height_formats: '1 1.1 1.2 1.3 1.4 1.5 2 2.5 3 4 5',
  object_resizing: 'img',
  resize_img_proportional: false,
  statusbar: false,
  paste_data_images: true, 
  paste_enable_default_filters: false,
  content_style: `
    body { font-family: sans-serif; font-size: 14px; background: #f1f5f9; padding: 0; }
    p { margin: 0; }
    #tinymce { display: flex; flex-direction: column; align-items: center; }
    .template-field { padding: 0 2px; border-radius: 2px; cursor: pointer; }
    .template-field:hover { background-color: rgba(0, 0, 0, 0.05); }
    #template-root[data-show-page-number="1"] .template-page-content:not(.cover-page)::before {
      content: '第 ' attr(data-page) ' / ' attr(data-total-pages) ' 页';
      position: absolute; left: 50%; bottom: 10px; transform: translateX(-50%); font-size: 12px; color: #64748b;
    }
    .attachment-file-link { color: #2563eb !important; text-decoration: underline !important; cursor: pointer !important; }
    img { cursor: default; }
    .floating-image { position: absolute; z-index: 10; cursor: move; user-select: none; border: 2px solid transparent; }
    .floating-image.fi-selected { border-color: #3b82f6; }
    .floating-image:hover { border-color: #93c5fd; }
    .floating-image img { display: block; pointer-events: none; }
    .floating-image .fi-handle { display: none; position: absolute; width: 8px; height: 8px; background: #3b82f6; border: 1px solid #fff; border-radius: 1px; }
    .floating-image.fi-selected .fi-handle { display: block; }
    .floating-image .fi-handle-tl { top: -5px; left: -5px; cursor: nwse-resize; }
    .floating-image .fi-handle-tr { top: -5px; right: -5px; cursor: nesw-resize; }
    .floating-image .fi-handle-bl { bottom: -5px; left: -5px; cursor: nesw-resize; }
    .floating-image .fi-handle-br { bottom: -5px; right: -5px; cursor: nwse-resize; }
    
    ${TEMPLATE_ROOT_STYLE('10mm')}
    ${FIELD_BLOCK_STYLE}
    ${LIVE_MAPPING_STYLE}
  `,
  extended_valid_elements: '+span[class|contenteditable|data-fieldid|data-fieldname|style|id],+hr[style|class],+img[class|src|alt|width|height|style|data-fieldname|crossorigin],+div[class|style|id|contenteditable|data-mce-bogus|data-mce-resize|data-corner|data-page|data-total-pages|data-show-page-number],+p[class|style|data-page|data-total-pages]',
  setup: setupEditor
};

onMounted(async () => {
  try {
    await loadTinymceScript();
  } catch (e) {
    console.error('TinyMCE script load failed:', e);
    return;
  }

  tinymce.init({
    api_key: '1yiqgiknc2aknys03ekamqwx94v2gja6wvpjbt1q21m3zkkw',
    selector: `#${editorId.value}`,
    base_url: '/tinymce',
    suffix: '.min',
    ...defaultConfig,
    ...props.options,
    readonly: props.readonly,
    formats: {
      lineheight: { selector: 'p,h1,h2,h3,h4,h5,h6,ul,ol,li,table', styles: { 'line-height': '%value' } },
      line_height: { selector: 'p,h1,h2,h3,h4,h5,h6,ul,ol,li,table', styles: { 'line-height': '%value' } }
    }
  }).then((editors: any[]) => {
    editorInstance = editors[0];
    
    // 编辑器初始化完成后，如果有记录数据则触发映射
    if (props.recordData && props.fieldNameToIdMap) {
      if (!originalContent.value && editorInstance) originalContent.value = editorInstance.getContent();
      setTimeout(() => {
        if (editorInstance && props.fieldNameToIdMap) {
          isMappingInProgress = true;
          editorInstance.undoManager.ignore(() => {
            applyLiveMapping(editorInstance!, props.recordData, props.fieldNameToIdMap);
          });
          // 映射后重置撤销基线，让映射后的状态成为起点
          editorInstance.undoManager.clear();
          editorInstance.undoManager.add();
          lastEmittedContent = editorInstance.getContent();
          if (editorInstance.getDoc()) {
              autoPageBreak(editorInstance.getDoc()); // 立即检查
              // 图片加载可能延迟，再次检查
              setTimeout(() => autoPageBreak(editorInstance!.getDoc()), 500); 
              setTimeout(() => autoPageBreak(editorInstance!.getDoc()), 1500);
          }
          isMappingInProgress = false;
        }
      }, 50);
    }
  });
});

onUnmounted(() => { if (editorInstance) editorInstance.destroy(); });

// React to external content changes (e.g. template selection)
// 使用 lastEmittedContent 而非 getContent() 来判断是否需要更新
// 防止循环依赖：applyLiveMapping → DOM变化 → emit → watch → setContent → restorePlaceholders → 映射被撤销
watch(() => props.modelValue, (val) => {
  if (editorInstance && !isUserEditing && val !== lastEmittedContent) {
    originalContent.value = val; // Update original content reference
    lastEmittedContent = val; // 同步更新，防止后续事件再次触发
    editorInstance.setContent(val);
    // 模板切换后重置撤销基线，防止 Ctrl+Z 撤回到空内容
    editorInstance.undoManager.clear();
    editorInstance.undoManager.add();
  }
});

// React to mapping data changes (record selection or field map updates)
watch(() => [props.recordData, props.fieldNameToIdMap], async () => {
  if (!editorInstance) {
    return;
  }
  
  // Rebuild cache whenever map changes
  if (props.fieldNameToIdMap) {
      buildNormalizedMap(props.fieldNameToIdMap);
  }

  if (props.recordData) {
    // 保存原始内容
    if (!originalContent.value) originalContent.value = editorInstance.getContent();
    // Use a short delay to ensure DOM is ready
    setTimeout(() => {
        if(editorInstance && props.fieldNameToIdMap) {
            isMappingInProgress = true;
            editorInstance.undoManager.ignore(() => {
                applyLiveMapping(editorInstance!, props.recordData, props.fieldNameToIdMap);
            });
            // 映射后重置撤销基线，让映射后的状态成为起点
            editorInstance.undoManager.clear();
            editorInstance.undoManager.add();
            lastEmittedContent = editorInstance.getContent();
            if (editorInstance.getDoc()) {
                autoPageBreak(editorInstance.getDoc()); // 立即检查
                // 图片加载可能延迟，再次检查
                setTimeout(() => autoPageBreak(editorInstance!.getDoc()), 500); 
                setTimeout(() => autoPageBreak(editorInstance!.getDoc()), 1500);
            }
            isMappingInProgress = false;
        }
    }, 50);
  } else if (!props.recordData) {
    // Clear all mappings if no record selected
    const doc = editorInstance.getDoc();
    if (doc) {
      doc.querySelectorAll('.mapped-shadow').forEach(s => s.remove());
      doc.querySelectorAll('.mapped-shadow-origin').forEach(el => {
          el.classList.remove('mapped-shadow-origin');
          (el as HTMLElement).style.display = '';
      });
      doc.querySelectorAll('.template-field.is-mapped').forEach(el => {
          el.classList.remove('is-mapped');
          (el as HTMLElement).style.display = ''; // Restore visibility
      });
      // 清除映射后也可能导致分页变化（收缩），重新检查分页
      autoPageBreak(doc);
    }
  }
}, { deep: true, immediate: true });

const insertContent = (field: any) => {
  if (editorInstance) {
    // 判断是纯文本还是字段对象
    if (typeof field === 'string') {
      // 纯文本：直接插入（系统字段）
      editorInstance.execCommand('mceInsertContent', false, field);
    } else if (field && field.name) {
      // 字段对象：创建占位符（用户字段）
      const span = document.createElement('span');
      span.className = 'template-field field-block';
      span.setAttribute('contenteditable', 'false');
      span.setAttribute('data-fieldid', field.id);
      span.setAttribute('data-fieldname', field.name);
      span.textContent = `{$${field.name}}`;

      // 如果当前已选择记录，直接查找真实值并一起插入
      if (props.recordData?.fields && props.fieldNameToIdMap) {
        // 确保映射缓存已构建
        buildNormalizedMap(props.fieldNameToIdMap);
        const { value, found } = findValueByFieldName(field.name, props.recordData.fields);
        
        if (found && value && value.trim()) {
          // 隐藏占位符，同时创建 shadow 显示真实值
          span.classList.add('is-mapped');
          span.style.display = 'none';
          
          // 先用简单的 span shadow 插入，后续 applyLiveMapping 会重新处理多段落
          const shadow = document.createElement('span');
          shadow.className = 'mapped-shadow';
          shadow.innerHTML = value;
          const html = `\u200B${span.outerHTML}${shadow.outerHTML}\u200B`;
          
          // 设置标志位，跳过 BeforeSetContent 中的 restorePlaceholders（否则会删除 shadow）
          skipRestoreOnNextInsert = true;
          editorInstance.execCommand('mceInsertContent', false, html);
          // 映射完成后同步 lastEmittedContent，防止 watch 循环
          lastEmittedContent = editorInstance.getContent();
        } else {
          // 字段在记录中没有值，插入隐藏的占位符（与 applyLiveMapping 行为一致）
          span.classList.add('is-mapped');
          span.style.display = 'none';
          const html = `\u200B${span.outerHTML}\u200B`;
          skipRestoreOnNextInsert = true;
          editorInstance.execCommand('mceInsertContent', false, html);
          lastEmittedContent = editorInstance.getContent();
        }
        // 后备：延迟再次 applyLiveMapping 确保所有字段都被映射
        setTimeout(() => {
          if (editorInstance && props.recordData && props.fieldNameToIdMap) {
            isMappingInProgress = true;
            editorInstance.undoManager.ignore(() => {
              applyLiveMapping(editorInstance!, props.recordData!, props.fieldNameToIdMap!);
            });
            lastEmittedContent = editorInstance.getContent();
            isMappingInProgress = false;
          }
        }, 100);
      } else {
        // 未选择记录，正常显示占位符
        const html = `\u200B${span.outerHTML}\u200B`;
        editorInstance.execCommand('mceInsertContent', false, html);
      }
    } else {
      console.warn('[Editor] insertContent 收到无效参数:', field);
    }
  }
};

defineExpose({ 
  insertContent, 
  getTemplateShellContent: () => editorInstance?.getContent() || '',
  getEditorInstance: () => editorInstance,
  applyLiveMapping: (editor: any, record: any, map: any) => applyLiveMapping(editor, record, map)
});
</script>

<style scoped>
.custom-editor-container { position: relative; width: 100%; height: 100%; }
</style>