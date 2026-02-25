import type { Editor } from 'tinymce';

// 扁平化结构：页面即内容容器
export const PAGE_CLASS = 'template-page-content'; // Class for the page itself
export const PAGE_CONTENT_CLASS = 'template-page-content'; // Kept for compatibility/clarity
export const PAGE_BREAK_SELECTOR = '.mce-pagebreak';
export const PAGE_BREAK_CLASS = 'page-break-visual';
export const PAGE_PADDING = '10mm';
export const OLD_PAGE_WRAPPER_CLASS = 'template-page'; // Deprecated wrapper

export const PAGE_BREAK_INLINE_STYLE = [
    'page-break-after: always',
    'break-after: page',
    'border-top: 1px dashed #d1d5db',
    'margin: 16px 0 24px',
    'height: 0',
    'display: block',
    'position: relative',
].join('; ');

export const PAGE_BREAK_HTML = `<div class="mce-pagebreak ${PAGE_BREAK_CLASS}" style="${PAGE_BREAK_INLINE_STYLE}" contenteditable="false" data-mce-bogus="1"></div>`;

export const updatePageNumbers = (doc: Document) => {
    const templateRoot = doc.getElementById('template-root');
    if (!templateRoot) return;
    // 排除封页 (.cover-page)，不计入总页数
    const pages = Array.from(templateRoot.querySelectorAll(`.${PAGE_CLASS}:not(.cover-page)`)) as HTMLElement[];
    const totalPages = pages.length || 1;
    pages.forEach((p, idx) => {
        p.setAttribute('data-page', String(idx + 1));
        p.setAttribute('data-total-pages', String(totalPages));
    });
};

export const removeCoverPage = (editor: Editor | null) => {
    if (!editor) return;
    const doc = editor.getDoc();
    if (!doc) return;
    const templateRoot = doc.getElementById('template-root');
    if (!templateRoot) return;
    const existingCover = templateRoot.querySelector('.cover-page');
    if (existingCover) {
        existingCover.remove();
        updatePageNumbers(doc);
        editor.fire('change');
        editor.undoManager.add();
    }
};

