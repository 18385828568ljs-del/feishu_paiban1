USE feishu_print;

-- 会员计划配置表（定价/创建订单/后台改价）
CREATE TABLE IF NOT EXISTS membership_plans (
  id VARCHAR(32) PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  price INT NOT NULL,
  original_price INT NULL,
  duration_days INT NOT NULL DEFAULT 30,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 初始化默认数据（如已存在则更新）
INSERT INTO membership_plans (id, name, price, original_price, duration_days)
VALUES
  ('pro', '专业版', 2900, 5900, 30),
  ('team', '团队版', 9900, 19900, 30)
ON DUPLICATE KEY UPDATE
  name = VALUES(name),
  price = VALUES(price),
  original_price = VALUES(original_price),
  duration_days = VALUES(duration_days);








