DROP TABLE IF EXISTS tasks;
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed BOOLEAN DEFAULT 0
);

-- 插入一些示例数据
INSERT INTO tasks (name, description) VALUES 
    ('完成项目文档', '编写项目技术文档和用户使用手册'),
    ('准备周会演示', '准备下周一的项目进度演示幻灯片');