export const insertCoverPage = (editor: Editor | null, options: { type: 'preset' | 'image', value: string }) => {
    if (!editor) return;
    const doc = editor.getDoc();
    if (!doc) return;

    ensureTemplateRoot(doc);
    const templateRoot = doc.getElementById('template-root') as HTMLElement | null;
    if (!templateRoot) return;

    // 先移除旧封页
    const existingCover = templateRoot.querySelector('.cover-page');
    if (existingCover) {
        existingCover.remove();
    }

    // 创建新封页 - 直接使用 template-page-content
    const coverPage = doc.createElement('div');
    coverPage.className = `${PAGE_CLASS} cover-page`;

    // 获取当前页面 Padding 设置
    const currentPadding = templateRoot.getAttribute('data-page-padding') || PAGE_PADDING;

    // 默认样式覆盖
    let customStyle = '';

    if (options.type === 'image') {
        // 图片封面：铺满
        customStyle = `padding: 0 !important; display: flex; justify-content: center; align-items: center; overflow: hidden;`;
        coverPage.innerHTML = `<img src="${options.value}" style="width: 100%; height: 100%; object-fit: cover;" />`;
    } else {
        // 预设模板
        customStyle = `padding: ${currentPadding} !important; display: flex; flex-direction: column; justify-content: space-between;`;

        if (options.value === 'business') {
            coverPage.innerHTML = `
                <!-- Top Header Bar -->
                <div style="width: 100%; height: 20mm; background-color: #1e293b; display: flex; align-items: center; justify-content: flex-end; padding: 0 20mm; box-sizing: border-box;">
                    <span style="color: rgba(255,255,255,0.8); font-size: 14px; letter-spacing: 1px;">COMPANY REPORT</span>
                </div>
                <!-- ... Content ... -->
                <div style="flex: 1; display: flex; flex-direction: column; padding: 20mm 25mm 20mm 25mm;">
                    <div style="margin-top: 30mm; text-align: center;">
                         <div style="display: inline-block; width: 60px; height: 4px; background-color: #3b82f6; margin-bottom: 20px;"></div>
                         <h1 style="font-size: 42px; font-family: 'SimSun', serif; font-weight: bold; color: #1e293b; margin: 0 0 15px 0; line-height: 1.4;">文档标题</h1>
                         <h2 style="font-size: 20px; font-weight: normal; color: #64748b; margin: 0;">副标题或文档说明文本</h2>
                    </div>
                    <div style="flex: 1;"></div>
                    <div style="width: 100%; border-top: 2px solid #e2e8f0; padding-top: 10mm; margin-bottom: 20mm;">
                        <table style="width: 100%; border-collapse: collapse;">
                            ${['编制人', '审核人', '日&emsp;期', '版&emsp;本'].map(label => `
                            <tr>
                                <td style="padding: 12px 0; width: 100px; color: #64748b; font-weight: 500;">${label}</td>
                                <td style="padding: 12px 0; border-bottom: 1px solid #f1f5f9; color: #334155;">${label.includes('期') ? new Date().toLocaleDateString() : (label.includes('本') ? 'v1.0' : '__________')}</td>
                            </tr>`).join('')}
                        </table>
                    </div>
                </div>`;
        } else if (options.value === 'modern') {
            coverPage.innerHTML = `
                 <div style="position: absolute; top: 0; right: 0; width: 35%; height: 100%; background-color: #f8fafc; z-index: -1;"></div>
                 <div style="position: absolute; bottom: 0; left: 0; width: 15%; height: 60%; background-image: radial-gradient(#e2e8f0 1px, transparent 1px); background-size: 20px 20px; z-index: -1; opacity: 0.5;"></div>
                 <div style="width: 100%; height: 100%; padding: 30mm; box-sizing: border-box; display: flex; flex-direction: column; justify-content: center;">
                     
                     <!-- Accent -->
                     <div style="width: 80px; height: 8px; background: linear-gradient(90deg, #2563eb, #60a5fa); margin-bottom: 40px; border-radius: 4px;"></div>
                     
                     <!-- Title -->
                     <h1 style="font-size: 64px; font-weight: 900; color: #0f172a; margin: 0 0 20px 0; letter-spacing: -1px; line-height: 1.1;">DOCUMENT<br><span style="color: #3b82f6;">TITLE</span></h1>
                     
                     <!-- Subtitle -->
                     <div style="font-size: 24px; color: #64748b; font-weight: 300; max-width: 60%; line-height: 1.5;">
                        Subtitle or descriptive text goes here.
                     </div>

                     <div style="margin-top: 80px; display: flex; gap: 40px;">
                        <div>
                            <div style="font-size: 12px; font-weight: 700; color: #94a3b8; letter-spacing: 2px; margin-bottom: 8px;">AUTHOR</div>
                            <div style="font-size: 18px; color: #334155; font-weight: 600;">Full Name</div>
                        </div>
                        <div>
                            <div style="font-size: 12px; font-weight: 700; color: #94a3b8; letter-spacing: 2px; margin-bottom: 8px;">DATE</div>
                            <div style="font-size: 18px; color: #334155; font-weight: 600;">${new Date().toLocaleDateString()}</div>
                        </div>
                     </div>
                 </div>`;
        } else if (options.value === 'simple') {
            coverPage.innerHTML = `
                <div style="width: 100%; height: 100%; padding: 20mm; box-sizing: border-box;">
                    <div style="width: 100%; height: 100%; border: 1px solid #000; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative;">
                        
                        <!-- Inner Border -->
                        <div style="position: absolute; top: 4px; left: 4px; right: 4px; bottom: 4px; border: 1px solid #000;"></div>

                        <!-- Content -->
                        <div style="text-align: center; z-index: 10; padding: 40px; background: white;">
                            <div style="font-size: 16px; letter-spacing: 4px; color: #333; margin-bottom: 20px;">REPORT</div>
                            <h1 style="font-size: 48px; font-family: 'SimSun', serif; margin: 0 0 20px 0; font-weight: normal;">文档封面标题</h1>
                            <div style="width: 40px; height: 1px; background: #000; margin: 0 auto;"></div>
                        </div>

                        <div style="position: absolute; bottom: 30mm; text-align: center; z-index: 10;">
                             <p style="margin: 5px 0; font-size: 14px; font-family: sans-serif;">${new Date().getFullYear()}</p>
                             <p style="margin: 5px 0; font-size: 12px; letter-spacing: 2px;">COMPANY NAME</p>
                        </div>
                    </div>
                </div>`;
        }
    }

    // 应用样式
    // 注意：CSS类负责尺寸和阴影，这里只需覆盖 padding 和 flex
    // 强制赋予必要的 CSS 变量以防万一
    coverPage.style.cssText = customStyle;

    // 插入到最前面
    templateRoot.prepend(coverPage);
    updatePageNumbers(doc);
    editor.fire('change');
    editor.undoManager.add();

    // 聚焦
    if (options.type !== 'image') {
        editor.selection.select(coverPage, true);
        editor.selection.collapse(true);
    }
};

