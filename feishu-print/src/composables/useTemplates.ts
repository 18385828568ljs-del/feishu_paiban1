import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessageBox, ElMessage } from 'element-plus';
import { templateApi } from '@/api/templates';

export function useTemplates() {
    const router = useRouter();
    const selectedTemplate = ref('');
    const templates = ref<{
        id: string;
        name: string;
        content: string;
        is_system?: boolean;
        owner_id?: number | null;
    }[]>([]);
    const editorContent = ref('');

    const loadTemplates = async () => {
        try {
            const data = await templateApi.getAll();
            templates.value = data.map((t: any) => ({
                id: String(t.id),
                name: t.name,
                content: t.content,
                is_system: t.is_system,
                owner_id: t.owner_id
            }));
        } catch (error) {
            console.error('加载模板列表失败:', error);
            ElMessage.error('加载模板列表失败');
        }
    };

    const handleNewTemplate = () => {
        editorContent.value = '';
        selectedTemplate.value = '';
    };

    const handleSaveTemplate = async () => {
        try {
            // 1. 检查是否正在编辑现有模板
            if (selectedTemplate.value) {
                const currentTpl = templates.value.find(t => t.id === selectedTemplate.value);

                if (currentTpl) {
                    // CASE A: 如果是系统模板 -> 执行"自动另存为" (Clone)
                    if (currentTpl.is_system) {
                        try {
                            // 尝试以原名创建新模板
                            const newTemplate = await templateApi.create({
                                name: currentTpl.name,
                                content: editorContent.value,
                                template_type: 'user' // 确保保存为用户模板
                            });

                            // 更新列表并切换到新模板
                            templates.value.push({
                                id: String(newTemplate.id),
                                name: newTemplate.name,
                                content: newTemplate.content,
                                is_system: newTemplate.is_system,
                                owner_id: newTemplate.owner_id as number
                            });

                            selectedTemplate.value = String(newTemplate.id);
                            ElMessage.success('已自动保存为您的个人模板');
                            return; // 结束流程
                        } catch (cloneError: any) {
                            // 处理重名情况
                            const errorDetail = cloneError?.response?.data?.detail || '';
                            if (errorDetail.includes('已存在')) {
                                // 如果重名，引导用户另存为
                                ElMessageBox.confirm(
                                    `您已有一个名为 "${currentTpl.name}" 的个人模板。如果是更新该模板，请先切换到该模板再编辑。或者选择"另存为"新名称？`,
                                    '模板名称冲突',
                                    {
                                        confirmButtonText: '另存为',
                                        cancelButtonText: '取消',
                                        type: 'warning'
                                    }
                                ).then(() => {
                                    handleSaveAsNewTemplate(() => editorContent.value);
                                }).catch(() => { });
                                return;
                            }
                            throw cloneError; // 其他错误抛出
                        }
                    }

                    // CASE B: 如果是个人模板 -> 直接更新
                    else {
                        await templateApi.update(Number(selectedTemplate.value), {
                            name: currentTpl.name,
                            content: editorContent.value
                        });
                        // 更新本地状态
                        currentTpl.content = editorContent.value;
                        ElMessage.success('模板更新成功');
                        return;
                    }
                }
            }

            // CASE C: 全新模板 (selectedTemplate 为空) -> 弹窗询问
            const { value: templateName } = await ElMessageBox.prompt('请输入模板名称', '保存模板', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                inputPattern: /.+/,
                inputErrorMessage: '模板名称不能为空'
            });

            if (templateName) {
                const newTemplate = await templateApi.create({
                    name: templateName,
                    content: editorContent.value,
                    template_type: 'user' // 确保保存为用户模板
                });
                templates.value.push({
                    id: String(newTemplate.id),
                    name: newTemplate.name,
                    content: newTemplate.content,
                    is_system: newTemplate.is_system,
                    owner_id: newTemplate.owner_id as number
                });
                selectedTemplate.value = String(newTemplate.id);
                ElMessage.success('模板已成功创建');
            }

        } catch (error: any) {
            if (error !== 'cancel') {
                console.error('保存模板失败:', error);
                const errorMessage = error?.response?.data?.detail || '保存模板失败';
                ElMessage.error(errorMessage);
            }
        }
    };

    const handleSaveAsNewTemplate = async (getTemplateShellContent: () => string) => {
        try {
            const { value: templateName } = await ElMessageBox.prompt('请输入模板名称', '保存为新模板', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                inputPattern: /.+/,
                inputErrorMessage: '模板名称不能为空',
            });

            if (templateName) {
                const templateContent = getTemplateShellContent();
                if (!templateContent || !templateContent.trim()) {
                    ElMessage.warning('模板内容不能为空');
                    return;
                }

                await templateApi.create({
                    name: templateName,
                    content: templateContent,
                    template_type: 'user',
                });

                ElMessage.success('模板已成功保存');
                router.push({ name: 'templates', query: { category: 'user' } });
            }
        } catch (error: any) {
            if (error !== 'cancel') {
                console.error('保存模板失败:', error);
                const errorMessage = error?.response?.data?.detail || '保存模板失败';
                ElMessage.error(errorMessage);
            }
        }
    };

    const handleDeleteTemplate = async () => {
        if (!selectedTemplate.value) {
            ElMessage.warning('请先选择一个模板进行删除');
            return;
        }

        try {
            await ElMessageBox.confirm('确定要删除此模板吗？', '删除模板', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            });

            await templateApi.delete(Number(selectedTemplate.value));
            const index = templates.value.findIndex(t => t.id === selectedTemplate.value);
            if (index !== -1) {
                templates.value.splice(index, 1);
                selectedTemplate.value = '';
                editorContent.value = '';
                ElMessage.success('模板已成功删除');
            }
        } catch (error: any) {
            if (error !== 'cancel') {
                console.error('删除模板失败:', error);
                ElMessage.error('删除模板失败');
            }
        }
    };

    watch(selectedTemplate, (newVal) => {
        if (newVal) {
            const template = templates.value.find(t => t.id === newVal);
            if (template) {
                editorContent.value = template.content;
            }
        } else {
            editorContent.value = '';
        }
    });

    return {
        selectedTemplate,
        templates,
        editorContent,
        loadTemplates,
        handleNewTemplate,
        handleSaveTemplate,
        handleSaveAsNewTemplate,
        handleDeleteTemplate
    };
}
