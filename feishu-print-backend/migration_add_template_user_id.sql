-- 添加 user_id 字段到 templates 表
-- 用于实现模板数据隔离，确保用户只能看到自己的模板

USE feishu_print;

-- 1. 添加 user_id 字段（允许为空，用于兼容系统模板）
ALTER TABLE templates 
ADD COLUMN user_id INT NULL AFTER id;

-- 2. 添加外键约束
ALTER TABLE templates 
ADD CONSTRAINT fk_template_user 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- 3. 添加索引（提高查询性能）
CREATE INDEX idx_template_user_id ON templates(user_id);

-- 4. 添加组合索引（用户ID + 模板类型）
CREATE INDEX idx_template_user_type ON templates(user_id, template_type);

-- 5. 将现有模板标记为系统模板（可选）
-- 如果希望现有模板对所有用户可见，取消下面这行的注释
-- UPDATE templates SET is_system = 1 WHERE user_id IS NULL;

SELECT '✓ 迁移完成：已添加 user_id 字段到 templates 表' AS result;