export const ensureTemplateRoot = (doc: Document): HTMLElement | null => {
    if (!doc?.body) return null;

    let templateRoot = doc.getElementById('template-root') as HTMLElement | null;
    if (!templateRoot) {
        templateRoot = doc.createElement('div');
        templateRoot.id = 'template-root';
        templateRoot.classList.add('template-root');
        while (doc.body.firstChild) templateRoot.appendChild(doc.body.firstChild);
        doc.body.appendChild(templateRoot);
    } else {
        templateRoot.classList.add('template-root');
        if (templateRoot.parentElement !== doc.body) {
            templateRoot.remove();
            doc.body.appendChild(templateRoot);
        }
        const nestedRoots = Array.from(templateRoot.querySelectorAll('#template-root')) as HTMLElement[];
        nestedRoots.forEach((nr) => {
            while (nr.firstChild) templateRoot!.insertBefore(nr.firstChild, nr);
            nr.remove();
        });
    }

    // 移除旧的 template-page 包装器，将内容提升 (Flatten)
    // 如果存在旧结构的 template-page，将其 children 移出并删除 wrappers
    const oldWrappers = Array.from(templateRoot.querySelectorAll(`.${OLD_PAGE_WRAPPER_CLASS}:not(.${PAGE_CLASS})`));
    oldWrappers.forEach(wrapper => {
        const content = wrapper.querySelector(`.${PAGE_CONTENT_CLASS}`);
        if (content) {
            wrapper.parentElement?.insertBefore(content, wrapper);
            wrapper.remove();
        } else {
            // 只有 wrapper 没有内容？把 wrapper 变身为 content?
            // 简单起见，移除 wrapper，其子节点移出
            while (wrapper.firstChild) wrapper.parentElement?.insertBefore(wrapper.firstChild, wrapper);
            wrapper.remove();
        }
    });

    templateRoot.style.height = 'auto';
    templateRoot.style.overflow = 'visible';
    templateRoot.style.removeProperty('max-height');

    // 识别或创建页面
    const children = Array.from(templateRoot.children) as HTMLElement[];
    let currentPage: HTMLElement | null = null;
    const pages: HTMLElement[] = [];

    // 第一次遍历：识别现有页面
    children.forEach(child => {
        if (child.classList.contains(PAGE_CLASS)) {
            pages.push(child);
            currentPage = child;
        } else if (child.tagName === 'DIV' && (child.classList.contains('page-break') || (child.style.width && child.style.width.includes('210mm')))) {
            // 可能是未标记的页面
            child.classList.add(PAGE_CLASS);
            pages.push(child);
            currentPage = child;
        } else {
            // 孤儿内容
            if (!currentPage) {
                // 创建第一页
                currentPage = doc.createElement('div');
                currentPage.className = PAGE_CLASS;
                templateRoot!.insertBefore(currentPage, child);
                pages.push(currentPage);
            }
            currentPage.appendChild(child);
        }
    });

    // 如果没有任何内容，创建空页
    if (pages.length === 0) {
        const page = doc.createElement('div');
        page.className = PAGE_CLASS;
        page.setAttribute('data-page', '1');
        templateRoot.appendChild(page);
    }

    updatePageNumbers(doc);
    return templateRoot;
};

