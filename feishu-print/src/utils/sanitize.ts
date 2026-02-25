import DOMPurify from 'dompurify';

/**
 * 配置 DOMPurify 白名单，允许模板需要的所有标签和属性
 * 只过滤危险标签（script, iframe, object, embed 等）
 */
const ALLOWED_TAGS = [
  'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
  'table', 'tr', 'td', 'th', 'thead', 'tbody', 'tfoot',
  'ul', 'ol', 'li', 'dl', 'dt', 'dd',
  'a', 'img', 'br', 'hr',
  'strong', 'em', 'b', 'i', 'u', 's', 'sub', 'sup',
  'blockquote', 'pre', 'code',
  'style', 'link', 'meta',
  'svg', 'path', 'circle', 'rect', 'line', 'polyline', 'polygon',
  'defs', 'pattern', 'linearGradient', 'radialGradient', 'stop',
  'g', 'text', 'tspan'
];

const ALLOWED_ATTR = [
  'class', 'id', 'style', 'data-*',
  'href', 'src', 'alt', 'title', 'target',
  'width', 'height', 'colspan', 'rowspan',
  'border', 'cellpadding', 'cellspacing', 'align', 'valign',
  'xmlns', 'viewBox', 'fill', 'stroke', 'stroke-width',
  'x', 'y', 'cx', 'cy', 'r', 'd', 'points',
  'x1', 'y1', 'x2', 'y2', 'xlink:href'
];

/**
 * 清理 HTML 内容，防止 XSS 攻击
 * 使用宽松的白名单，允许模板需要的所有标签和属性
 * @param html 原始 HTML 内容
 * @returns 清理后的 HTML 内容
 */
export function sanitizeHtml(html: string): string {
  if (!html) return '';

  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS,
    ALLOWED_ATTR,
    ALLOW_DATA_ATTR: true,
    ALLOW_UNKNOWN_PROTOCOLS: false,
    // 允许 style 标签中的内容
    ALLOWED_URI_REGEXP: /^(?:(?:(?:f|ht)tps?|mailto|tel|callto|sms|cid|xmpp|data):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i,
    // 允许所有 CSS 样式（防止过滤掉分页样式）
    FORBID_TAGS: [],
    FORBID_ATTR: [],
  });
}

/**
 * 检查 HTML 是否包含危险内容
 * @param html HTML 内容
 * @returns 如果包含危险内容返回 true
 */
export function isHtmlDangerous(html: string): boolean {
  if (!html) return false;

  const dangerousPatterns = [
    /<script[\s\S]*?>[\s\S]*?<\/script>/gi,
    /<iframe[\s\S]*?>[\s\S]*?<\/iframe>/gi,
    /<object[\s\S]*?>[\s\S]*?<\/object>/gi,
    /<embed[\s\S]*?>/gi,
    /on\w+\s*=/gi, // 事件处理器
    /javascript:/gi,
    /data:text\/html/gi
  ];

  return dangerousPatterns.some(pattern => pattern.test(html));
}

