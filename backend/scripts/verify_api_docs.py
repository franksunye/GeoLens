#!/usr/bin/env python3
"""
API文档验证脚本

验证API文档中的端点是否与实际代码中的路由定义一致。
"""

import os
import re
import sys
from pathlib import Path

def extract_api_routes_from_code():
    """从代码中提取实际的API路由"""
    routes = []
    
    # 查找所有API路由文件
    api_dir = Path("app/api/v1")
    if not api_dir.exists():
        print("❌ API目录不存在")
        return routes
    
    for py_file in api_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
            
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 提取路由装饰器
        route_patterns = [
            r'@router\.(get|post|put|delete|patch)\("([^"]+)"',
            r'@router\.(get|post|put|delete|patch)\(\'([^\']+)\''
        ]
        
        for pattern in route_patterns:
            matches = re.findall(pattern, content)
            for method, path in matches:
                routes.append({
                    'method': method.upper(),
                    'path': path,
                    'file': py_file.name
                })
    
    return routes

def extract_api_routes_from_docs():
    """从API文档中提取API路由"""
    routes = []
    docs_file = Path("../docs/20_API.md")

    if not docs_file.exists():
        print("❌ API文档不存在")
        return routes
    
    with open(docs_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取HTTP方法和路径
    pattern = r'```http\n(GET|POST|PUT|DELETE|PATCH)\s+([^\n]+)\n```'
    matches = re.findall(pattern, content)
    
    for method, path in matches:
        # 清理路径中的查询参数
        clean_path = path.split('?')[0].strip()
        routes.append({
            'method': method,
            'path': clean_path
        })
    
    return routes

def get_full_api_path(route_path, router_prefix):
    """获取完整的API路径"""
    base_path = "/api/v1"
    
    # 根据文件确定前缀
    prefix_map = {
        'auth.py': '/auth',
        'projects.py': '/projects', 
        'ai.py': '/ai',
        'mention_detection.py': '/api'
    }
    
    prefix = prefix_map.get(router_prefix, '')
    
    if route_path.startswith('/'):
        return f"{base_path}{prefix}{route_path}"
    else:
        return f"{base_path}{prefix}/{route_path}"

def main():
    """主函数"""
    print("🔍 验证API文档与代码一致性")
    print("=" * 50)
    
    # 切换到backend目录
    if os.path.basename(os.getcwd()) != 'backend':
        if os.path.exists('backend'):
            os.chdir('backend')
        else:
            print("❌ 请在项目根目录或backend目录运行此脚本")
            sys.exit(1)
    
    # 提取代码中的路由
    code_routes = extract_api_routes_from_code()
    print(f"📝 从代码中找到 {len(code_routes)} 个API端点")
    
    # 提取文档中的路由
    doc_routes = extract_api_routes_from_docs()
    print(f"📚 从文档中找到 {len(doc_routes)} 个API端点")
    
    print("\n🔍 代码中的API端点:")
    for route in code_routes:
        full_path = get_full_api_path(route['path'], route['file'])
        print(f"  {route['method']} {full_path} ({route['file']})")
    
    print("\n📚 文档中的API端点:")
    for route in doc_routes:
        print(f"  {route['method']} {route['path']}")
    
    # 验证一致性
    print("\n✅ 验证结果:")
    
    # 构建代码路由的完整路径集合
    code_full_routes = set()
    for route in code_routes:
        full_path = get_full_api_path(route['path'], route['file'])
        code_full_routes.add(f"{route['method']} {full_path}")
    
    # 构建文档路由集合
    doc_full_routes = set()
    for route in doc_routes:
        doc_full_routes.add(f"{route['method']} {route['path']}")
    
    # 检查文档中但代码中没有的路由
    doc_only = doc_full_routes - code_full_routes
    if doc_only:
        print("❌ 文档中存在但代码中不存在的API:")
        for route in sorted(doc_only):
            print(f"  {route}")
    
    # 检查代码中但文档中没有的路由
    code_only = code_full_routes - doc_full_routes
    if code_only:
        print("⚠️  代码中存在但文档中缺失的API:")
        for route in sorted(code_only):
            print(f"  {route}")
    
    # 检查匹配的路由
    matching = code_full_routes & doc_full_routes
    if matching:
        print("✅ 文档与代码一致的API:")
        for route in sorted(matching):
            print(f"  {route}")
    
    print(f"\n📊 总结:")
    print(f"  代码中的API: {len(code_full_routes)}")
    print(f"  文档中的API: {len(doc_full_routes)}")
    print(f"  一致的API: {len(matching)}")
    print(f"  文档多余: {len(doc_only)}")
    print(f"  文档缺失: {len(code_only)}")
    
    if doc_only or code_only:
        print("\n❌ 发现不一致，需要更新API文档")
        sys.exit(1)
    else:
        print("\n✅ API文档与代码完全一致")

if __name__ == "__main__":
    main()
