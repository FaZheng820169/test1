#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
import shutil
import re
from pathlib import Path

# 颜色输出
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text, color):
    print(f"{color}{text}{Colors.ENDC}")

def print_step(step):
    print_colored(f"\n[STEP] {step}", Colors.HEADER)

def print_success(message):
    print_colored(f"✓ {message}", Colors.GREEN)

def print_error(message):
    print_colored(f"✗ ERROR: {message}", Colors.FAIL)

def print_warning(message):
    print_colored(f"⚠ WARNING: {message}", Colors.WARNING)

def run_command(command, error_message="命令执行失败"):
    """执行shell命令并处理错误"""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print_error(f"{error_message}: {e}")
        print(f"错误输出: {e.stderr}")
        return None

def is_root():
    """检查是否以root权限运行"""
    return os.geteuid() == 0 if hasattr(os, 'geteuid') else False

def detect_os():
    """检测操作系统类型"""
    system = platform.system().lower()
    
    if system == 'linux':
        # 检测Linux发行版
        try:
            with open('/etc/os-release', 'r') as f:
                os_info = f.read()
                if 'ubuntu' in os_info.lower():
                    return 'ubuntu'
                elif 'debian' in os_info.lower():
                    return 'debian'
                elif 'centos' in os_info.lower() or 'rhel' in os_info.lower():
                    return 'centos'
        except FileNotFoundError:
            pass
        return 'linux'
    
    return system

def install_nginx(os_type):
    """根据操作系统类型安装Nginx"""
    print_step("安装Nginx")
    
    if os_type in ['ubuntu', 'debian']:
        run_command("apt update", "更新软件包列表失败")
        result = run_command("apt install -y nginx", "安装Nginx失败")
    elif os_type == 'centos':
        run_command("yum install -y epel-release", "安装EPEL仓库失败")
        result = run_command("yum install -y nginx", "安装Nginx失败")
    else:
        print_error(f"不支持的操作系统: {os_type}")
        sys.exit(1)
    
    if result is not None:
        print_success("Nginx安装成功")
    
    # 验证安装
    nginx_version = run_command("nginx -v 2>&1", "获取Nginx版本失败")
    if nginx_version:
        print_success(f"Nginx版本: {nginx_version}")

def get_nginx_paths(os_type):
    """获取Nginx配置路径"""
    if os_type in ['ubuntu', 'debian']:
        sites_available = '/etc/nginx/sites-available'
        sites_enabled = '/etc/nginx/sites-enabled'
        conf_path = os.path.join(sites_available, 'flask_app')
    elif os_type == 'centos':
        sites_available = '/etc/nginx/conf.d'
        sites_enabled = None  # CentOS不使用sites-enabled
        conf_path = os.path.join(sites_available, 'flask_app.conf')
    else:
        # 默认路径
        sites_available = '/etc/nginx/conf.d'
        sites_enabled = None
        conf_path = os.path.join(sites_available, 'flask_app.conf')
    
    return {
        'sites_available': sites_available,
        'sites_enabled': sites_enabled,
        'conf_path': conf_path
    }

def configure_nginx(os_type, app_path):
    """配置Nginx"""
    print_step("配置Nginx")
    
    # 获取Nginx路径
    paths = get_nginx_paths(os_type)
    
    # 读取配置模板
    try:
        with open('nginx_flask_config.conf', 'r') as f:
            config_content = f.read()
    except FileNotFoundError:
        print_error("找不到Nginx配置模板文件: nginx_flask_config.conf")
        sys.exit(1)
    
    # 替换静态文件路径
    static_path = os.path.join(app_path, 'static')
    config_content = config_content.replace('/path/to/your/app/static/', static_path + '/')
    
    # 写入配置文件
    try:
        with open(paths['conf_path'], 'w') as f:
            f.write(config_content)
        print_success(f"Nginx配置已写入: {paths['conf_path']}")
    except Exception as e:
        print_error(f"写入Nginx配置失败: {e}")
        sys.exit(1)
    
    # 对于Ubuntu/Debian，创建符号链接
    if paths['sites_enabled']:
        if os.path.exists(os.path.join(paths['sites_enabled'], os.path.basename(paths['conf_path']))):
            os.remove(os.path.join(paths['sites_enabled'], os.path.basename(paths['conf_path'])))
        
        try:
            os.symlink(
                paths['conf_path'], 
                os.path.join(paths['sites_enabled'], os.path.basename(paths['conf_path']))
            )
            print_success("已创建配置符号链接")
        except Exception as e:
            print_error(f"创建符号链接失败: {e}")
    
    # 测试Nginx配置
    result = run_command("nginx -t", "Nginx配置测试失败")
    if result is not None:
        print_success("Nginx配置测试通过")

def restart_nginx():
    """重启Nginx服务"""
    print_step("重启Nginx服务")
    
    result = run_command("systemctl restart nginx", "重启Nginx服务失败")
    if result is not None:
        print_success("Nginx服务已重启")
    
    # 确保Nginx已启用
    run_command("systemctl enable nginx", "启用Nginx服务失败")

def check_port_80():
    """检查80端口是否可用"""
    print_step("检查80端口")
    
    result = run_command("netstat -tuln | grep ':80 '", "检查端口失败")
    if result:
        print_warning("80端口已被占用，可能是Nginx或其他服务")
        print(result)
    else:
        print_success("80端口可用")

def main():
    """主函数"""
    print_colored("Nginx配置工具 - Flask应用", Colors.BOLD)
    
    # 检查root权限
    if not is_root():
        print_error("此脚本需要root权限运行")
        print("请使用 'sudo python setup_nginx.py' 重新运行")
        sys.exit(1)
    
    # 检测操作系统
    os_type = detect_os()
    print_success(f"检测到操作系统: {os_type}")
    
    # 获取应用路径
    app_path = os.path.abspath(os.path.dirname(__file__))
    print_success(f"应用路径: {app_path}")
    
    # 检查80端口
    check_port_80()
    
    # 安装Nginx
    install_nginx(os_type)
    
    # 配置Nginx
    configure_nginx(os_type, app_path)
    
    # 重启Nginx
    restart_nginx()
    
    print_colored("\n配置完成！", Colors.BOLD)
    print_success("Flask应用现在应该可以通过80端口访问")
    print_success("请访问 http://your_server_ip 测试配置")
    
    # 提供一些额外信息
    print_colored("\n其他信息:", Colors.BLUE)
    print("- Nginx日志位置: /var/log/nginx/")
    print("- 如需修改配置: 编辑 nginx_flask_config.conf 然后重新运行此脚本")
    print("- 如需手动重启Nginx: sudo systemctl restart nginx")

if __name__ == "__main__":
    main()