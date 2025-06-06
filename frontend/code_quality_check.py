#!/usr/bin/env python3
"""
GeoLens Frontend 代码质量检查脚本
分析代码质量、性能问题和最佳实践
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Any, Set
import json

class CodeQualityAnalyzer:
    """代码质量分析器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues = []
        self.metrics = {
            'total_files': 0,
            'total_lines': 0,
            'total_functions': 0,
            'total_classes': 0,
            'duplicated_code_blocks': 0,
            'long_functions': 0,
            'complex_functions': 0,
            'missing_docstrings': 0
        }
    
    def analyze_project(self) -> Dict[str, Any]:
        """分析整个项目"""
        print("🔍 开始代码质量分析...")
        
        # 获取所有Python文件
        python_files = list(self.project_root.glob("**/*.py"))
        self.metrics['total_files'] = len(python_files)
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
                
            self._analyze_file(file_path)
        
        # 检查重复代码
        self._check_code_duplication(python_files)
        
        return {
            'metrics': self.metrics,
            'issues': self.issues,
            'recommendations': self._generate_recommendations()
        }
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """检查是否应该跳过文件"""
        skip_patterns = [
            '__pycache__',
            '.git',
            'venv',
            'env',
            '.pytest_cache',
            'test_',
            '__init__.py'
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _analyze_file(self, file_path: Path):
        """分析单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 基本指标
            lines = content.split('\n')
            self.metrics['total_lines'] += len(lines)
            
            # AST分析
            try:
                tree = ast.parse(content)
                self._analyze_ast(tree, file_path)
            except SyntaxError as e:
                self.issues.append({
                    'type': 'syntax_error',
                    'file': str(file_path),
                    'line': e.lineno,
                    'message': f"语法错误: {e.msg}",
                    'severity': 'error'
                })
            
            # 文本分析
            self._analyze_text(content, file_path)
            
        except Exception as e:
            self.issues.append({
                'type': 'file_error',
                'file': str(file_path),
                'message': f"文件分析失败: {str(e)}",
                'severity': 'warning'
            })
    
    def _analyze_ast(self, tree: ast.AST, file_path: Path):
        """分析AST"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._analyze_function(node, file_path)
            elif isinstance(node, ast.ClassDef):
                self._analyze_class(node, file_path)
    
    def _analyze_function(self, node: ast.FunctionDef, file_path: Path):
        """分析函数"""
        self.metrics['total_functions'] += 1
        
        # 检查函数长度
        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
            func_length = node.end_lineno - node.lineno
            if func_length > 50:
                self.metrics['long_functions'] += 1
                self.issues.append({
                    'type': 'long_function',
                    'file': str(file_path),
                    'line': node.lineno,
                    'function': node.name,
                    'length': func_length,
                    'message': f"函数 '{node.name}' 过长 ({func_length} 行)",
                    'severity': 'warning'
                })
        
        # 检查函数复杂度（简单的圈复杂度）
        complexity = self._calculate_complexity(node)
        if complexity > 10:
            self.metrics['complex_functions'] += 1
            self.issues.append({
                'type': 'complex_function',
                'file': str(file_path),
                'line': node.lineno,
                'function': node.name,
                'complexity': complexity,
                'message': f"函数 '{node.name}' 复杂度过高 ({complexity})",
                'severity': 'warning'
            })
        
        # 检查文档字符串
        if not ast.get_docstring(node):
            self.metrics['missing_docstrings'] += 1
            self.issues.append({
                'type': 'missing_docstring',
                'file': str(file_path),
                'line': node.lineno,
                'function': node.name,
                'message': f"函数 '{node.name}' 缺少文档字符串",
                'severity': 'info'
            })
    
    def _analyze_class(self, node: ast.ClassDef, file_path: Path):
        """分析类"""
        self.metrics['total_classes'] += 1
        
        # 检查类文档字符串
        if not ast.get_docstring(node):
            self.issues.append({
                'type': 'missing_docstring',
                'file': str(file_path),
                'line': node.lineno,
                'class': node.name,
                'message': f"类 '{node.name}' 缺少文档字符串",
                'severity': 'info'
            })
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """计算函数复杂度"""
        complexity = 1  # 基础复杂度
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _analyze_text(self, content: str, file_path: Path):
        """文本分析"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 检查行长度
            if len(line) > 120:
                self.issues.append({
                    'type': 'long_line',
                    'file': str(file_path),
                    'line': i,
                    'length': len(line),
                    'message': f"行过长 ({len(line)} 字符)",
                    'severity': 'info'
                })
            
            # 检查TODO/FIXME注释
            if re.search(r'#\s*(TODO|FIXME|XXX)', line, re.IGNORECASE):
                self.issues.append({
                    'type': 'todo_comment',
                    'file': str(file_path),
                    'line': i,
                    'message': "发现TODO/FIXME注释",
                    'severity': 'info'
                })
            
            # 检查print语句（可能是调试代码）
            if re.search(r'\bprint\s*\(', line) and 'logger' not in line:
                self.issues.append({
                    'type': 'debug_print',
                    'file': str(file_path),
                    'line': i,
                    'message': "发现print语句，建议使用日志",
                    'severity': 'info'
                })
    
    def _check_code_duplication(self, python_files: List[Path]):
        """检查代码重复"""
        # 简单的重复代码检测
        code_blocks = {}
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 检查连续的5行代码
                for i in range(len(lines) - 4):
                    block = ''.join(lines[i:i+5]).strip()
                    if len(block) > 100:  # 只检查有意义的代码块
                        block_hash = hash(block)
                        
                        if block_hash in code_blocks:
                            self.metrics['duplicated_code_blocks'] += 1
                            self.issues.append({
                                'type': 'code_duplication',
                                'file': str(file_path),
                                'line': i + 1,
                                'duplicate_file': code_blocks[block_hash]['file'],
                                'duplicate_line': code_blocks[block_hash]['line'],
                                'message': "发现重复代码块",
                                'severity': 'warning'
                            })
                        else:
                            code_blocks[block_hash] = {
                                'file': str(file_path),
                                'line': i + 1
                            }
            
            except Exception:
                continue
    
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于指标生成建议
        if self.metrics['long_functions'] > 0:
            recommendations.append(
                f"发现 {self.metrics['long_functions']} 个过长函数，建议拆分为更小的函数"
            )
        
        if self.metrics['complex_functions'] > 0:
            recommendations.append(
                f"发现 {self.metrics['complex_functions']} 个复杂函数，建议简化逻辑或拆分函数"
            )
        
        if self.metrics['missing_docstrings'] > 5:
            recommendations.append(
                f"发现 {self.metrics['missing_docstrings']} 个缺少文档字符串的函数/类，建议添加文档"
            )
        
        if self.metrics['duplicated_code_blocks'] > 0:
            recommendations.append(
                f"发现 {self.metrics['duplicated_code_blocks']} 个重复代码块，建议提取公共函数"
            )
        
        # 基于问题类型生成建议
        error_count = len([i for i in self.issues if i['severity'] == 'error'])
        warning_count = len([i for i in self.issues if i['severity'] == 'warning'])
        
        if error_count > 0:
            recommendations.append(f"发现 {error_count} 个错误，需要立即修复")
        
        if warning_count > 10:
            recommendations.append(f"发现 {warning_count} 个警告，建议逐步改进")
        
        return recommendations

def generate_report(analysis_result: Dict[str, Any]) -> str:
    """生成分析报告"""
    metrics = analysis_result['metrics']
    issues = analysis_result['issues']
    recommendations = analysis_result['recommendations']
    
    report = []
    report.append("# 🔍 GeoLens Frontend 代码质量分析报告")
    report.append("")
    report.append("## 📊 代码指标")
    report.append("")
    report.append(f"- **总文件数**: {metrics['total_files']}")
    report.append(f"- **总代码行数**: {metrics['total_lines']}")
    report.append(f"- **函数数量**: {metrics['total_functions']}")
    report.append(f"- **类数量**: {metrics['total_classes']}")
    report.append("")
    
    # 质量指标
    report.append("## 🎯 质量指标")
    report.append("")
    report.append(f"- **过长函数**: {metrics['long_functions']}")
    report.append(f"- **复杂函数**: {metrics['complex_functions']}")
    report.append(f"- **缺少文档**: {metrics['missing_docstrings']}")
    report.append(f"- **重复代码块**: {metrics['duplicated_code_blocks']}")
    report.append("")
    
    # 问题统计
    error_count = len([i for i in issues if i['severity'] == 'error'])
    warning_count = len([i for i in issues if i['severity'] == 'warning'])
    info_count = len([i for i in issues if i['severity'] == 'info'])
    
    report.append("## 🚨 问题统计")
    report.append("")
    report.append(f"- **错误**: {error_count}")
    report.append(f"- **警告**: {warning_count}")
    report.append(f"- **信息**: {info_count}")
    report.append("")
    
    # 主要问题
    if issues:
        report.append("## 🔧 主要问题")
        report.append("")
        
        # 按严重程度分组
        for severity in ['error', 'warning']:
            severity_issues = [i for i in issues if i['severity'] == severity]
            if severity_issues:
                severity_name = "错误" if severity == 'error' else "警告"
                report.append(f"### {severity_name}")
                report.append("")
                
                for issue in severity_issues[:10]:  # 只显示前10个
                    file_name = Path(issue['file']).name
                    line = issue.get('line', '?')
                    message = issue['message']
                    report.append(f"- **{file_name}:{line}** - {message}")
                
                if len(severity_issues) > 10:
                    report.append(f"- ... 还有 {len(severity_issues) - 10} 个{severity_name}")
                
                report.append("")
    
    # 改进建议
    if recommendations:
        report.append("## 💡 改进建议")
        report.append("")
        for i, rec in enumerate(recommendations, 1):
            report.append(f"{i}. {rec}")
        report.append("")
    
    # 总体评分
    total_issues = len(issues)
    total_functions = metrics['total_functions']
    
    if total_functions > 0:
        quality_score = max(0, 100 - (total_issues / total_functions * 10))
        report.append("## 📈 质量评分")
        report.append("")
        report.append(f"**总体质量评分**: {quality_score:.1f}/100")
        report.append("")
        
        if quality_score >= 90:
            report.append("✅ **优秀** - 代码质量很高")
        elif quality_score >= 80:
            report.append("🟡 **良好** - 代码质量较好，有改进空间")
        elif quality_score >= 70:
            report.append("🟠 **一般** - 代码质量一般，建议改进")
        else:
            report.append("🔴 **需要改进** - 代码质量较差，需要重点改进")
    
    return "\n".join(report)

def main():
    """主函数"""
    print("🌍 GeoLens Frontend 代码质量检查工具")
    print("=" * 60)
    
    # 分析代码
    analyzer = CodeQualityAnalyzer(".")
    result = analyzer.analyze_project()
    
    # 生成报告
    report = generate_report(result)
    
    # 保存报告
    report_file = Path("code_quality_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 输出摘要
    print("\n📊 分析完成！")
    print(f"📁 分析文件: {result['metrics']['total_files']}")
    print(f"📝 代码行数: {result['metrics']['total_lines']}")
    print(f"🔧 发现问题: {len(result['issues'])}")
    print(f"💡 改进建议: {len(result['recommendations'])}")
    print(f"📄 详细报告: {report_file}")
    
    # 保存JSON数据
    json_file = Path("code_quality_data.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"📊 数据文件: {json_file}")

if __name__ == "__main__":
    main()
