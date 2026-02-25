<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Document, Plus, Edit, Timer, WarningFilled, Picture } from '@element-plus/icons-vue';
import { bitable, FieldType } from '@lark-base-open/js-sdk';

const fieldList = ref<any[]>([]);
const activeCategory = ref('fields'); // 'fields' 或 'system'

const props = defineProps({
  isReadonly: {
    type: Boolean,
    default: true,
  },
  templateName: {
    type: String,
    default: '未命名模板',
  },
});

const emit = defineEmits(['insert-field']);

// 插入用户字段（占位符）
const insertField = (field: any) => {
  if (props.isReadonly) {
    ElMessage({
      message: '请先打开编辑模式',
      type: 'error',
    });
    return;
  }
  emit('insert-field', { type: 'placeholder', data: field });
};

// 插入系统字段（真实值）
const insertSystemField = (fieldType: 'time' | 'name') => {
  if (props.isReadonly) {
    ElMessage({
      message: '请先打开编辑模式',
      type: 'error',
    });
    return;
  }
  
  let content = '';
  if (fieldType === 'time') {
    // 使用更可靠的时间格式化方法
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hour = String(now.getHours()).padStart(2, '0');
    const minute = String(now.getMinutes()).padStart(2, '0');
    content = `${year}-${month}-${day} ${hour}:${minute}`;
  } else if (fieldType === 'name') {
    // 使用当前模板名称
    content = props.templateName;
  }
  
  emit('insert-field', { type: 'text', content });
};

onMounted(async () => {
  try {
    const table = await bitable.base.getActiveTable();
    const view = await table.getActiveView();
    const fieldMetaList = await view.getFieldMetaList();
    fieldList.value = fieldMetaList;
  } catch (error) {
    console.error('字段加载失败:', error);
  }
});
</script>

<template>
  <div class="field-list-container">
    <!-- 自定义 Tab 切换栏 -->
    <div class="custom-tabs">
      <div 
        class="tab-item" 
        :class="{ active: activeCategory === 'fields' }"
        @click="activeCategory = 'fields'"
      >
        字段
      </div>
      <div 
        class="tab-item" 
        :class="{ active: activeCategory === 'system' }"
        @click="activeCategory = 'system'"
      >
        系统
      </div>
    </div>

    <!-- 字段 Tab 内容 -->
    <div v-show="activeCategory === 'fields'" class="tab-content">
      <div class="field-header">
        <slot name="header"></slot>
      </div>
      <el-scrollbar class="field-scrollbar">
        <el-menu v-if="fieldList.length">
          <el-menu-item v-for="field in fieldList" :key="field.id" class="scrollbar-item">
            <el-icon class="field-type-icon">
              <template v-if="field.type === FieldType.Attachment">
                <Picture />
              </template>
              <template v-else>
                <Edit />
              </template>
            </el-icon>
            <span @click.stop="insertField(field)">{{ field.name }}</span>
            <el-icon class="insert-icon" @click.stop="insertField(field)"><Plus /></el-icon>
          </el-menu-item>
        </el-menu>
        <div v-else class="empty-state">
          <el-icon :size="20"><WarningFilled /></el-icon>
          <span>正在加载字段列表...</span>
        </div>
      </el-scrollbar>
    </div>
      
    <!-- 系统 Tab 内容 -->
    <div v-show="activeCategory === 'system'" class="tab-content">
      <el-scrollbar class="field-scrollbar">
        <el-menu>
          <el-menu-item class="scrollbar-item system-field">
            <el-icon class="field-type-icon"><Timer /></el-icon>
            <span @click.stop="insertSystemField('time')">时间</span>
            <el-icon class="insert-icon" @click.stop="insertSystemField('time')"><Plus /></el-icon>
          </el-menu-item>
          <el-menu-item class="scrollbar-item system-field">
            <el-icon class="field-type-icon"><Document /></el-icon>
            <span @click.stop="insertSystemField('name')">名称</span>
            <el-icon class="insert-icon" @click.stop="insertSystemField('name')"><Plus /></el-icon>
          </el-menu-item>
        </el-menu>
      </el-scrollbar>
    </div>
  </div>
</template>

<style scoped>
.field-list-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #fff;
}

/* 自定义 Tab 样式 */
.custom-tabs {
  display: flex;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 10px;
  flex-shrink: 0;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 10px 0;
  cursor: pointer;
  font-size: 14px;
  color: #303133;
  position: relative;
  transition: all 0.3s;
}

.tab-item:hover {
  color: #409eff;
}

.tab-item.active {
  color: #409eff;
  font-weight: 500;
}

.tab-item.active::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: -1px; /* 覆盖底部边框 */
  width: 100%;
  height: 2px;
  background-color: #409eff;
}

.tab-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* 防止撑开父容器 */
}

.field-header {
  padding: 0 10px;
  margin-bottom: 10px;
  flex-shrink: 0;
}

.field-scrollbar {
  flex: 1;
  overflow: hidden;
}

.scrollbar-item {
  display: flex;
  align-items: center;
  padding: 0 8px !important;
  height: 36px;
  margin: 4px 5px;
  border-radius: 4px;
  background-color: #f0f2f5;
  color: #333;
  font-size: 13px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.scrollbar-item.system-field {
  background-color: #fff7e6;
  border: 1px solid #ffd591;
}

.scrollbar-item.system-field:hover {
  background-color: #ffe7ba;
  color: #d46b08;
}

.scrollbar-item .el-icon {
  margin-right: 5px;
}

.field-type-icon {
  font-size: 16px;
  vertical-align: middle;
}

.scrollbar-item span {
  flex-grow: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.scrollbar-item:hover {
  background-color: #e0e9ff;
  color: #1e40af;
}

.insert-icon {
  margin-left: auto;
  visibility: hidden;
}

.scrollbar-item:hover .insert-icon {
  visibility: visible;
}

.el-menu--vertical {
  border-right: none;
}

.empty-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 50vh;
  color: #999;
}

.empty-state .el-icon {
  margin-bottom: 10px;
}
</style>