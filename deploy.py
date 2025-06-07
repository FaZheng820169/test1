#!/usr/bin/env python3
import os
import sys
import subprocess
import logging
import signal
import time
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class Deployer:
    def __init__(self):
        self.app_dir = Path(__file__).parent.absolute()
        self.venv_dir = self.app_dir / 'venv'
        self.gunicorn_pid_file = 'gunicorn.pid'
        self.log_dir = self.app_dir / 'logs'
        self.gunicorn_workers = 4  # 根据CPU核心数调整

    def setup_directories(self):
        """创建必要的目录"""
        try:
            self.log_dir.mkdir(exist_ok=True)
            logger.info("成功创建日志目录")
        except Exception as e:
            logger.error(f"创建目录时出错: {e}")
            raise

    def create_virtual_env(self):
        """创建并激活虚拟环境"""
        try:
            if not self.venv_dir.exists():
                logger.info("创建虚拟环境...")
                subprocess.run([sys.executable, '-m', 'venv', str(self.venv_dir)], check=True)
            logger.info("虚拟环境已就绪")
        except subprocess.CalledProcessError as e:
            logger.error(f"创建虚拟环境失败: {e}")
            raise

    def install_dependencies(self):
        """安装项目依赖"""
        pip_cmd = str(self.venv_dir / 'bin' / 'pip') if os.name != 'nt' else str(self.venv_dir / 'Scripts' / 'pip')
        try:
            logger.info("安装依赖...")
            # 确保安装最新版本的pip
            subprocess.run([pip_cmd, 'install', '--upgrade', 'pip'], check=True)
            # 安装项目依赖
            subprocess.run([pip_cmd, 'install', '-r', 'requirements.txt'], check=True)
            # 安装Gunicorn（仅在非Windows系统上）
            if os.name != 'nt':
                subprocess.run([pip_cmd, 'install', 'gunicorn'], check=True)
            logger.info("所有依赖安装完成")
        except subprocess.CalledProcessError as e:
            logger.error(f"安装依赖失败: {e}")
            raise

    def start_application(self):
        """启动应用"""
        if os.name == 'nt':
            logger.warning("Windows环境检测到，将使用Flask开发服务器而不是Gunicorn")
            self._start_flask_dev_server()
        else:
            self._start_gunicorn()

    def _start_gunicorn(self):
        """使用Gunicorn启动应用"""
        gunicorn_cmd = str(self.venv_dir / 'bin' / 'gunicorn')
        try:
            # 停止已运行的实例
            self.stop_application()
            
            # 启动新实例
            cmd = [
                gunicorn_cmd,
                'app:app',  # app模块中的app对象
                f'--workers={self.gunicorn_workers}',
                '--bind=0.0.0.0:5000',
                '--daemon',  # 后台运行
                f'--pid={self.gunicorn_pid_file}',
                f'--log-file={self.log_dir}/gunicorn.log',
                '--log-level=info',
                '--access-logfile=-',  # 访问日志输出到标准输出
                '--error-logfile=-',   # 错误日志输出到标准输出
                '--reload'  # 代码变更时自动重载
            ]
            subprocess.run(cmd, check=True)
            logger.info("Gunicorn 服务器已启动")
            
            # 等待几秒确保服务器正常启动
            time.sleep(2)
            self._check_application_health()
        except subprocess.CalledProcessError as e:
            logger.error(f"启动Gunicorn失败: {e}")
            raise

    def _start_flask_dev_server(self):
        """在Windows环境下使用Flask开发服务器"""
        python_cmd = str(self.venv_dir / 'Scripts' / 'python') if os.name == 'nt' else str(self.venv_dir / 'bin' / 'python')
        try:
            cmd = [python_cmd, 'app.py']
            subprocess.Popen(cmd)
            logger.info("Flask 开发服务器已启动")
            time.sleep(2)
            self._check_application_health()
        except subprocess.CalledProcessError as e:
            logger.error(f"启动Flask开发服务器失败: {e}")
            raise

    def stop_application(self):
        """停止应用"""
        if os.path.exists(self.gunicorn_pid_file):
            try:
                with open(self.gunicorn_pid_file, 'r') as f:
                    pid = int(f.read().strip())
                os.kill(pid, signal.SIGTERM)
                logger.info(f"已停止PID为{pid}的进程")
                os.remove(self.gunicorn_pid_file)
            except ProcessLookupError:
                logger.warning("进程已不存在")
                os.remove(self.gunicorn_pid_file)
            except Exception as e:
                logger.error(f"停止应用时出错: {e}")

    def _check_application_health(self):
        """检查应用是否成功启动"""
        import urllib.request
        import urllib.error
        
        url = "http://localhost:5000/"
        try:
            response = urllib.request.urlopen(url)
            if response.status == 200:
                logger.info("应用健康检查通过")
            else:
                logger.warning(f"应用响应异常状态码: {response.status}")
        except urllib.error.URLError as e:
            logger.error(f"应用健康检查失败: {e}")
            raise

    def deploy(self):
        """执行完整的部署流程"""
        try:
            logger.info("开始部署流程...")
            self.setup_directories()
            self.create_virtual_env()
            self.install_dependencies()
            self.start_application()
            logger.info("部署完成！应用已成功启动")
        except Exception as e:
            logger.error(f"部署过程中出错: {e}")
            sys.exit(1)

if __name__ == '__main__':
    deployer = Deployer()
    if len(sys.argv) > 1 and sys.argv[1] == 'stop':
        deployer.stop_application()
    else:
        deployer.deploy()