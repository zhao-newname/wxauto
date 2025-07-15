#!/usr/bin/env python3
"""
验证miniprogram.py文件的基本结构和语法
"""

import ast
import inspect

def verify_miniprogram_file():
    """验证miniprogram.py文件"""
    print("验证miniprogram.py文件结构...")
    
    # 读取文件内容
    with open('wxauto/msgs/miniprogram.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析AST
    try:
        tree = ast.parse(content)
        print("✅ 语法检查通过")
    except SyntaxError as e:
        print(f"❌ 语法错误: {e}")
        return False
    
    # 检查类定义
    classes = {}
    functions = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes[node.name] = {
                'bases': [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases],
                'methods': []
            }
            
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    classes[node.name]['methods'].append(item.name)
        
        elif isinstance(node, ast.FunctionDef) and not hasattr(node, 'parent_class'):
            functions[node.name] = True
    
    print(f"\n发现的类: {list(classes.keys())}")
    print(f"发现的函数: {list(functions.keys())}")
    
    # 验证MiniprogramInfo类
    if 'MiniprogramInfo' in classes:
        print("\n✅ MiniprogramInfo类已定义")
        info_methods = classes['MiniprogramInfo']['methods']
        required_methods = ['to_dict', 'to_json']
        for method in required_methods:
            if method in info_methods:
                print(f"   ✅ {method}方法已定义")
            else:
                print(f"   ❌ 缺少{method}方法")
    else:
        print("❌ 未找到MiniprogramInfo类")
        return False
    
    # 验证MiniprogramMessage类
    if 'MiniprogramMessage' in classes:
        print("\n✅ MiniprogramMessage类已定义")
        msg_info = classes['MiniprogramMessage']
        
        # 检查继承
        if 'HumanMessage' in msg_info['bases']:
            print("   ✅ 正确继承自HumanMessage")
        else:
            print(f"   ❌ 继承关系错误: {msg_info['bases']}")
        
        # 检查必要方法
        required_methods = [
            '__init__', '_parse_miniprogram_info', '_extract_app_name', 
            '_extract_app_description', 'extract_link_info', 
            'open_miniprogram', 'copy_link_info'
        ]
        
        msg_methods = msg_info['methods']
        for method in required_methods:
            if method in msg_methods:
                print(f"   ✅ {method}方法已定义")
            else:
                print(f"   ❌ 缺少{method}方法")
        
        # 检查属性方法
        property_methods = [
            'app_name', 'app_description', 'app_id', 'page_path', 
            'page_params', 'thumbnail_url', 'miniprogram_info'
        ]
        
        for prop in property_methods:
            if prop in msg_methods:
                print(f"   ✅ {prop}属性方法已定义")
            else:
                print(f"   ❌ 缺少{prop}属性方法")
                
    else:
        print("❌ 未找到MiniprogramMessage类")
        return False
    
    # 检查导入语句
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imports.append(f"from {node.module} import {', '.join([alias.name for alias in node.names])}")
        elif isinstance(node, ast.Import):
            imports.append(f"import {', '.join([alias.name for alias in node.names])}")
    
    print(f"\n导入语句:")
    for imp in imports:
        print(f"   {imp}")
    
    print("\n🎉 文件结构验证完成！")
    return True

if __name__ == "__main__":
    verify_miniprogram_file()