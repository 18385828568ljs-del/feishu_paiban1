import { ref } from 'vue';
import type { Editor } from 'tinymce';
import dayjs from 'dayjs';
import QRCode from 'qrcode';
import JsBarcode from 'jsbarcode';

export const useEditorMapping = () => {
    const normalizedMapCache = ref<Record<string, string>>({});
    const currentMap = ref<Record<string, string>>({});

    const normalizeString = (str: string): string => {
        return str.trim().toLowerCase().replace(/\s+/g, ' ');
    };

    const buildNormalizedMap = (map: Record<string, string>) => {
        currentMap.value = map;
        const cache: Record<string, string> = {};
        Object.entries(map).forEach(([name, id]) => {
            cache[normalizeString(name)] = id;
        });
        normalizedMapCache.value = cache;
    };

    // 将单个对象提取为可读文本
    const extractObjectText = (obj: any): string => {
        if (!obj || typeof obj !== 'object') return String(obj ?? '');
        // IOpenSegment (多行文本段): {type, text, link?}
        if (obj.text !== undefined) return obj.link ? `${obj.text}` : String(obj.text);
        // IOpenUser / IOpenGroupChat: {id, name, enName, ...}
        if (obj.name) return String(obj.name);
        if (obj.enName || obj.en_name) return String(obj.enName || obj.en_name);
        // IOpenLocation: {fullAddress, address, name, ...}
        if (obj.fullAddress || obj.full_address) return String(obj.fullAddress || obj.full_address);
        // IOpenLink (关联): {text, recordIds, tableId}
        if (obj.recordIds || obj.record_ids) return obj.text ? String(obj.text) : '';
        // IOpenAutoNumber (自动编号): ISelfCalculationValue<string> → {type, value}
        if (obj.value !== undefined) return String(obj.value);
        // 兜底：取第一个非空字符串值
        const strVals = Object.values(obj).filter(v => typeof v === 'string' && v.length > 0);
        return strVals.length > 0 ? String(strVals[0]) : '';
    };

    const getFieldValue = (fieldCell: any): string => {
        if (fieldCell === null || fieldCell === undefined) return '';

        // 换行处理：将每行文本转为独立的 <p> 标签，与手动输入 Enter 产生的段落结构一致
        const textToParagraphs = (text: string): string => {
            const lines = text.split('\n');
            if (lines.length <= 1) return text; // 单行直接返回
            return lines
                .map(line => `<p>${line || '<br>'}</p>`)
                .join('');
        };

        // 字符串 (多行文本/电话/邮箱/条码等)
        if (typeof fieldCell === 'string') return textToParagraphs(fieldCell);

        // 数字 (数字/进度/评分/货币/时间戳)
        if (typeof fieldCell === 'number') {
            if (String(fieldCell).length === 13) return dayjs(fieldCell).format('YYYY/MM/DD HH:mm');
            return String(fieldCell);
        }

        // 布尔 (复选框)
        if (typeof fieldCell === 'boolean') return fieldCell ? '是' : '否';

        // 数组 (多选/人员/附件/多行文本段/群组/关联/Lookup/Formula等)
        if (Array.isArray(fieldCell)) {
            if (fieldCell.length === 0) return '';
            // 附件: [{token, name, type, size, ...}]
            const hasAttachments = fieldCell.some(item => item && typeof item === 'object' && item.token && item.size !== undefined);
            if (hasAttachments) {
                return fieldCell.filter(Boolean).map(item => {
                    const url = item.tmp_url || item.url || `https://open.feishu.cn/open-apis/drive/v1/medias/${item.token}/download`;
                    const isImage = (item.type && item.type.startsWith('image/')) || /\.(jpg|jpeg|png|gif|bmp|webp|svg)$/i.test(item.name || '');
                    return isImage
                        ? `<img src="${url}" style="width: 100%;" alt="${item.name || '图片'}" crossorigin="anonymous" />`
                        : `<a href="${url}" target="_blank" class="attachment-file-link">${item.name || '附件'}</a>`;
                }).join(' ');
            }
            // 检查是否为文本段数组 (IOpenSegment[])：每个元素有 type 和 text 属性
            const isTextSegments = fieldCell.every((item: any) => item && typeof item === 'object' && item.text !== undefined && item.type !== undefined);
            if (isTextSegments) {
                // 文本段直接拼接（保留原始换行），然后转换换行符
                const rawText = fieldCell.map((item: any) => extractObjectText(item)).join('');
                return textToParagraphs(rawText);
            }
            // 其他数组 (人员/多选/群组/Lookup值等) - 逗号分隔，不需要段落处理
            return fieldCell
                    .map((item: any) => {
                        if (item === null || item === undefined) return '';
                        if (typeof item === 'string') return item;
                        if (typeof item === 'number') {
                            return String(item).length === 13 ? dayjs(item).format('YYYY/MM/DD HH:mm') : String(item);
                        }
                        if (typeof item === 'boolean') return item ? '是' : '否';
                        if (typeof item === 'object') return extractObjectText(item);
                        return String(item);
                    })
                    .filter((s: string) => s.length > 0)
                    .join(', ');
        }

        // 单个对象 (单选/位置/关联/自动编号等) - 通常是单行，不需要段落处理
        if (typeof fieldCell === 'object') return extractObjectText(fieldCell);

        return String(fieldCell);
    };

    const findValueByFieldName = (fieldName: string, fields: Record<string, any>): { value: string; found: boolean } => {
        const name = fieldName.trim();
        // 1. Check Exact Name in Map
        if (currentMap.value[name]) {
            const id = currentMap.value[name];
            const hasValue = fields[id] !== undefined;
            return { value: hasValue ? getFieldValue(fields[id]) : '', found: true };
        }

        // 2. Check Normalized Name in Cache
        const normalized = normalizeString(name);
        if (normalizedMapCache.value[normalized]) {
            const id = normalizedMapCache.value[normalized];
            const hasValue = fields[id] !== undefined;
            return { value: hasValue ? getFieldValue(fields[id]) : '', found: true };
        }

        // 3. Fallback: Search in Record Fields (for manual/unmapped cases)
        const entry = Object.entries(fields).find(([k, v]) => k === name || (v as any)?.name === name);
        return entry ? { value: getFieldValue(entry[1]), found: true } : { value: '', found: false };
    };

    const restorePlaceholders = (html: string): string => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        // Remove shadows and unmark fields
        doc.querySelectorAll('.mapped-shadow').forEach(s => s.remove());
        doc.querySelectorAll('.mapped-shadow-origin').forEach(el => {
            el.classList.remove('mapped-shadow-origin');
            (el as HTMLElement).style.display = '';
        });
        doc.querySelectorAll('.template-field.is-mapped').forEach(el => {
            el.classList.remove('is-mapped');
            (el as HTMLElement).style.display = '';
        });

        // 同时将已存在的 template-field span 中 ${Name} 格式统一为 {$Name}
        doc.querySelectorAll('.template-field').forEach(el => {
            const txt = el.textContent || '';
            const m = txt.match(/^\$\{(.+)\}$/);
            if (m) {
                const name = m[1].trim();
                el.textContent = `{$${name}}`;
                if (!el.getAttribute('data-fieldname')) {
                    el.setAttribute('data-fieldname', name);
                }
            }
        });

        // Convert plain text placeholders back to spans
        // 支持两种格式：${字段名} 和 {$字段名}，统一输出为 {$字段名}
        const placeholderRegex = /(\$\{([^\}]+)\})|(\{\$([^\}]+)\})/g;
        const processText = (node: Node) => {
            if (node.nodeType === 3) {
                const text = node.textContent || '';
                placeholderRegex.lastIndex = 0;
                if (placeholderRegex.test(text)) {
                    const frag = doc.createDocumentFragment();
                    let last = 0;
                    placeholderRegex.lastIndex = 0;
                    let m;
                    while ((m = placeholderRegex.exec(text)) !== null) {
                        // m[2] 是 ${Name} 格式的字段名, m[4] 是 {$Name} 格式的字段名
                        const fieldName = (m[2] || m[4] || '').trim();

                        frag.appendChild(doc.createTextNode(text.substring(last, m.index)));
                        const span = doc.createElement('span');
                        span.className = 'template-field field-block';
                        span.setAttribute('contenteditable', 'false');
                        span.setAttribute('data-fieldname', fieldName);
                        // 统一为 {$Name} 格式
                        span.textContent = `{$${fieldName}}`;
                        frag.appendChild(span);
                        last = m.index + m[0].length;
                    }
                    frag.appendChild(doc.createTextNode(text.substring(last)));
                    node.parentNode?.replaceChild(frag, node);
                }
            } else if (node.nodeType === 1 && !(node as HTMLElement).classList.contains('template-field')) {
                Array.from(node.childNodes).forEach(processText);
            }
        };
        processText(doc.body);
        
        // 注意：<style> 标签由 DOMParser 放入 head，doc.body.innerHTML 不包含它们
        // <style> 的提取和注入由 Editor.vue 的 BeforeSetContent 处理
        return doc.body.innerHTML;
    };

    const scanAndWrapPlaceholders = (root: Node, doc: Document) => {
        // 支持两种占位符格式: {$Field} 和 ${Field}
        const placeholderRegex = /(\{\$([^}]+)\})|(\$\{([^}]+)\})/g;
        const walker = doc.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
        const nodesToReplace: { node: Text, matches: RegExpExecArray[] }[] = [];

        let currentNode: Node | null;
        while (currentNode = walker.nextNode()) {
            const text = currentNode.textContent || '';
            placeholderRegex.lastIndex = 0;
            if (placeholderRegex.test(text)) {
                // Check if parent is already a template-field to avoid double wrapping
                if (currentNode.parentElement?.classList.contains('template-field')) {
                    continue;
                }

                const matches: RegExpExecArray[] = [];
                let m;
                placeholderRegex.lastIndex = 0;
                while ((m = placeholderRegex.exec(text)) !== null) {
                    matches.push(m);
                }
                nodesToReplace.push({ node: currentNode as Text, matches });
            }
        }

        nodesToReplace.forEach(({ node, matches }) => {
            const frag = doc.createDocumentFragment();
            let last = 0;
            const text = node.textContent || '';

            matches.forEach(m => {
                frag.appendChild(doc.createTextNode(text.substring(last, m.index)));
                const span = doc.createElement('span');
                span.className = 'template-field field-block';
                span.setAttribute('contenteditable', 'false');
                // m[2] 是 {$Field} 格式的字段名, m[4] 是 ${Field} 格式的字段名
                const fieldName = (m[2] || m[4] || '').trim();
                span.setAttribute('data-fieldname', fieldName);
                // 统一为 {$Name} 格式
                span.textContent = `{$${fieldName}}`;
                span.style.padding = '0 2px';
                span.style.borderRadius = '2px';
                span.style.cursor = 'pointer';
                frag.appendChild(span);
                last = m.index + m[0].length;
            });
            frag.appendChild(doc.createTextNode(text.substring(last)));
            node.parentNode?.replaceChild(frag, node);
        });
    };

    const applyLiveMapping = (editor: Editor, recordData: any, fieldMap: Record<string, string>) => {
        const doc = editor.getDoc();
        if (!doc || !recordData?.fields) return;

        // Safety check for fieldMap
        if (!fieldMap || Object.keys(fieldMap).length === 0) return;

        // 1. Ensure all text placeholders are wrapped
        scanAndWrapPlaceholders(doc.body, doc);

        // 2. Rebuild map
        buildNormalizedMap(fieldMap);
        const normalizedMap = normalizedMapCache.value;

        // 3. Apply mapping
        const fields = recordData.fields;
        let mappedCount = 0;

        const allFields = doc.querySelectorAll('.template-field');

        allFields.forEach((el: any) => {
            let fieldName = (el.getAttribute('data-fieldname') || '').trim();

            // Text Content Fallback:
            const textContent = el.textContent?.trim() || '';
            const textMatch = textContent.match(/^\{\$([^}]+)\}$/) || textContent.match(/^\$\{([^}]+)\}$/);
            const textName = textMatch ? textMatch[1].trim() : '';

            // 1. Try Lookup by Attribute
            let result = fieldName ? findValueByFieldName(fieldName, fields) : { value: '', found: false };

            // 2. Fallback: Try Lookup by Text Content if Attribute failed
            if (!result.found && textName && textName !== fieldName) {
                const textResult = findValueByFieldName(textName, fields);
                if (textResult.found) {
                    result = textResult;
                    fieldName = textName;
                    el.setAttribute('data-fieldname', fieldName);
                }
            }

            const { value, found } = result;

            let shadow = el.nextSibling as HTMLElement | null;
            while (shadow && shadow.nodeType === 3 && !shadow.textContent?.trim()) shadow = shadow.nextSibling as HTMLElement | null;
            // 必须检查是否为元素节点，否则文本节点/注释节点没有classList属性
            let isShadow = shadow && shadow.nodeType === 1 && shadow.classList?.contains('mapped-shadow');

            // 如果在 el 旁边没找到 span shadow，检查父级 <p> 的下一个兄弟（多段落 p shadow 的情况）
            if (!isShadow) {
                const parentP = el.closest('p');
                if (parentP) {
                    const nextEl = parentP.nextElementSibling as HTMLElement | null;
                    if (nextEl && nextEl.classList?.contains('mapped-shadow')) {
                        shadow = nextEl;
                        isShadow = true;
                    }
                }
            }

            // ALWAYS hide the placeholder when a record is selected
            mappedCount++;
            el.classList.add('is-mapped');
            (el as HTMLElement).style.display = 'none';

            // If not found or empty value, just remove shadow (shows nothing)
            if (!found || !value || (typeof value === 'string' && !value.trim())) {
                if (isShadow) shadow?.remove();
                // 也清理可能存在的多段落 shadow，并恢复隐藏的原始 <p>
                const parentP = el.closest('p');
                if (parentP) {
                    if ((parentP as HTMLElement).classList.contains('mapped-shadow-origin')) {
                        (parentP as HTMLElement).classList.remove('mapped-shadow-origin');
                        (parentP as HTMLElement).style.display = '';
                    }
                    let next = parentP.nextElementSibling;
                    while (next && next.classList?.contains('mapped-shadow')) {
                        const toRemove = next;
                        next = next.nextElementSibling;
                        toRemove.remove();
                    }
                }
            } else {
                // Handle valid value: Show shadow
                const hasBlockContent = /<p[\s>]/i.test(value);

                if (hasBlockContent) {
                    // 多段落内容：每行作为独立的 <p class="mapped-shadow"> 插入
                    if (isShadow) shadow?.remove();
                    const parentP = el.closest('p') as HTMLElement | null;
                    
                    // 获取原始 <p> 的渲染样式（如果已隐藏则临时恢复），包括 margin
                    const inheritedParts: string[] = [];
                    if (parentP) {
                        const wasHidden = parentP.style.display === 'none';
                        if (wasHidden) parentP.style.display = '';
                        
                        const win = doc.defaultView || window;
                        const computed = win.getComputedStyle(parentP);
                        // 优先取 inline style（用户显式设置），否则取 computed
                        const lh = parentP.style.lineHeight || computed.lineHeight;
                        if (lh && lh !== 'normal') inheritedParts.push(`line-height: ${lh}`);
                        const ff = parentP.style.fontFamily || computed.fontFamily;
                        if (ff) inheritedParts.push(`font-family: ${ff}`);
                        const fs = parentP.style.fontSize || computed.fontSize;
                        if (fs) inheritedParts.push(`font-size: ${fs}`);
                        const ta = parentP.style.textAlign || computed.textAlign;
                        if (ta && ta !== 'start') inheritedParts.push(`text-align: ${ta}`);
                        const ti = parentP.style.textIndent || computed.textIndent;
                        if (ti && ti !== '0px') inheritedParts.push(`text-indent: ${ti}`);
                        const co = parentP.style.color || computed.color;
                        if (co) inheritedParts.push(`color: ${co}`);
                        
                        // 隐藏原始 <p>
                        parentP.style.display = 'none';
                        parentP.classList.add('mapped-shadow-origin');
                        // 清理旧 shadow
                        let next = parentP.nextElementSibling;
                        while (next && next.classList?.contains('mapped-shadow')) {
                            const toRemove = next;
                            next = next.nextElementSibling;
                            toRemove.remove();
                        }
                    }
                    const shadowStyle = inheritedParts.join('; ');

                    const tempDiv = doc.createElement('div');
                    tempDiv.innerHTML = value;
                    const paragraphs = tempDiv.querySelectorAll('p');

                    const insertAnchor = parentP || el;
                    const insertParent = insertAnchor.parentNode;
                    if (insertParent && paragraphs.length > 0) {
                        let refNode = insertAnchor.nextSibling;
                        paragraphs.forEach((p) => {
                            const newP = doc.createElement('p');
                            newP.className = 'mapped-shadow';
                            newP.innerHTML = p.innerHTML;
                            newP.setAttribute('style', shadowStyle);
                            insertParent.insertBefore(newP, refNode);
                        });
                    }
                } else {
                    // 单行内容：用 span shadow 保持在原始 <p> 内部
                    // 清理可能存在的旧多段落 p shadow（兼容旧数据）
                    const parentP = el.closest('p');
                    if (parentP) {
                        let next = parentP.nextElementSibling;
                        while (next && next.classList?.contains('mapped-shadow')) {
                            const toRemove = next;
                            next = next.nextElementSibling;
                            toRemove.remove();
                        }
                        if ((parentP as HTMLElement).classList.contains('mapped-shadow-origin')) {
                            (parentP as HTMLElement).classList.remove('mapped-shadow-origin');
                            (parentP as HTMLElement).style.display = '';
                        }
                    }
                    
                    // 如果之前找到的 shadow 是 <p> 类型（旧数据），已被清理
                    if (isShadow && shadow && shadow.tagName === 'P') {
                        shadow = null;
                        isShadow = false;
                    }

                    if (!isShadow) {
                        shadow = doc.createElement('span');
                        shadow.className = 'mapped-shadow';
                        el.insertAdjacentElement('afterend', shadow);
                    }
                    if (shadow) {
                        const existingImg = shadow.querySelector('img') as HTMLImageElement | null;
                        const newSrcMatch = value.match(/src="([^"]+)"/);
                        const existingSrc = existingImg?.getAttribute('src');
                        const sameImage = existingImg && existingSrc && newSrcMatch && existingSrc === newSrcMatch[1];
                        if (!sameImage) {
                            shadow.innerHTML = value;
                        }
                    }
                }
            }
        });

        // 4. Update Dynamic Barcodes
        const barcodes = doc.querySelectorAll('img.dynamic-barcode');
        barcodes.forEach((img: any) => {
            const fieldName = img.getAttribute('data-fieldname');
            if (fieldName) {
                let { value, found } = findValueByFieldName(fieldName, fields);
                // Strip HTML tags (e.g. <br>) and trim whitespace for barcode value
                if (value) {
                    value = value.replace(/<[^>]*>/g, '').trim();
                }
                if (found && value) {
                    try {
                        const canvas = document.createElement('canvas');
                        // ASCII Check: CODE128 (default) doesn't support Chinese or other non-ASCII chars
                        if (/[^\x00-\x7F]/.test(value)) {
                            // Hide barcode and show a warning toast (only once per mapping cycle)
                            img.style.display = 'none';
                            const fieldName = img.getAttribute('data-fieldname') || '未知字段';
                            console.warn(`条形码字段"${fieldName}"的值包含非ASCII字符，无法生成条形码`);
                        } else {
                            JsBarcode(canvas, value, { format: 'CODE128', displayValue: true, margin: 0, width: 3, height: 80 });
                        }
                        const newSrc = canvas.toDataURL();
                        if (img.src !== newSrc) {
                            // 保留当前的尺寸样式，防止重置
                            // 1. 获取当前宽高（优先取 style，因为用户缩放通常改的是 style）
                            let currentWidth = img.style.width || img.getAttribute('width');
                            let currentHeight = img.style.height || img.getAttribute('height');

                            img.src = newSrc;
                            img.style.display = '';

                            // 2. 恢复宽高
                            if (currentWidth) {
                                if (/^\d+$/.test(currentWidth)) {
                                    img.setAttribute('width', currentWidth);
                                    img.style.width = currentWidth + 'px';
                                } else {
                                    img.style.width = currentWidth;
                                }
                            }
                            if (currentHeight) {
                                if (/^\d+$/.test(currentHeight)) {
                                    img.setAttribute('height', currentHeight);
                                    img.style.height = currentHeight + 'px';
                                } else {
                                    img.style.height = currentHeight;
                                }
                            }
                        }
                    } catch (e) {
                        console.error('Barcode generation failed for:', value, e);
                        img.style.display = 'none';
                    }
                } else {
                    img.style.display = 'none';
                }
            } else {
                img.style.display = 'none';
            }
        });

        // 5. Update Dynamic QR Codes
        const qrcodes = doc.querySelectorAll('img.dynamic-qrcode');
        qrcodes.forEach((img: any) => {
            const fieldName = img.getAttribute('data-fieldname');
            if (fieldName) {
                const { value, found } = findValueByFieldName(fieldName, fields);
                if (found && value) {
                    QRCode.toDataURL(value, { margin: 0, width: 300 })
                        .then((url: string) => {
                            if (img.src !== url) {
                                // 1. 获取当前宽高（优先取 style）
                                let currentWidth = img.style.width || img.getAttribute('width');
                                let currentHeight = img.style.height || img.getAttribute('height');

                                img.src = url;
                                img.style.display = '';

                                // 2. 恢复宽高
                                if (currentWidth) {
                                    if (/^\d+$/.test(currentWidth)) {
                                        img.setAttribute('width', currentWidth);
                                        img.style.width = currentWidth + 'px';
                                    } else {
                                        img.style.width = currentWidth;
                                    }
                                }
                                if (currentHeight) {
                                    if (/^\d+$/.test(currentHeight)) {
                                        img.setAttribute('height', currentHeight);
                                        img.style.height = currentHeight + 'px';
                                    } else {
                                        img.style.height = currentHeight;
                                    }
                                }
                            }
                        })
                        .catch((e: any) => {
                            console.error('QRCode generation failed for:', value, e);
                            img.style.display = 'none';
                        });
                } else {
                    img.style.display = 'none';
                }
            }
        });
    };

    return {
        buildNormalizedMap,
        getFieldValue,
        findValueByFieldName,
        restorePlaceholders,
        applyLiveMapping,
        scanAndWrapPlaceholders
    };
};
