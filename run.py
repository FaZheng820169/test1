#!/usr/bin/env python
"""
启动Flask Todo应用的简单脚本
"""
import os
import webbrowser
from app import app, init_db

if __name__ == '__main__':
    print("初始化数据库...")
    init_db()
    
    # 在新线程中打开浏览器
    port = 5000
    url = f"http://localhost:{port}"
    print(f"启动浏览器访问: {url}")
    webbrowser.open_new(url)
    
    # 启动Flask应用
    print("启动Flask应用...")
    app.run(debug=True, port=port)