export const enforceTemplateBodyLayout = (doc: Document | null) => {
    if (!doc?.head) return;
    let styleEl = doc.getElementById('template-body-style') as HTMLStyleElement | null;
    if (!styleEl) {
        styleEl = doc.createElement('style');
        styleEl.id = 'template-body-style';
        doc.head.appendChild(styleEl);
    }
    styleEl.textContent = `
    body#tinymce { margin: 0 !important; padding: 0 !important; display: flex !important; justify-content: center !important; background: #f5f5f5 !important; }
    body#tinymce > :not(#template-root):not([data-mce-bogus]):not(.mce-visual-caret) { display: none !important; }
  `;
};

export const normalizeSingleMargin = (value: string): string => {
    const raw = (value || '').trim();
    if (!raw) return PAGE_PADDING;
    const matched = raw.match(/^(\d+(?:\.\d+)?)(mm|cm|px|in)?$/i);
    if (matched) {
        const num = parseFloat(matched[1]);
        const unit = (matched[2] || 'mm').toLowerCase();
        if (Number.isNaN(num)) return PAGE_PADDING;
        if (unit === 'cm') return `${+(num * 10).toFixed(2)}mm`;
        if (unit === 'in') return `${+(num * 25.4).toFixed(2)}mm`;
        return `${num}${unit}`;
    }
    return raw;
};

export const normalizePageMargin = (value: string): string => {
    const parts = (value || '').trim().split(/\s+/).filter(Boolean);
    if (parts.length === 0) return PAGE_PADDING;
    if (parts.length === 1) return normalizeSingleMargin(parts[0]);
    const normParts = parts.map(p => normalizeSingleMargin(p));
    let [top, right, bottom, left] = [normParts[0], normParts[1] || normParts[0], normParts[2] || normParts[0], normParts[3] || normParts[1] || normParts[0]];
    return `${top} ${right} ${bottom} ${left}`;
};

// A4 页面内容最大高度（297mm 减去上下 padding）
const A4_HEIGHT_PX = 1122; // 297mm ≈ 1122px at 96dpi

/**
 * 自动分页（扁平化版）：直接检查 template-page-content 是否内容溢出
 */
// Helper to get computed margins
const getMargins = (el: HTMLElement, win: Window) => {
    const style = win.getComputedStyle(el);
    return (parseFloat(style.marginTop) || 0) + (parseFloat(style.marginBottom) || 0);
};

// Deep Split Logic encapsulated
const deepSplitElement = (element: HTMLElement, maxFirstPageHeight: number, doc: Document) => {
    // 基础检查：如果是文本或空元素，无法拆分
    if (!element.hasChildNodes()) return null;

    const children = Array.from(element.children) as HTMLElement[];
    if (children.length === 0) return null; // 纯文本节点暂不处理拆分（复杂且容易破坏格式）

    let splitIndex = -1;
    let accHeight = 0;
    const win = element.ownerDocument.defaultView || window;

    for (let i = 0; i < children.length; i++) {
        const child = children[i];
        const h = child.offsetHeight + getMargins(child, win);
        accHeight += h;
        if (accHeight > maxFirstPageHeight) {
            splitIndex = i;
            break;
        }
    }

    if (splitIndex === -1) return null; // 全部都放得下（理应不该发生，除非 maxFirstPageHeight 极大）

    // 拆分点: children[0...splitIndex-1] 留在当前 element
    // children[splitIndex...] 移动到新 element

    // 如果是第一个子元素就溢出了，尝试递归 Deep Split (只允许一层递归防止过深)
    if (splitIndex === 0) {
        // 递归拆分 children[0]
        // 注意：这里的 maxFirstPageHeight 是剩余高度，对于第一个元素，就是 0 (因为它已经溢出了)
        // 其实逻辑应该是：element 本身在当前页剩余空间中放不下。
        // 但这里 maxFirstPageHeight 是传入的“针对该元素的可用高度”。
        // 如果 splitIndex === 0，说明可用高度连第一个子元素都放不下。
        // 我们应该把 element 整个移走吗？
        // 不，deepSplit 是为了解决“element 已经是当前页第一个元素”的情况。
        // 如果 element 是当前页第一个元素，且 children[0] 也溢出...
        // 那只能继续 deepSplit children[0]。
        // 但为了简单，暂时只支持一层 Deep Split。如果连第一个子元素都放不下，就强制切分（move whole element or brute force split）。
        // 简单策略：如果 splitIndex === 0，说明没有任何子元素能放下。将整个 element 标记为不可拆分，或者强行切分 text node（暂不支持）。
        // 实际上，如果 element 是 Page 的第一个元素，children[0] 也是第一个，那么 children[0] 必然溢出。
        // 这时应该 split children[0] 内部。
        // TODO: 进一步递归。现在先返回 null，由外层决定（移动整个 element 到下一页，如果已经是新页则允许溢出）。
        return null;
    }

    // 创建新容器（浅克隆）
    const newElement = element.cloneNode(false) as HTMLElement;
    // 移除 id 避免重复
    newElement.removeAttribute('id');

    // 移动溢出的子元素
    const moveChildren = children.slice(splitIndex);
    for (const child of moveChildren) {
        newElement.appendChild(child);
    }

    return newElement;
};

