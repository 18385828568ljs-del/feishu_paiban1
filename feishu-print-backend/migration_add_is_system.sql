-- 添加is_system字段的迁移脚本
USE feishu_print;

-- 检查并添加 is_system 字段（如果不存在）
SET @dbname = DATABASE();
SET @tablename = 'templates';
SET @columnname = 'is_system';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (COLUMN_NAME = @columnname)
  ) > 0,
  'SELECT 1', -- 字段已存在，不执行任何操作
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' BOOLEAN DEFAULT FALSE NOT NULL')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 将现有的所有模版标记为非系统模版（is_system = FALSE）
-- 注意：系统模版应该通过import_system_templates.py脚本导入，并标记为is_system = TRUE
UPDATE templates SET is_system = FALSE WHERE is_system IS NULL OR is_system = FALSE;

