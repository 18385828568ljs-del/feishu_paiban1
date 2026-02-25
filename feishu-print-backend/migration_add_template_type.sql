-- 添加模板类型字段的迁移脚本
USE feishu_print;

-- 检查并添加 template_type 字段（如果不存在）
SET @dbname = DATABASE();
SET @tablename = 'templates';
SET @columnname = 'template_type';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (COLUMN_NAME = @columnname)
  ) > 0,
  'SELECT 1', -- 字段已存在，不执行任何操作
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' VARCHAR(20) DEFAULT ''normal'' NOT NULL AFTER content')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 为现有数据设置默认值
UPDATE templates SET template_type = 'normal' WHERE template_type IS NULL OR template_type = '';

-- 检查并添加索引（如果不存在）
SET @indexname = 'idx_template_type';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (INDEX_NAME = @indexname)
  ) > 0,
  'SELECT 1', -- 索引已存在，不执行任何操作
  CONCAT('CREATE INDEX ', @indexname, ' ON ', @tablename, '(', @columnname, ')')
));
PREPARE createIndexIfNotExists FROM @preparedStatement;
EXECUTE createIndexIfNotExists;
DEALLOCATE PREPARE createIndexIfNotExists;

