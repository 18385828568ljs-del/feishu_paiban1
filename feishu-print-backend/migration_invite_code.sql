-- 迁移脚本：使 team_invites 表的 invitee_feishu_id 字段可以为空
-- 执行时间：修改邀请码功能以支持通用邀请码
-- 
-- 使用方法：
-- 1. 连接到数据库：mysql -u your_user -p feishu_print
-- 2. 执行此脚本：source migration_invite_code.sql
-- 或者在 MySQL 客户端中直接执行以下 SQL

USE feishu_print;

-- 修改 invitee_feishu_id 字段，允许为空
ALTER TABLE team_invites 
MODIFY COLUMN invitee_feishu_id VARCHAR(64) NULL 
COMMENT '被邀请人飞书ID（为空表示通用邀请码）';

-- 验证修改
DESCRIBE team_invites;

