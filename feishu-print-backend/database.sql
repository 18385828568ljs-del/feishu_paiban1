-- 创建数据库
CREATE DATABASE IF NOT EXISTS feishu_print CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE feishu_print;

-- 创建模板表
CREATE TABLE IF NOT EXISTS templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content LONGTEXT NOT NULL,
    template_type VARCHAR(20) DEFAULT 'normal' NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_template_type (template_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入示例数据
INSERT INTO templates (name, content, template_type) VALUES 
('医疗设备验收单', '<p style="text-align: center;"><span style="font-size: 22pt; font-family: 方正小标宋简体;">医疗设备验收单</span></p> 
 <p style="text-align: right;"><span style="font-family: 仿宋;">□是/□否安装类</span></p>
<table style="border-collapse: collapse; width: 100.072%; height: 745.031px;" border="1"><colgroup><col style="width: 16%;"><col style="width: 34%;"><col style="width: 16%;"><col style="width: 34%;"></colgroup>
<tbody>
<tr style="height: 45px;">
<td><span style="font-family: 仿宋;">资产名称</span></td>
<td><span style="font-family: 仿宋;" class="template-field field-block" contenteditable="false" data-fieldid="fld0l6zAu7" data-fieldname="设备名称">{$设备名称}</span></td>
<td><span style="font-family: 仿宋;">规格型号</span></td>
<td><span style="font-family: 仿宋;" class="template-field field-block" contenteditable="false" data-fieldid="fld2gouIKu" data-fieldname="规格型号">{$规格型号}</span></td>
</tr>
</tbody>
</table>', 'normal'),
('模板二', '<p>这是<i>模板二</i>的内容。</p>', 'normal');
