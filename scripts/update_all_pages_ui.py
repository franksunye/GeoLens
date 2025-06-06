#!/usr/bin/env python3
"""
批量更新所有页面的企业级UI
去除emoji，应用企业级设计
"""

import os
import re
from pathlib import Path

def update_page_file(file_path: Path):
    """更新单个页面文件"""
    print(f"更新文件: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. 添加企业级主题导入
        if 'from styles.enterprise_theme import' not in content:
            # 找到最后一个import语句
            import_lines = []
            other_lines = []
            in_imports = True
            
            for line in content.split('\n'):
                if line.strip().startswith('from ') or line.strip().startswith('import '):
                    if in_imports:
                        import_lines.append(line)
                    else:
                        other_lines.append(line)
                elif line.strip() == '' and in_imports:
                    import_lines.append(line)
                else:
                    in_imports = False
                    other_lines.append(line)
            
            # 添加企业级主题导入
            import_lines.append('from styles.enterprise_theme import apply_enterprise_theme, render_enterprise_header, render_status_badge')
            
            content = '\n'.join(import_lines + other_lines)
        
        # 2. 添加主题应用
        if 'apply_enterprise_theme()' not in content:
            # 在页面配置后添加主题应用
            content = re.sub(
                r'(st\.set_page_config\([^)]+\))',
                r'\1\n\n# 应用企业级主题\napply_enterprise_theme()',
                content
            )
        
        # 3. 替换页面标题
        content = re.sub(
            r'st\.markdown\("# [🌍📁🔍📜📚📊👤⚡🎯🏷️🤖📈📋🔧⚙️🔔🔗🛡️💡🎨📝📄➕✏️📋🗑️📤📥🔄💾❌✅⏳🔄📊📈📉📋📝📄📊📈📉📋📝📄]+ ([^"]+)"\)',
            r'render_enterprise_header("\1", "")',
            content
        )
        
        # 4. 去除标题中的emoji
        content = re.sub(
            r'st\.markdown\("# ([🌍📁🔍📜📚📊👤⚡🎯🏷️🤖📈📋🔧⚙️🔔🔗🛡️💡🎨📝📄➕✏️📋🗑️📤📥🔄💾❌✅⏳🔄📊📈📉📋📝📄]+) ([^"]+)"\)',
            r'render_enterprise_header("\2", "")',
            content
        )
        
        # 5. 去除子标题中的emoji
        content = re.sub(
            r'st\.markdown\("### ([🌍📁🔍📜📚📊👤⚡🎯🏷️🤖📈📋🔧⚙️🔔🔗🛡️💡🎨📝📄➕✏️📋🗑️📤📥🔄💾❌✅⏳🔄📊📈📉📋📝📄]+) ([^"]+)"\)',
            r'st.markdown("### \2")',
            content
        )
        
        # 6. 去除按钮中的emoji
        content = re.sub(
            r'st\.button\("([🌍📁🔍📜📚📊👤⚡🎯🏷️🤖📈📋🔧⚙️🔔🔗🛡️💡🎨📝📄➕✏️📋🗑️📤📥🔄💾❌✅⏳🔄📊📈📉📋📝📄]+) ([^"]+)"',
            r'st.button("\2"',
            content
        )
        
        # 7. 去除表单标签中的emoji
        content = re.sub(
            r'"([🌍📁🔍📜📚📊👤⚡🎯🏷️🤖📈📋🔧⚙️🔔🔗🛡️💡🎨📝📄➕✏️📋🗑️📤📥🔄💾❌✅⏳🔄📊📈📉📋📝📄]+) ([^"]+)"',
            r'"\2"',
            content
        )
        
        # 8. 去除选项卡中的emoji
        content = re.sub(
            r'st\.tabs\(\[([^\]]+)\]\)',
            lambda m: 'st.tabs([' + ', '.join([
                f'"{item.strip().split(" ", 1)[-1] if any(emoji in item for emoji in "🌍📁🔍📜📚📊👤⚡🎯🏷️🤖📈📋🔧⚙️🔔🔗🛡️💡🎨📝📄➕✏️📋🗑️📤📥🔄💾❌✅⏳🔄📊📈📉📋📝📄") else item.strip()}"'
                for item in m.group(1).split(',')
            ]) + '])',
            content
        )
        
        # 9. 去除指标标签中的emoji
        content = re.sub(
            r'st\.metric\(\s*"([🌍📁🔍📜📚📊👤⚡🎯🏷️🤖📈📋🔧⚙️🔔🔗🛡️💡🎨📝📄➕✏️📋🗑️📤📥🔄💾❌✅⏳🔄📊📈📉📋📝📄]+) ([^"]+)"',
            r'st.metric("\2"',
            content
        )
        
        # 10. 去除selectbox标签中的emoji
        content = re.sub(
            r'st\.selectbox\(\s*"([🌍📁🔍📜📚📊👤⚡🎯🏷️🤖📈📋🔧⚙️🔔🔗🛡️💡🎨📝📄➕✏️📋🗑️📤📥🔄💾❌✅⏳🔄📊📈📉📋📝📄]+) ([^"]+)"',
            r'st.selectbox("\2"',
            content
        )
        
        # 11. 去除text_input标签中的emoji
        content = re.sub(
            r'st\.text_input\(\s*"([🌍📁🔍📜📚📊👤⚡🎯🏷️🤖📈📋🔧⚙️🔔🔗🛡️💡🎨📝📄➕✏️📋🗑️📤📥🔄💾❌✅⏳🔄📊📈📉📋📝📄]+) ([^"]+)"',
            r'st.text_input("\2"',
            content
        )
        
        # 12. 去除multiselect标签中的emoji
        content = re.sub(
            r'st\.multiselect\(\s*"([🌍📁🔍📜📚📊👤⚡🎯🏷️🤖📈📋🔧⚙️🔔🔗🛡️💡🎨📝📄➕✏️📋🗑️📤📥🔄💾❌✅⏳🔄📊📈📉📋📝📄]+) ([^"]+)"',
            r'st.multiselect("\2"',
            content
        )
        
        # 13. 去除expander标签中的emoji
        content = re.sub(
            r'st\.expander\("([🌍📁🔍📜📚📊👤⚡🎯🏷️🤖📈📋🔧⚙️🔔🔗🛡️💡🎨📝📄➕✏️📋🗑️📤📥🔄💾❌✅⏳🔄📊📈📉📋📝📄]+) ([^"]+)"',
            r'st.expander("\2"',
            content
        )
        
        # 14. 去除状态消息中的emoji
        content = re.sub(
            r'st\.(info|success|warning|error)\("([🌍📁🔍📜📚📊👤⚡🎯🏷️🤖📈📋🔧⚙️🔔🔗🛡️💡🎨📝📄➕✏️📋🗑️📤📥🔄💾❌✅⏳🔄📊📈📉📋📝📄]+) ([^"]+)"',
            r'st.\1("\3"',
            content
        )
        
        # 15. 去除markdown中的emoji标题
        content = re.sub(
            r'st\.markdown\("#### ([🌍📁🔍📜📚📊👤⚡🎯🏷️🤖📈📋🔧⚙️🔔🔗🛡️💡🎨📝📄➕✏️📋🗑️📤📥🔄💾❌✅⏳🔄📊📈📉📋📝📄]+) ([^"]+)"\)',
            r'st.markdown("#### \2")',
            content
        )
        
        # 16. 处理特殊的页面标题格式
        if 'render_enterprise_header' not in content and 'st.markdown("# ' in content:
            # 查找主标题并替换
            title_match = re.search(r'st\.markdown\("# ([^"]+)"\)', content)
            if title_match:
                title = title_match.group(1)
                # 去除emoji
                clean_title = re.sub(r'[🌍📁🔍📜📚📊👤⚡🎯🏷️🤖📈📋🔧⚙️🔔🔗🛡️💡🎨📝📄➕✏️📋🗑️📤📥🔄💾❌✅⏳🔄📊📈📉📋📝📄]+ ', '', title)
                content = content.replace(
                    f'st.markdown("# {title}")',
                    f'render_enterprise_header("{clean_title}", "")'
                )
        
        # 只有内容发生变化时才写入文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 已更新: {file_path}")
            return True
        else:
            print(f"⏭️ 无需更新: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ 更新失败 {file_path}: {e}")
        return False

def main():
    """主函数"""
    print("🎨 开始批量更新页面企业级UI...")
    
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
    
    updated_count = 0
    
    # 更新每个页面文件
    for page_file in page_files:
        if update_page_file(page_file):
            updated_count += 1
    
    print(f"\n📊 更新完成:")
    print(f"   总文件数: {len(page_files)}")
    print(f"   已更新: {updated_count}")
    print(f"   无需更新: {len(page_files) - updated_count}")
    
    if updated_count > 0:
        print(f"\n🎉 成功更新 {updated_count} 个页面的企业级UI！")
    else:
        print(f"\n✅ 所有页面已是最新的企业级UI")

if __name__ == "__main__":
    main()
