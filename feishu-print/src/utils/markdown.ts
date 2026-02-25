/**
 * Markdown 解析工具
 * 用于检测和解析文本字段中的 Markdown 内容
 */

import { marked } from 'marked';

// 配置 marked
marked.setOptions({
    breaks: true, // 支持换行符转换为 <br>
    gfm: true, // 启用 GitHub 风格的 Markdown
});

/**
 * 检测文本是否包含 Markdown 语法
 * 匹配常见的 Markdown 语法特征
 */
export const isMarkdown = (text: string): boolean => {
    if (!text || typeof text !== 'string') return false;

    // 常见 Markdown 语法正则表达式
    const markdownPatterns = [
        /^#{1,6}\s+/m,           // 标题 # ## ### 等
        /\*\*[^*]+\*\*/,         // 粗体 **text**
        /\*[^*]+\*/,             // 斜体 *text*
        /__[^_]+__/,             // 粗体 __text__
        /_[^_]+_/,               // 斜体 _text_
        /^\s*[-*+]\s+/m,         // 无序列表 - * +
        /^\s*\d+\.\s+/m,         // 有序列表 1. 2. 3.
        /\[.+\]\(.+\)/,          // 链接 [text](url)
        /!\[.*\]\(.+\)/,         // 图片 ![alt](url)
        /`[^`]+`/,               // 行内代码 `code`
        /^```/m,                 // 代码块 ```
        /^\s*>/m,                // 引用 >
        /^\s*---+\s*$/m,         // 水平分割线 ---
        /\|\s*[^|]+\s*\|/,       // 表格 | cell |
    ];

    return markdownPatterns.some(pattern => pattern.test(text));
};

/**
 * 将 Markdown 解析为 HTML
 * 如果检测到 Markdown 语法则解析，否则返回原文本
 */
export const parseMarkdownIfNeeded = (text: string): string => {
    if (!text || typeof text !== 'string') return text || '';

    // 普通文本：只将换行符转为 <br>，不做任何额外处理
    if (!isMarkdown(text)) {
        return text.replace(/\n/g, '<br>');
    }

    try {
        // 解析 Markdown 为 HTML
        let html = marked.parse(text) as string;

        // 移除 marked 自动添加的 <p> 标签包裹（对于单行内容）
        // 这样可以避免在 span 元素中嵌套块级元素
        if (!text.includes('\n') && html.startsWith('<p>') && html.endsWith('</p>\n')) {
            html = html.slice(3, -5);
        }

        return html;
    } catch (error) {
        console.error('Markdown 解析失败:', error);
        return text;
    }
};

/**
 * 强制解析 Markdown（不检测，直接解析）
 */
export const parseMarkdown = (text: string): string => {
    if (!text || typeof text !== 'string') return text || '';

    try {
        return marked.parse(text) as string;
    } catch (error) {
        console.error('Markdown 解析失败:', error);
        return text;
    }
};
