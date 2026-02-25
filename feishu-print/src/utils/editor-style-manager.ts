import type { Editor } from 'tinymce';

// 常量样式定义
export const LIVE_MAPPING_STYLE = `
  .template-field.is-mapped {
    display: none !important;
  }
  .mapped-shadow {
    display: inline;
    line-height: inherit;
  }
  p.mapped-shadow {
    display: block;
  }
`;

export const FIELD_BLOCK_STYLE = `
  .template-field.field-block {
    display: inline;
  }
`;

export const TEMPLATE_ROOT_STYLE = (padding: string = '10mm') => `
  #template-root {
    width: 100% !important;
    min-height: 100% !important;
    margin: 0 !important;
    box-sizing: border-box !important;
    background-size: cover !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    display: block !important;
    padding: 0 !important;
  }
  /* 
   * Flattened Structure: .template-page-content acts as the page itself.
   * Original .template-page wrapper is deprecated.
   */
  .template-page {
    /* Deprecated, kept for backward compatibility if needed, but display contents or merge */
    display: contents; 
  }

  .template-page-content {
    /* Page Dimensions & Layout */
    display: block;
    width: 210mm;
    min-height: 297mm;
    /* 不设置 max-height，让内容自由扩展，分页检测使用累计高度法 */
    margin: 20px auto;
    background: #fff;
    border-radius: 2px;
    position: relative;
    box-shadow: 0 0 0 1px #e5e7eb, 0 12px 25px rgba(0,0,0,0.08);
    
    /* Content Padding & Box Model */
    padding: var(--template-page-padding, ${padding}) !important;
    box-sizing: border-box !important;
    
    /* Overflow Handling */
    word-wrap: break-word;
    overflow-wrap: break-word;
    word-break: break-word;
    overflow: visible; /* 允许内容可见，分页逻辑会处理溢出 */
  }

  /* 防止图片和表格撑破版面 */
  .template-page-content img {
    max-width: 100%;
    height: auto;
  }
  .template-page-content table {
    max-width: 100%;
  }
  .template-page-content pre {
    white-space: pre-wrap;
    word-wrap: break-word;
    max-width: 100%;
    overflow-x: hidden;
  }
  
  /* 移除 Markdown 解析后 code 标签的默认背景色 */
  .template-page-content code, .template-page-content pre {
    background-color: transparent;
    padding: 0;
    font-family: inherit;
    font-size: inherit;
    color: inherit;
    border-radius: 0;
    border: none;
    margin: 0;
  }
  
  /* 分页线与页码提示 */
  .mce-pagebreak, .page-break-visual {
    border: 0;
    border-top: 1px dashed #d1d5db;
    margin: 16px 0 24px;
    height: 0;
    position: relative;
    page-break-after: always;
    display: block;
  }
  .mce-pagebreak::after, .page-break-visual::after {
    counter-increment: page;
    content: '分页符 · 第' counter(page) '页';
    position: absolute;
    left: 0;
    top: -10px;
    font-size: 12px;
    color: #6b7280;
    background: #fff;
    padding: 0 8px;
  }

  /* 打印样式 */
  @page { margin: 0; }
  @media print {
    body { background: #fff !important; padding: 0 !important; }
    #tinymce { margin: 0 auto !important; background: transparent !important; }
    #template-root { padding: 0 !important; margin: 0 auto !important; }
    .template-page { box-shadow: none !important; break-inside: avoid; page-break-inside: avoid; margin: 0 !important; }
    .template-page-content { padding: var(--template-page-padding, ${padding}) !important; }
    .page-break-visual { page-break-after: always; }
  }
`;

export class EditorStyleManager {
  private injectedStyles: Map<string, string> = new Map();
  private editor: Editor | null = null;

  constructor(editor: Editor | null) {
    this.editor = editor;
  }

  setEditor(editor: Editor | null) {
    this.editor = editor;
  }

  extractStyles(html: string): string[] {
    if (!html) return [];
    const styles: string[] = [];
    const styleRegex = /<style[^>]*>([\s\S]*?)<\/style>/gi;
    let match;
    while ((match = styleRegex.exec(html)) !== null) {
      const cssText = match[1].trim();
      if (cssText) styles.push(cssText);
    }
    return styles;
  }

  injectStyle(cssText: string, styleId: string): boolean {
    if (!this.editor || !cssText || !cssText.trim()) return false;

    if (this.injectedStyles.get(styleId) === cssText) return false;

    const doc = this.editor.getDoc();
    if (!doc?.head) {
      setTimeout(() => this.injectStyle(cssText, styleId), 50);
      return false;
    }

    const existingStyle = doc.getElementById(styleId);
    if (existingStyle) existingStyle.remove();

    const styleElement = doc.createElement('style');
    styleElement.id = styleId;
    styleElement.textContent = this.scopeStyles(cssText);
    doc.head.appendChild(styleElement);

    this.injectedStyles.set(styleId, cssText);
    return true;
  }

  private scopeStyles(cssText: string): string {
    if (!cssText || !cssText.trim()) return cssText;
    return cssText.replace(/\/\*[\s\S]*?\*\//g, '')
      .replace(/\bbody\s*\{/gi, '#tinymce {')
      .replace(/\bhtml\s*\{/gi, '#tinymce {');
  }

  injectMultipleStyles(styles: string[], baseId: string = 'template-style'): void {
    styles.forEach((css, i) => this.injectStyle(css, `${baseId}-${i}`));
  }

  clearAll(): void {
    const doc = this.editor?.getDoc();
    if (!doc) return;
    this.injectedStyles.forEach((_, id) => doc.getElementById(id)?.remove());
    this.injectedStyles.clear();
  }
}

export const styleManager = new EditorStyleManager(null);
