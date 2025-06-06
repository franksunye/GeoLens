#!/usr/bin/env python3
"""
修复页面导入错误
确保企业级主题导入在正确位置
"""

import os
import re
from pathlib import Path

def fix_page_imports(file_path: Path):
    """修复单个页面文件的导入"""
    print(f"修复导入: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 检查是否已经有正确的导入
        if 'from styles.enterprise_theme import' in content:
            print(f"✅ 导入已正确: {file_path}")
            return False
        
        # 查找导入部分的结束位置
        lines = content.split('\n')
        import_end_index = -1
        page_config_start = -1
        
        for i, line in enumerate(lines):
            # 找到最后一个import语句
            if line.strip().startswith(('import ', 'from ')) and not line.strip().startswith('#'):
                import_end_index = i
            # 找到页面配置的开始
            elif 'st.set_page_config(' in line:
                page_config_start = i
                break
        
        if import_end_index == -1:
            print(f"❌ 未找到导入部分: {file_path}")
            return False
        
        # 在导入部分末尾添加企业级主题导入
        enterprise_import = 'from styles.enterprise_theme import apply_enterprise_theme, render_enterprise_header, render_status_badge'
        
        # 插入导入语句
        lines.insert(import_end_index + 1, enterprise_import)
        
        # 重新组合内容
        content = '\n'.join(lines)
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 已修复导入: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败 {file_path}: {e}")
        return False

def main():
    """主函数"""
    print("🔧 开始修复页面导入错误...")
    
    # 获取前端目录
    frontend_dir = Path(__file__).parent.parent / "frontend"
    pages_dir = frontend_dir / "pages"
    
    if not pages_dir.exists():
        print(f"❌ 页面目录不存在: {pages_dir}")
        return
    
    # 获取所有Python页面文件
    page_files = list(pages_dir.glob("*.py"))
    
    if not page_files:
        print(f"❌ 未找到页面文件: {pages_dir}")
        return
    
    print(f"📋 找到 {len(page_files)} 个页面文件")
    
    fixed_count = 0
    
    # 修复每个页面文件
    for page_file in page_files:
        if fix_page_imports(page_file):
            fixed_count += 1
    
    print(f"\n📊 修复完成:")
    print(f"   总文件数: {len(page_files)}")
    print(f"   已修复: {fixed_count}")
    print(f"   无需修复: {len(page_files) - fixed_count}")
    
    if fixed_count > 0:
        print(f"\n🎉 成功修复 {fixed_count} 个页面的导入问题！")
    else:
        print(f"\n✅ 所有页面导入已正确")

if __name__ == "__main__":
    main()
