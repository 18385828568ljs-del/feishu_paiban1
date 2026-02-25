import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';
import { exportWord } from '@/api/export';

export function useExportLogic(
    checkAndUseFeature: (feat: string) => Promise<boolean>,
    _readPageMarginFromIframe: () => [number, number, number, number],
    _createExportRoot: (opt?: { includePageNumbers?: boolean }) => any,
    generateWordExportData: (wrapper: HTMLElement, doc: Document | null) => Promise<{ htmlString: string; margins: [number, number, number, number] }>,
    _generateExportCanvas: (root: HTMLElement) => Promise<HTMLCanvasElement>
) {
    const router = useRouter();

    const handleExportPDF = async (contentWrapper: HTMLElement, cleanup: () => void, exportName?: string) => {
        const allowed = await checkAndUseFeature('pdf_export');
        if (!allowed) {
            router.push('/pricing');
            return;
        }

        try {
            // 获取所有页面
            const pages = contentWrapper.querySelectorAll('.template-page-content');
            if (pages.length === 0) {
                ElMessage.warning('未找到可导出的页面');
                cleanup();
                return;
            }

            // 创建 PDF (A4: 210mm x 297mm)
            const pdf = new jsPDF({ unit: 'mm', format: 'a4', orientation: 'portrait' });
            const pdfWidth = 210;
            const pdfHeight = 297;

            // 逐页渲染
            for (let i = 0; i < pages.length; i++) {
                const page = pages[i] as HTMLElement;
                
                // 临时显示单个页面用于截图
                const originalDisplay = page.style.display;
                
                // 渲染当前页面为 canvas
                const canvas = await html2canvas(page, {
                    scale: 2,
                    useCORS: true,
                    logging: false,
                    backgroundColor: '#ffffff',
                    width: page.offsetWidth,
                    height: page.offsetHeight
                });

                // 计算图片在 PDF 中的尺寸（保持比例，适应 A4）
                const imgWidth = pdfWidth;
                const imgHeight = (canvas.height * pdfWidth) / canvas.width;

                // 添加页面（第一页不需要 addPage）
                if (i > 0) {
                    pdf.addPage();
                }

                // 将 canvas 添加到 PDF
                const imgData = canvas.toDataURL('image/jpeg', 0.95);
                pdf.addImage(imgData, 'JPEG', 0, 0, imgWidth, Math.min(imgHeight, pdfHeight));

                page.style.display = originalDisplay;
            }

            // 保存 PDF
            pdf.save(`${exportName || '导出'}.pdf`);
            ElMessage.success('PDF 导出成功');
        } catch (error) {
            console.error('导出 PDF 失败:', error);
            ElMessage.error('导出 PDF 失败');
        } finally {
            cleanup();
        }
    };

    const handleExportImage = async (contentWrapper: HTMLElement, cleanup: () => void, exportName?: string) => {
        try {
            // 获取所有页面，逐页导出
            const pages = contentWrapper.querySelectorAll('.template-page-content');
            if (pages.length === 0) {
                ElMessage.warning('未找到可导出的页面');
                cleanup();
                return;
            }

            const baseName = exportName || '导出图片';

            if (pages.length === 1) {
                // 单页：直接下载
                const canvas = await html2canvas(pages[0] as HTMLElement, {
                    scale: 2,
                    useCORS: true,
                    logging: false,
                    backgroundColor: '#ffffff'
                });
                const dataUrl = canvas.toDataURL('image/png');
                const link = document.createElement('a');
                link.download = `${baseName}.png`;
                link.href = dataUrl;
                link.click();
            } else {
                // 多页：逐页下载（带页码后缀）
                for (let i = 0; i < pages.length; i++) {
                    const page = pages[i] as HTMLElement;
                    const canvas = await html2canvas(page, {
                        scale: 2,
                        useCORS: true,
                        logging: false,
                        backgroundColor: '#ffffff'
                    });
                    const dataUrl = canvas.toDataURL('image/png');
                    const link = document.createElement('a');
                    link.download = `${baseName}_第${i + 1}页.png`;
                    link.href = dataUrl;
                    link.click();
                    // 稍微延迟，避免浏览器阻止多次下载
                    await new Promise(r => setTimeout(r, 300));
                }
            }

            ElMessage.success(`图片导出成功${pages.length > 1 ? `（共${pages.length}页）` : ''}`);
        } catch (error) {
            console.error('导出图片失败:', error);
            ElMessage.error('导出图片失败');
        } finally {
            cleanup();
        }
    };

    const handleExportWordAction = async (contentWrapper: HTMLElement, doc: Document | null, cleanup: () => void, templateName: string) => {
        try {
            const { htmlString, margins } = await generateWordExportData(contentWrapper, doc);
            cleanup();
            await exportWord(htmlString, templateName || '导出文档', margins);
            ElMessage.success('Word 文档导出成功');
        } catch (error) {
            console.error('导出 Word 失败:', error);
            ElMessage.error('导出 Word 失败: ' + (error as Error).message);
        }
    };

    // 导出长图：所有页面拼接成一张图片
    const handleExportLongImage = async (contentWrapper: HTMLElement, cleanup: () => void, exportName?: string) => {
        try {
            const pages = contentWrapper.querySelectorAll('.template-page-content');
            if (pages.length === 0) {
                ElMessage.warning('未找到可导出的页面');
                cleanup();
                return;
            }

            const baseName = exportName || '导出长图';

            // 逐页渲染成 canvas
            const canvases: HTMLCanvasElement[] = [];
            let totalHeight = 0;
            let maxWidth = 0;

            for (let i = 0; i < pages.length; i++) {
                const page = pages[i] as HTMLElement;
                const canvas = await html2canvas(page, {
                    scale: 2,
                    useCORS: true,
                    logging: false,
                    backgroundColor: '#ffffff'
                });
                canvases.push(canvas);
                totalHeight += canvas.height;
                maxWidth = Math.max(maxWidth, canvas.width);
            }

            // 创建合并后的大 canvas
            const mergedCanvas = document.createElement('canvas');
            mergedCanvas.width = maxWidth;
            mergedCanvas.height = totalHeight;
            const ctx = mergedCanvas.getContext('2d');
            if (!ctx) throw new Error('无法创建 canvas context');

            // 逐个绘制到合并 canvas
            let currentY = 0;
            for (const canvas of canvases) {
                ctx.drawImage(canvas, 0, currentY);
                currentY += canvas.height;
            }

            // 下载
            const dataUrl = mergedCanvas.toDataURL('image/png');
            const link = document.createElement('a');
            link.download = `${baseName}.png`;
            link.href = dataUrl;
            link.click();

            ElMessage.success('长图导出成功');
        } catch (error) {
            console.error('导出长图失败:', error);
            ElMessage.error('导出长图失败');
        } finally {
            cleanup();
        }
    };

    return {
        handleExportPDF,
        handleExportImage,
        handleExportLongImage,
        handleExportWordAction
    };
}
