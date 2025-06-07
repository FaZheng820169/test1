# Flask Todo 应用

这是一个使用Flask开发的Todo应用，支持任务的增删改查操作。

## 项目结构

```
├── app.py              # Flask应用主文件
├── config.py           # 配置文件
├── deploy.py           # 部署脚本
├── index.html          # 主页面
├── init_db.py         # 数据库初始化脚本
├── nginx_flask_config.conf  # Nginx配置文件
├── requirements.txt    # 项目依赖
├── schema.sql         # 数据库架构
├── setup_nginx.py     # Nginx设置脚本
├── static/            # 静态文件目录
│   ├── index.html    # 静态主页
│   └── js/           # JavaScript文件
│       └── taskApi.js # API调用脚本
└── tasks.db           # SQLite数据库文件
```

## 如何运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 初始化数据库：
```bash
python init_db.py
```

3. 启动应用：
```bash
python app.py
```

4. 访问应用：
打开浏览器访问 http://localhost:5000

## 功能特性

- 添加新任务
- 查看所有任务
- 更新任务状态
- 删除任务

## 技术栈

- 后端：Flask
- 数据库：SQLite
- 前端：HTML, JavaScript
- 部署：Nginx (可选)

## 注意事项

- 确保运行应用前已安装所有依赖
- 数据库文件 (tasks.db) 会在首次运行时自动创建
- 如果需要部署到生产环境，请参考 deploy.py 和 nginx_flask_config.conf