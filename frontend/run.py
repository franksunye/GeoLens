#!/usr/bin/env python3
"""
GeoLens Streamlit Frontend 启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """检查依赖是否安装"""
    try:
        import streamlit
        import httpx
        import plotly
        import pandas
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_env_file():
    """检查环境配置文件"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️  未找到 .env 文件，正在从 .env.example 创建...")
            env_file.write_text(env_example.read_text())
            print("✅ .env 文件创建成功")
        else:
            print("❌ 未找到环境配置文件")
            return False
    
    return True

def start_streamlit():
    """启动Streamlit应用"""
    print("🚀 启动 GeoLens Streamlit 应用...")
    
    # Streamlit配置
    config_args = [
        "--server.port=8501",
        "--server.address=localhost",
        "--server.runOnSave=true",
        "--browser.gatherUsageStats=false",
        "--theme.primaryColor=#1f77b4",
        "--theme.backgroundColor=#ffffff",
        "--theme.secondaryBackgroundColor=#f0f2f6",
        "--theme.textColor=#262730"
    ]
    
    # 构建命令
    cmd = ["streamlit", "run", "main.py"] + config_args
    
    try:
        # 启动Streamlit
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
        sys.exit(0)

def main():
    """主函数"""
    print("🌍 GeoLens Streamlit Frontend")
    print("=" * 50)
    
    # 检查当前目录
    if not Path("main.py").exists():
        print("❌ 请在frontend目录下运行此脚本")
        sys.exit(1)
    
    # 检查依赖
    if not check_requirements():
        sys.exit(1)
    
    # 检查环境配置
    if not check_env_file():
        sys.exit(1)
    
    # 显示启动信息
    print("\n📋 启动信息:")
    print("- 应用地址: http://localhost:8501")
    print("- 演示账号: demo@geolens.ai / demo123")
    print("- 按 Ctrl+C 停止应用")
    print("\n" + "=" * 50)
    
    # 启动应用
    start_streamlit()

if __name__ == "__main__":
    main()
