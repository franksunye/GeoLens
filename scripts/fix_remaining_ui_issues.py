#!/usr/bin/env python3
"""
修复剩余的UI问题
处理批量更新脚本遗留的问题
"""

import os
import re
from pathlib import Path

def fix_page_file(file_path: Path):
    """修复单个页面文件"""
    print(f"修复文件: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. 修复选项卡中的双引号问题
        content = re.sub(r'st\.tabs\(\[""([^"]+)"", ""([^"]+)"", ""([^"]+)""\]\)', r'st.tabs(["\1", "\2", "\3"])', content)
        content = re.sub(r'st\.tabs\(\[""([^"]+)"", ""([^"]+)"", ""([^"]+)"", ""([^"]+)""\]\)', r'st.tabs(["\1", "\2", "\3", "\4"])', content)
        
        # 2. 修复剩余的emoji按钮
        emoji_patterns = [
            (r'st\.button\("🚀 ([^"]+)"', r'st.button("\1"'),
            (r'st\.button\("📊 ([^"]+)"', r'st.button("\1"'),
            (r'st\.button\("📁 ([^"]+)"', r'st.button("\1"'),
            (r'st\.button\("🔄 ([^"]+)"', r'st.button("\1"'),
            (r'st\.button\("🗑️ ([^"]+)"', r'st.button("\1"'),
            (r'st\.button\("📤 ([^"]+)"', r'st.button("\1"'),
            (r'st\.button\("📥 ([^"]+)"', r'st.button("\1"'),
            (r'st\.button\("💾 ([^"]+)"', r'st.button("\1"'),
            (r'st\.button\("✏️ ([^"]+)"', r'st.button("\1"'),
            (r'st\.button\("📋 ([^"]+)"', r'st.button("\1"'),
            (r'st\.button\("➕ ([^"]+)"', r'st.button("\1"'),
            (r'st\.button\("🎯 ([^"]+)"', r'st.button("\1"'),
            (r'st\.button\("🔍 ([^"]+)"', r'st.button("\1"'),
        ]
        
        for pattern, replacement in emoji_patterns:
            content = re.sub(pattern, replacement, content)
        
        # 3. 修复剩余的emoji标签
        label_patterns = [
            (r'"📅 ([^"]+)"', r'"\1"'),
            (r'"📊 ([^"]+)"', r'"\1"'),
            (r'"🏷️ ([^"]+)"', r'"\1"'),
            (r'"🤖 ([^"]+)"', r'"\1"'),
            (r'"⚙️ ([^"]+)"', r'"\1"'),
            (r'"📝 ([^"]+)"', r'"\1"'),
            (r'"🎯 ([^"]+)"', r'"\1"'),
            (r'"📁 ([^"]+)"', r'"\1"'),
            (r'"🔍 ([^"]+)"', r'"\1"'),
            (r'"📂 ([^"]+)"', r'"\1"'),
            (r'"📈 ([^"]+)"', r'"\1"'),
            (r'"🔧 ([^"]+)"', r'"\1"'),
            (r'"🌐 ([^"]+)"', r'"\1"'),
            (r'"🏷️ ([^"]+)"', r'"\1"'),
            (r'"👀 ([^"]+)"', r'"\1"'),
        ]
        
        for pattern, replacement in label_patterns:
            content = re.sub(pattern, replacement, content)
        
        # 4. 修复状态映射中的emoji
        status_mapping_pattern = r"'([^']+)': '([🌍📁🔍📜📚📊👤⚡🎯🏷️🤖📈📋🔧⚙️🔔🔗🛡️💡🎨📝📄➕✏️📋🗑️📤📥🔄💾❌✅⏳🔄📊📈📉📋📝📄]+) ([^']+)'"
        content = re.sub(status_mapping_pattern, r"'\1': '\3'", content)
        
        # 5. 修复markdown中剩余的emoji
        content = re.sub(r'st\.markdown\("#### 👀 ([^"]+)"\)', r'st.markdown("#### \1")', content)
        
        # 6. 修复download_button中的emoji
        content = re.sub(r'label="📥 ([^"]+)"', r'label="\1"', content)
        content = re.sub(r'label="📤 ([^"]+)"', r'label="\1"', content)
        
        # 7. 修复form_submit_button中的emoji
        content = re.sub(r'st\.form_submit_button\("🚀 ([^"]+)"', r'st.form_submit_button("\1"', content)
        content = re.sub(r'st\.form_submit_button\("💾 ([^"]+)"', r'st.form_submit_button("\1"', content)
        content = re.sub(r'st\.form_submit_button\("🔄 ([^"]+)"', r'st.form_submit_button("\1"', content)
        content = re.sub(r'st\.form_submit_button\("❌ ([^"]+)"', r'st.form_submit_button("\1"', content)
        content = re.sub(r'st\.form_submit_button\("🗑️ ([^"]+)"', r'st.form_submit_button("\1"', content)
        
        # 8. 修复expander中的emoji
        content = re.sub(r'st\.expander\("🤖 ([^"]+)"', r'st.expander("\1"', content)
        content = re.sub(r'st\.expander\("📄 ([^"]+)"', r'st.expander("\1"', content)
        
        # 9. 修复info/success/warning/error中的emoji
        content = re.sub(r'st\.info\("📝 ([^"]+)"\)', r'st.info("\1")', content)
        content = re.sub(r'st\.info\("📊 ([^"]+)"\)', r'st.info("\1")', content)
        content = re.sub(r'st\.info\("💡 ([^"]+)"\)', r'st.info("\1")', content)
        content = re.sub(r'st\.success\("🎉 ([^"]+)"\)', r'st.success("\1")', content)
        content = re.sub(r'st\.success\("✅ ([^"]+)"\)', r'st.success("\1")', content)
        content = re.sub(r'st\.warning\("⚠️ ([^"]+)"\)', r'st.warning("\1")', content)
        content = re.sub(r'st\.error\("❌ ([^"]+)"\)', r'st.error("\1")', content)
        
        # 10. 修复text_area和text_input中的emoji标签
        content = re.sub(r'st\.text_area\(\s*"([🌍📁🔍📜📚📊👤⚡🎯🏷️🤖📈📋🔧⚙️🔔🔗🛡️💡🎨📝📄➕✏️📋🗑️📤📥🔄💾❌✅⏳🔄📊📈📉📋📝📄]+) ([^"]+)"', r'st.text_area("\2"', content)
        content = re.sub(r'st\.text_input\(\s*"([🌍📁🔍📜📚📊👤⚡🎯🏷️🤖📈📋🔧⚙️🔔🔗🛡️💡🎨📝📄➕✏️📋🗑️📤📥🔄💾❌✅⏳🔄📊📈📉📋📝📄]+) ([^"]+)"', r'st.text_input("\2"', content)
        
        # 只有内容发生变化时才写入文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 已修复: {file_path}")
            return True
        else:
            print(f"⏭️ 无需修复: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ 修复失败 {file_path}: {e}")
        return False

def main():
    """主函数"""
    print("🔧 开始修复剩余的UI问题...")
    
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
        if fix_page_file(page_file):
            fixed_count += 1
    
    print(f"\n📊 修复完成:")
    print(f"   总文件数: {len(page_files)}")
    print(f"   已修复: {fixed_count}")
    print(f"   无需修复: {len(page_files) - fixed_count}")
    
    if fixed_count > 0:
        print(f"\n🎉 成功修复 {fixed_count} 个页面的UI问题！")
    else:
        print(f"\n✅ 所有页面UI已是最新状态")

if __name__ == "__main__":
    main()
