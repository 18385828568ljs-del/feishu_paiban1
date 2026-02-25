/**
 * Word 布局优化器 V2
 * 
 * 增强功能：
 * 1. 优先识别子元素的 layout 宽度 (width: xx%)
 * 2. 强制 table-layout: fixed 以防止内容挤压
 * 3. 更好地处理 flex-grow
 */

export function optimizeForWord(html: string): string {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');

    // 1. 处理 Flex 布局
    const flexContainers = Array.from(doc.querySelectorAll('*')).filter(el => {
        const style = el.getAttribute('style') || '';
        const classList = el.classList;
        return (
            style.includes('display: flex') ||
            style.includes('display:flex') ||
            classList.contains('flex') ||
            classList.contains('d-flex') ||
            classList.contains('row')
        );
    }) as HTMLElement[];

    flexContainers.forEach(container => {
        transformFlexToTable(container);
    });

    return doc.body.innerHTML;
}

function transformFlexToTable(container: HTMLElement) {
    if (container.tagName === 'TABLE') return;

    const children = Array.from(container.children) as HTMLElement[];
    if (children.length === 0) return;

    // 创建表格
    const table = document.createElement('table');
    table.setAttribute('width', '100%'); // Word 兼容性更好
    table.style.width = '100%';
    table.style.tableLayout = 'fixed'; // 关键：固定布局，防止内容把单元格撑乱
    table.style.borderCollapse = 'collapse';
    table.style.marginBottom = '0';

    // 继承背景色等样式
    const containerStyle = container.getAttribute('style') || '';
    if (containerStyle.includes('background')) {
        const match = containerStyle.match(/background.*?;/);
        if (match) table.style.cssText += match[0];
    }

    const tr = document.createElement('tr');

    // 预先扫描所有子元素，确定宽度策略
    let totalFlexGrow = 0;
    let hasExplicitWidth = false;

    children.forEach(child => {
        const style = child.getAttribute('style') || '';
        // 检查 width: xx%
        if (style.match(/width:\s*\d+(\.\d+)?%/)) {
            hasExplicitWidth = true;
        }
        // 检查 flex 值
        const flexMatch = style.match(/flex:\s*(\d+)/);
        if (flexMatch) {
            totalFlexGrow += parseInt(flexMatch[1]);
        } else {
            totalFlexGrow += 1; // 默认为 1
        }
    });

    children.forEach(child => {
        const td = document.createElement('td');

        td.style.verticalAlign = 'top';
        td.style.padding = '0';
        td.style.border = 'none'; // 默认无边框

        // --- 宽度计算核心逻辑 ---
        const style = child.getAttribute('style') || '';
        let finalWidth = '';

        // 1. 优先使用显式的百分比宽度
        const widthMatch = style.match(/width:\s*(\d+(\.\d+)?%)/);
        if (widthMatch) {
            finalWidth = widthMatch[1];
        } else {
            // 2. 如果没有显式宽度，则使用 flex 比例
            // 如果 totalFlexGrow 异常（比如都为0），则均分
            let grow = 1;
            const flexMatch = style.match(/flex:\s*(\d+)/);
            if (flexMatch) grow = parseInt(flexMatch[1]);

            // 如果混合了 explicitly width 和 flex，这里可能比较复杂，
            // 简单处理：如果没有 explicit width，就用 flex 比例
            // 如果有 explicit width，那么还是优先用 explicit
            if (!hasExplicitWidth) {
                const percent = (grow / Math.max(totalFlexGrow, 1)) * 100;
                finalWidth = `${percent}%`;
            }
        }

        if (finalWidth) {
            td.style.width = finalWidth;
            td.setAttribute('width', finalWidth); // 增强 Word 兼容
        }

        // 迁移样式：移除 margin，防止破坏表格
        child.style.margin = '0';
        child.style.width = '100%'; // 让内容撑满 TD
        // 移除 box-shadow 等可能引起渲染问题的属性

        td.appendChild(child);
        tr.appendChild(td);
    });

    table.appendChild(tr);

    container.parentNode?.replaceChild(table, container);
}
