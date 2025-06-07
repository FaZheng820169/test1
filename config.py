import os
from pathlib import Path

class Config:
    """基础配置类"""
    # 应用根目录
    BASE_DIR = Path(__file__).parent.absolute()
    
    # 数据库配置
    DATABASE = os.environ.get('DATABASE_URI', os.path.join(BASE_DIR, 'instance', 'tasks.db'))
    
    # 安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    
    # 应用配置
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DATABASE = os.path.join(Config.BASE_DIR, 'instance', 'test.db')


class ProductionConfig(Config):
    """生产环境配置"""
    # 在生产环境中，应该设置更安全的密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'production-key-please-set-in-environment'
    
    # 生产环境数据库URI
    DATABASE = os.environ.get('DATABASE_URI') or os.path.join(Config.BASE_DIR, 'instance', 'production.db')


# 配置映射
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """根据环境变量获取配置"""
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default'])