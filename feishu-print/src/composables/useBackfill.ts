import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import { bitable, FieldType, type IAttachmentField } from '@lark-base-open/js-sdk';

export function useBackfill() {
    const targetFieldId = ref('');
    const attachmentFields = ref<{ id: string; name: string }[]>([]);
    const backfillFormat = ref<'image' | 'pdf' | 'word'>('image');
    const selectedRecordIds = ref<string[]>([]);
    const isBackfilling = ref(false);
    const backfillProgress = ref({ current: 0, total: 0 });
    const showBackfillDialog = ref(false);
    const backfillCancelled = ref(false);

    const loadAttachmentFields = async () => {
        try {
            const table = await bitable.base.getActiveTable();
            // 使用SDK常量而非硬编码
            const fields = await table.getFieldMetaList();
            // 手动过滤附件类型字段
            const attachmentFieldsList = fields.filter(f => f.type === FieldType.Attachment);
            attachmentFields.value = attachmentFieldsList.map(f => ({ id: f.id, name: f.name }));


            if (attachmentFields.value.length > 0 && !targetFieldId.value) {
                targetFieldId.value = attachmentFields.value[0].id;
            } else if (attachmentFields.value.length === 0) {
                ElMessage.warning('未找到附件类型字段，请先在表格中添加附件字段');
            }
        } catch (error) {
            console.error('加载附件字段失败:', error);
            ElMessage.error('加载附件字段失败: ' + (error as Error).message);
        }
    };

    const handleBackfillCurrent = async (
        selectedRecordId: string,
        getContentAsFile: (format: 'image' | 'pdf' | 'word', recordId: string) => Promise<File>
    ) => {
        if (!targetFieldId.value) {
            ElMessage.warning('请先选择回填字段');
            return;
        }
        if (!selectedRecordId || selectedRecordId === '__placeholder__') {
            ElMessage.warning('请先选择一条记录');
            return;
        }

        isBackfilling.value = true;
        try {
            const table = await bitable.base.getActiveTable();
            const field = await table.getField<IAttachmentField>(targetFieldId.value);
            const file = await getContentAsFile(backfillFormat.value, selectedRecordId);
            await field.setValue(selectedRecordId, file);

            const formatName = backfillFormat.value === 'image' ? '图片' : backfillFormat.value === 'pdf' ? 'PDF' : 'Word';
            ElMessage.success(`回填成功 (${formatName})`);
        } catch (error) {
            console.error('回填失败:', error);
            ElMessage.error('回填失败: ' + (error as Error).message);
        } finally {
            isBackfilling.value = false;
        }
    };

    const handleBackfillSelected = async (
        getContentAsFile: (format: 'image' | 'pdf' | 'word', recordId: string) => Promise<File>,
        loadRecordData: (recordId: string) => Promise<void>
    ) => {
        if (!targetFieldId.value) {
            ElMessage.warning('请先选择回填字段');
            return;
        }
        if (selectedRecordIds.value.length === 0) {
            ElMessage.warning('请先选择要回填的记录');
            return;
        }

        isBackfilling.value = true;
        backfillCancelled.value = false;
        backfillProgress.value = { current: 0, total: selectedRecordIds.value.length };

        let successCount = 0;
        try {
            const table = await bitable.base.getActiveTable();
            const field = await table.getField<IAttachmentField>(targetFieldId.value);

            for (let i = 0; i < selectedRecordIds.value.length; i++) {
                if (backfillCancelled.value) {
                    ElMessage.warning(`已取消，成功回填 ${successCount} 条记录`);
                    break;
                }

                const recordId = selectedRecordIds.value[i];
                backfillProgress.value.current = i + 1;

                await loadRecordData(recordId);
                await new Promise(resolve => setTimeout(resolve, 500));

                const file = await getContentAsFile(backfillFormat.value, recordId);
                await field.setValue(recordId, file);
                successCount++;
            }

            if (!backfillCancelled.value) {
                ElMessage.success(`成功回填 ${successCount} 条记录`);
            }
        } catch (error) {
            console.error('回填选中记录失败:', error);
            ElMessage.error(`回填失败: ${(error as Error).message}，已完成 ${successCount} 条`);
        } finally {
            isBackfilling.value = false;
            backfillCancelled.value = false;
            backfillProgress.value = { current: 0, total: 0 };
        }
    };

    const cancelBackfill = () => {
        backfillCancelled.value = true;
        ElMessage.info('正在取消...');
    };

    return {
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
    };
}