export const autoPageBreak = (doc: Document) => {
    const templateRoot = doc.getElementById('template-root') as HTMLElement | null;
    console.log('[AutoPageBreak] Called. templateRoot:', !!templateRoot);
    if (!templateRoot) return;

    let hasSplit = true;
    let loopCount = 0;
    const MAX_LOOPS = 50;

    while (hasSplit && loopCount < MAX_LOOPS) {
        hasSplit = false;
        loopCount++;

        const pages = Array.from(templateRoot.querySelectorAll(`:scope > .${PAGE_CLASS}:not(.cover-page)`)) as HTMLElement[];
        console.log(`[AutoPageBreak] Loop ${loopCount}, Found ${pages.length} pages.`);

        for (let pageIdx = 0; pageIdx < pages.length; pageIdx++) {
            const page = pages[pageIdx];
            const pageContent = page;
            const win = pageContent.ownerDocument.defaultView || window;

            const children = Array.from(pageContent.children) as HTMLElement[];
            if (children.length === 0) continue;

            // 计算页面内容区域最大高度
            const style = win.getComputedStyle(pageContent);
            const paddingTop = parseFloat(style.paddingTop) || 0;
            const paddingBottom = parseFloat(style.paddingBottom) || 0;
            const maxContentHeight = A4_HEIGHT_PX - paddingTop - paddingBottom - 4;

            // 使用累积高度法检测溢出（不依赖 scrollHeight/clientHeight）
            let accHeight = 0;
            let splitIndex = -1;

            for (let i = 0; i < children.length; i++) {
                const child = children[i];
                const h = child.offsetHeight + getMargins(child, win);
                accHeight += h;

                if (accHeight > maxContentHeight) {
                    splitIndex = i;
                    console.log(`[AutoPageBreak] Page ${pageIdx}: Overflow at child ${i}, accHeight=${accHeight}, max=${maxContentHeight}`);
                    break;
                }
            }

            // 没有溢出
            if (splitIndex === -1) {
                console.log(`[AutoPageBreak] Page ${pageIdx}: No overflow, accHeight=${accHeight}, max=${maxContentHeight}`);
                continue;
            }

            // 拆分处理
            const newPage = doc.createElement('div');
            newPage.className = PAGE_CLASS;
            // 继承当前页面的 inline padding (如果存在)
            if (pageContent.style.padding) newPage.style.padding = pageContent.style.padding;

            // 情况 1: 第一个元素就溢出了 (splitIndex === 0)
            if (splitIndex === 0) {
                // 必须尝试 Deep Split 第一个元素
                const childToSplit = children[0];
                // 剩余可用高度就是 maxContentHeight (因为是第一个)
                // 实际上是 child 自身高度 vs maxContentHeight
                // 尝试拆分 childToSplit
                const splitResult = deepSplitElement(childToSplit, maxContentHeight, doc);

                if (splitResult) {
                    // 拆分成功：当前页保留 childToSplit (已裁切)，新页放入 splitResult
                    newPage.appendChild(splitResult);
                    // 同时把剩下的 siblings 也移过去
                    const remainingSiblings = children.slice(1);
                    for (const sib of remainingSiblings) newPage.appendChild(sib);

                    page.insertAdjacentElement('afterend', newPage);
                    hasSplit = true;
                    break; // Restart loop
                } else {
                    // 拆分失败（无法拆分）：
                    // 如果这是第一页（或前一页有内容），我们可以把整个 block 移到下一页试试？
                    // 检查 page 是否已经是“新页”（即除了这个 block 没别的）?
                    // 如何判断？ page.previousElementSibling 是 page class，且 page children count == 1?
                    // 或者 simpler: 如果 children.length > 1 (即后面还有东西)，那至少把后面东西移走，让 index 0 独占一页溢出。
                    if (children.length > 1) {
                        // 将 1...end 移到下一页
                        const moveChildren = children.slice(1);
                        for (const child of moveChildren) newPage.appendChild(child);
                        page.insertAdjacentElement('afterend', newPage);
                        hasSplit = true;
                        break;
                    }
                    // 如果 children.length == 1，且无法 deep split，那就只能让它溢出了。
                    // 防止无限循环：不 hasSplit.
                    continue;
                }
            } else {
                // 情况 2: 普通拆分 (splitIndex > 0)
                // 将 children[splitIndex...] 移到新页
                // 这里也可以优化：如果 children[splitIndex] 本身很大，移过去后在新页也会通过 splitIndex=0 逻辑被 Deep Split。
                // 所以直接移动即可。
                const moveChildren = children.slice(splitIndex);
                for (const child of moveChildren) {
                    newPage.appendChild(child);
                }
                page.insertAdjacentElement('afterend', newPage);
                hasSplit = true;
                break;
            }
        }
    }
    updatePageNumbers(doc);
};

