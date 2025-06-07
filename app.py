from flask import Flask, request, jsonify, g, send_from_directory
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

DATABASE = 'tasks.db'

def init_db():
    """初始化数据库表结构"""
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()

def get_db():
    """获取数据库连接"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
    return db

@app.teardown_appcontext
def close_connection(exception):
    """关闭数据库连接"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    """执行查询并返回结果"""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (dict(rv[0]) if rv else None) if one else [dict(row) for row in rv]

def modify_db(query, args=()):
    """执行修改数据库的操作"""
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    cur.close()
    return cur.lastrowid

# 获取所有任务
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = query_db('SELECT * FROM tasks')
    return jsonify({"tasks": tasks})

# 获取单个任务
@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = query_db('SELECT * FROM tasks WHERE id = ?', [task_id], one=True)
    if task:
        return jsonify({"task": task})
    return jsonify({"error": "任务不存在"}), 404

# 创建新任务
@app.route('/api/tasks', methods=['POST'])
def create_task():
    try:
        if not request.json:
            return jsonify({"error": "请求必须是JSON格式"}), 400
            
        if not 'name' in request.json:
            return jsonify({"error": "请提供任务名称"}), 400
        
        name = request.json['name'].strip()
        if not name:
            return jsonify({"error": "任务名称不能为空"}), 400
            
        description = request.json.get('description', '').strip()
        
        # 检查任务名称长度
        if len(name) > 100:  # 假设我们限制任务名称最大长度为100
            return jsonify({"error": "任务名称过长（最大100个字符）"}), 400
            
        # 创建任务
        task_id = modify_db(
            'INSERT INTO tasks (name, description, created_at) VALUES (?, ?, ?)',
            [name, description, datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        )
        
        # 获取新创建的任务
        task = query_db('SELECT * FROM tasks WHERE id = ?', [task_id], one=True)
        
        app.logger.info(f'成功创建新任务: ID={task_id}, 名称="{name}"')
        return jsonify({
            "task": task,
            "message": "任务创建成功"
        }), 201
        
    except sqlite3.Error as e:
        app.logger.error(f'数据库错误: {str(e)}')
        return jsonify({"error": "数据库操作失败"}), 500
    except Exception as e:
        app.logger.error(f'创建任务时发生错误: {str(e)}')
        return jsonify({"error": "服务器内部错误"}), 500

# 更新任务
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    if not request.json:
        return jsonify({"error": "无效的请求数据"}), 400
    
    # 检查任务是否存在
    task = query_db('SELECT * FROM tasks WHERE id = ?', [task_id], one=True)
    if not task:
        return jsonify({"error": "任务不存在"}), 404
    
    name = request.json.get('name', task['name'])
    description = request.json.get('description', task['description'])
    completed = request.json.get('completed', task['completed'])
    
    modify_db(
        'UPDATE tasks SET name = ?, description = ?, completed = ? WHERE id = ?',
        [name, description, completed, task_id]
    )
    
    updated_task = query_db('SELECT * FROM tasks WHERE id = ?', [task_id], one=True)
    return jsonify({"task": updated_task})

# 删除任务
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    # 检查任务是否存在
    task = query_db('SELECT * FROM tasks WHERE id = ?', [task_id], one=True)
    if not task:
        return jsonify({"error": "任务不存在"}), 404
    
    modify_db('DELETE FROM tasks WHERE id = ?', [task_id])
    return jsonify({"result": "任务已删除"})

# 标记任务为已完成
@app.route('/api/tasks/<int:task_id>/complete', methods=['PATCH'])
def complete_task(task_id):
    # 检查任务是否存在
    task = query_db('SELECT * FROM tasks WHERE id = ?', [task_id], one=True)
    if not task:
        return jsonify({"error": "任务不存在"}), 404
    
    modify_db('UPDATE tasks SET completed = 1 WHERE id = ?', [task_id])
    updated_task = query_db('SELECT * FROM tasks WHERE id = ?', [task_id], one=True)
    return jsonify({"task": updated_task})

# 服务静态文件
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# 处理表单提交的任务（支持表单数据）
@app.route('/submit-task', methods=['POST'])
def submit_task():
    try:
        # 获取表单数据
        name = request.form.get('taskName', '').strip()
        description = request.form.get('taskDescription', '').strip()
        
        # 验证数据
        if not name:
            return jsonify({"error": "请提供任务名称"}), 400
            
        # 创建任务
        task_id = modify_db(
            'INSERT INTO tasks (name, description, created_at) VALUES (?, ?, ?)',
            [name, description, datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        )
        
        # 获取新创建的任务
        task = query_db('SELECT * FROM tasks WHERE id = ?', [task_id], one=True)
        
        app.logger.info(f'通过表单成功创建新任务: ID={task_id}, 名称="{name}"')
        
        # 可以选择重定向到主页或返回JSON响应
        return jsonify({
            "task": task,
            "message": "任务创建成功"
        }), 201
        
    except Exception as e:
        app.logger.error(f'处理表单提交时发生错误: {str(e)}')
        return jsonify({"error": "服务器内部错误"}), 500

# 主页路由
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    app.run(debug=True)