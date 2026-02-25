import { saveAs } from 'file-saver';
import { optimizeForWord } from '@/utils/word-layout-optimizer';

/**
 * 内部函数：生成完整的 Word HTML 文档
 * 用于统一 exportWord 和 getWordBlob 的逻辑
 */
function generateWordHtml(
  htmlContent: string,
  filename: string,
  margins: [number, number, number, number]
): string {
  const [top, right, bottom, left] = margins;

  // 0. 预处理 HTML：将 Flex 布局转为 Table 布局以兼容 Word
  let optimizedContent = optimizeForWord(htmlContent);

  // 1. 在每个.template-page后添加Word专用分页符（除了最后一个）
  // 使用DOM解析以确保正确插入
  const parser = new DOMParser();
  const doc = parser.parseFromString(optimizedContent, 'text/html');
  const pages = doc.querySelectorAll('.template-page');

  pages.forEach((page, index) => {
    // 最后一页不需要分页符
    if (index < pages.length - 1) {
      // Word专用分页符：使用br + mso-special-character
      const pageBreak = doc.createElement('br');
      pageBreak.setAttribute('clear', 'all');
      pageBreak.setAttribute('style', 'mso-special-character:line-break;page-break-before:always');
      // 在当前page之后插入
      page.parentNode?.insertBefore(pageBreak, page.nextSibling);
    }
  });

  optimizedContent = doc.body.innerHTML;

  // 2. 构建带有 Office 命名空间的完整 HTML 结构
  return `
    <html xmlns:o='urn:schemas-microsoft-com:office:office' 
          xmlns:w='urn:schemas-microsoft-com:office:word' 
          xmlns='http://www.w3.org/TR/REC-html40'>
      <head>
        <meta charset="utf-8">
        <title>${filename}</title>
        <!--[if gte mso 9]>
        <xml>
          <w:WordDocument>
            <w:View>Print</w:View>
            <w:Zoom>100</w:Zoom>
            <w:DoNotOptimizeForBrowser/>
          </w:WordDocument>
        </xml>
        <![endif]-->
        <style>
          /* 基础字号和字体 */
          html, body {
            font-family: "Microsoft YaHei", "宋体", SimSun, sans-serif;
            font-size: 14px;
          }

          /* 打印设置：强制 A4 纸张和动态边距 */
          @page WordSection1 {
            size: 210mm 297mm;  /* A4 尺寸 */
            margin: ${top}mm ${right}mm ${bottom}mm ${left}mm;
            mso-page-orientation: portrait;  /* 纵向 */
            mso-header-margin: 0mm;
            mso-footer-margin: 0mm;
            mso-paper-source: 0;
          }

          /* 将 div 关联到上面的 @page 设置 */
          div.WordSection1 {
            page: WordSection1;
          }

          /* 表格优化：解决 Word 中边框丢失或变粗的问题 */
          table {
            border-collapse: collapse;
            mso-table-layout-alt: fixed; /* 强制固定布局 */
            mso-padding-alt: 0in 0in 0in 0in;
          }
          td, th {
            /* 确保边框单线显示 */
            mso-border-alt: solid windowtext 0.5pt;
            padding: 3px 5px;
            vertical-align: top;
          }
          
          /* 打印背景色支持 */
          @media print {
            body { 
              -webkit-print-color-adjust: exact; 
              print-color-adjust: exact; 
            }
          }
          
          /* 针对导出内容的特殊覆盖 */
          /* 1. 复位页面容器，使其只是一个流式包裹 */
          .template-page {
            width: 100% !important; 
            margin: 0 !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
          }

          /* 2. 关键优化：移除内容容器的内边距 */
          /* 因为我们已经设置了 Word 的页面边距 (@page margin) ，所以 HTML 内部的 padding 必须清除 */
          /* 否则会出现 双重边距 (Word Margin + Padding) */
          .template-page-content {
             padding: 0 !important;
             width: auto !important;
             margin: 0 !important;
          }
        </style>
      </head>
      <body>
        <!-- 这里的 Wrapper div 非常重要，它定义了一个 Word "节" -->
        <div class="WordSection1">
          ${optimizedContent}
        </div>
      </body>
    </html>
  `;
}

/**
 * 导出 "伪" Word 文档 (MHTML/HTML 黑科技)
 * 优化版：支持动态页边距，将编辑器内边距转换为 Word 页面边距
 *
 * @param htmlContent 编辑器内容的 HTML 字符串
 * @param filename 文件名（不含后缀）
 * @param margins 页边距数组 [上, 右, 下, 左] (单位 mm)，默认 [15, 20, 15, 20]
 */
export async function exportWord(
  htmlContent: string,
  filename: string = '导出文档',
  margins: [number, number, number, number] = [15, 20, 15, 20]
): Promise<void> {
  const fullHtml = generateWordHtml(htmlContent, filename, margins);

  // 2. 创建 Blob
  // application/msword 是最稳妥的 MIME 类型
  const blob = new Blob([fullHtml], { type: 'application/msword;charset=utf-8' });

  // 3. 处理文件名
  // 强制使用 .doc 后缀（.docx 是 XML 压缩包，不能直接放入 HTML 内容）
  // 虽然内容是 HTML，但 .doc 后缀能诱导 Word 打开它
  let downloadFilename = filename;
  if (downloadFilename.endsWith('.docx')) {
    downloadFilename = downloadFilename.slice(0, -5);
  }
  if (!downloadFilename.endsWith('.doc')) {
    downloadFilename += '.doc';
  }

  // 4. 触发下载
  saveAs(blob, downloadFilename);
}

// 兼容旧接口（用于回填功能等）
export async function getWordBlob(
  html: string,
  filename?: string,
  margins: [number, number, number, number] = [15, 20, 15, 20]
): Promise<Blob> {
  const fullHtml = generateWordHtml(html, filename || '导出文档', margins);
  return new Blob([fullHtml], { type: 'application/msword;charset=utf-8' });
}