export const insertNewPageAtCursor = (editor: Editor | null) => {
    if (!editor) return;
    const doc = editor.getDoc();
    if (!doc) return;

    ensureTemplateRoot(doc);
    const templateRoot = doc.getElementById('template-root') as HTMLElement | null;
    if (!templateRoot) return;

    // 扁平化逻辑：直接查找 template-page-content
    const currentRng = editor.selection?.getRng();

    // ... 如果没有选区或选区不在 root 内，聚焦第一个页面 ...
    if (!currentRng || !templateRoot.contains(currentRng.startContainer)) {
        const firstPage = templateRoot.querySelector(`.${PAGE_CLASS}`) as HTMLElement | null;
        if (firstPage) {
            editor.selection?.select(firstPage, true);
            editor.selection?.collapse(false);
        }
    }

    const rng = editor.selection?.getRng();
    if (!rng) return;

    const markerId = `__page_split_${Date.now()}__`;
    const marker = doc.createElement('span');
    marker.id = markerId;
    marker.setAttribute('data-mce-bogus', '1');
    marker.style.cssText = 'display:inline-block;width:0;height:0;overflow:hidden;';
    rng.insertNode(marker);

    const markerEl = doc.getElementById(markerId);
    const currentPage = markerEl?.closest(`.${PAGE_CLASS}`) as HTMLElement | null;

    if (!markerEl || !currentPage) {
        markerEl?.remove();
        return;
    }

    // 创建新页面
    const newPage = doc.createElement('div');
    newPage.className = PAGE_CLASS;
    // 继承 padding
    if (currentPage.style.padding) newPage.style.padding = currentPage.style.padding;

    templateRoot.insertBefore(newPage, currentPage.nextSibling);

    // 移动内容
    const rangeToEnd = doc.createRange();
    rangeToEnd.setStartAfter(markerEl);
    if (currentPage.lastChild) rangeToEnd.setEndAfter(currentPage.lastChild);
    else rangeToEnd.setEnd(currentPage, 0);

    const extracted = rangeToEnd.extractContents();
    newPage.appendChild(extracted);

    markerEl.remove();
    updatePageNumbers(doc);
    editor.undoManager?.add?.();
    editor.nodeChanged?.();

    if (newPage) {
        editor.selection?.select(newPage, true);
        editor.selection?.collapse(true);
    }
};
