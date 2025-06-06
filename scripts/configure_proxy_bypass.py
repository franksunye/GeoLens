#!/usr/bin/env python3
"""
代理绕过配置脚本
帮助配置代理绕过本地地址，解决前后端通信问题
"""

import os
import sys
import subprocess
import platform

def configure_windows_proxy_bypass():
    """配置Windows系统代理绕过"""
    print("🔧 配置Windows系统代理绕过...")
    
    bypass_list = "localhost;127.0.0.1;*.local;10.*;172.16.*;192.168.*"
    
    try:
        # 使用PowerShell设置代理绕过
        powershell_cmd = f'''
        $regPath = "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings"
        Set-ItemProperty -Path $regPath -Name "ProxyOverride" -Value "{bypass_list}"
        Write-Host "✅ 代理绕过配置已更新"
        '''
        
        result = subprocess.run(
            ["powershell", "-Command", powershell_cmd],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Windows系统代理绕过配置成功")
            print(f"   绕过列表: {bypass_list}")
        else:
            print("❌ 配置失败，请手动设置")
            print("   请在Windows设置 → 网络和Internet → 代理中手动添加绕过地址")
            
    except Exception as e:
        print(f"❌ 配置过程中出错: {e}")
        print("   请手动配置代理绕过")

def show_manual_configuration_guide():
    """显示手动配置指南"""
    print("\n📋 手动配置指南:")
    print("=" * 50)
    
    print("\n🖥️  Windows系统代理设置:")
    print("1. 打开 Windows 设置")
    print("2. 进入 网络和Internet → 代理")
    print("3. 在'手动代理设置'中找到'请勿将代理服务器用于以下地址'")
    print("4. 添加以下地址:")
    print("   localhost;127.0.0.1;*.local;10.*;172.16.*;192.168.*")
    
    print("\n🌐 浏览器代理插件设置 (如SwitchyOmega):")
    print("1. 打开代理插件设置")
    print("2. 找到'绕过列表'或'Bypass List'")
    print("3. 添加以下规则:")
    print("   localhost")
    print("   127.0.0.1")
    print("   *.local")
    
    print("\n🔧 环境变量设置:")
    print("在PowerShell中执行:")
    print('$env:NO_PROXY="localhost,127.0.0.1,.local"')

def test_local_connection():
    """测试本地连接"""
    print("\n🧪 测试本地连接...")
    
    import requests
    
    test_urls = [
        "http://localhost:8000/health",
        "http://127.0.0.1:8000/health"
    ]
    
    for url in test_urls:
        try:
            # 设置不使用代理
            proxies = {
                'http': None,
                'https': None
            }
            
            response = requests.get(url, timeout=5, proxies=proxies)
            if response.status_code == 200:
                print(f"✅ {url} - 连接成功")
            else:
                print(f"⚠️  {url} - 状态码: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {url} - 连接失败 (后端服务可能未启动)")
        except Exception as e:
            print(f"❌ {url} - 错误: {e}")

def main():
    """主函数"""
    print("🚀 GeoLens 代理绕过配置工具")
    print("=" * 40)
    
    system = platform.system()
    
    if system == "Windows":
        print("检测到Windows系统")
        
        choice = input("\n是否尝试自动配置系统代理绕过? (y/n): ").lower()
        if choice == 'y':
            configure_windows_proxy_bypass()
        
    else:
        print(f"检测到 {system} 系统")
        print("请参考手动配置指南")
    
    show_manual_configuration_guide()
    
    # 测试连接
    test_choice = input("\n是否测试本地连接? (y/n): ").lower()
    if test_choice == 'y':
        test_local_connection()
    
    print("\n🎯 配置完成后请:")
    print("1. 重启浏览器")
    print("2. 重启前端应用")
    print("3. 测试登录功能")

if __name__ == "__main__":
    main()
