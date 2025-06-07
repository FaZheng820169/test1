import sqlite3
import os

def init_db():
    # 确保在当前目录下创建数据库文件
    db_path = 'tasks.db'
    
    # 如果数据库文件已存在，先删除它
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # 创建新的数据库连接
    conn = sqlite3.connect(db_path)
    
    try:
        # 读取schema.sql文件
        with open('schema.sql', 'r', encoding='utf-8') as f:
            schema = f.read()
        
        # 执行SQL语句
        conn.executescript(schema)
        
        # 提交更改
        conn.commit()
        print("数据库初始化成功！")
        
    except Exception as e:
        print(f"初始化数据库时出错：{e}")
        # 发生错误时回滚
        conn.rollback()
        
    finally:
        # 关闭连接
        conn.close()

if __name__ == '__main__':
    init_db()