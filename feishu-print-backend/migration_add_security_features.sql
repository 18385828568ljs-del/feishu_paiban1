-- 添加安全功能相关字段和表
-- 执行时间：2026-01-30

-- 1. 为 users 表添加 security_level 字段
ALTER TABLE users 
ADD COLUMN security_level VARCHAR(20) DEFAULT 'medium' COMMENT '安全等级: low, medium, high';

-- 2. 创建用户活动日志表
CREATE TABLE IF NOT EXISTS user_activities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    feishu_user_id VARCHAR(64) NOT NULL COMMENT '飞书用户ID',
    ip_address VARCHAR(45) NOT NULL COMMENT 'IP地址',
    user_agent VARCHAR(500) COMMENT 'User-Agent',
    client_fingerprint VARCHAR(500) COMMENT '客户端指纹',
    action VARCHAR(50) NOT NULL COMMENT '操作类型',
    security_level VARCHAR(20) COMMENT '安全等级',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_feishu_user_id (feishu_user_id),
    INDEX idx_ip_address (ip_address),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户活动日志表';

-- 3. 为现有用户设置默认安全等级
UPDATE users SET security_level = 'medium' WHERE security_level IS NULL;
