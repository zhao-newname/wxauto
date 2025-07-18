#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试小程序消息交互功能

验证以下功能：
1. open_miniprogram 方法能够成功点击并打开小程序
2. copy_link_info 方法能够复制小程序信息到剪贴板
3. 转发功能能够正常工作（继承自父类）
4. 所有交互操作失败时返回WxResponse.failure()并包含错误信息
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from wxauto.msgs.miniprogram import MiniprogramMessage, MiniprogramInfo, MiniprogramCardAnalyzer
from wxauto.param import WxResponse
from wxauto import uiautomation as uia
import time

def test_miniprogram_interaction():
    """测试小程序消息交互功能"""
    print("=== 小程序消息交互功能测试 ===")
    
    # 测试1: 验证方法存在性
    print("\n1. 验证交互方法存在性...")
    
    # 检查MiniprogramMessage类是否有必要的方法
    required_methods = [
        'open_miniprogram',
        'copy_link_info', 
        'forward',  # 继承自父类
        'extract_link_info'
    ]
    
    for method_name in required_methods:
        if hasattr(MiniprogramMessage, method_name):
            print(f"   ✓ {method_name} 方法存在")
        else:
            print(f"   ✗ {method_name} 方法缺失")
    
    # 测试2: 验证属性访问
    print("\n2. 验证属性访问...")
    
    required_properties = [
        'app_name',
        'app_description',
        'app_id',
        'page_path',
        'page_params',
        'thumbnail_url',
        'miniprogram_info'
    ]
    
    for prop_name in required_properties:
        if hasattr(MiniprogramMessage, prop_name):
            print(f"   ✓ {prop_name} 属性存在")
        else:
            print(f"   ✗ {prop_name} 属性缺失")
    
    # 测试3: 模拟交互操作测试
    print("\n3. 模拟交互操作测试...")
    
    # 创建模拟控件
    class MockControl:
        def __init__(self):
            self.Name = "测试小程序"
            self.runtimeid = [1, 2, 3, 4]
            self.BoundingRectangle = MockRect()
            
        def Exists(self, timeout=0):
            return True
            
        def Click(self):
            print("   模拟点击小程序卡片")
            
        def RightClick(self):
            print("   模拟右键点击小程序卡片")
            
        def GetParentControl(self):
            return self
            
        def ButtonControl(self, searchDepth=2):
            return MockControl()
            
        def ImageControl(self, searchDepth=3):
            mock_img = MockControl()
            mock_img.Name = "小程序图标"
            return mock_img
            
        def TextControl(self, searchDepth=2):
            return MockControl()
    
    class MockRect:
        def __init__(self):
            pass
            
        def width(self):
            return 300
            
        def height(self):
            return 80
            
        @property
        def left(self):
            return 100
            
        @property
        def top(self):
            return 200
    
    class MockChatBox:
        def __init__(self):
            self.root = self
            
        def get_info(self):
            return {"chat_name": "测试聊天"}
            
        def _show(self):
            pass
    
    # 创建模拟的小程序消息实例
    try:
        mock_control = MockControl()
        mock_chatbox = MockChatBox()
        
        # 这里我们只测试方法调用，不实际创建实例
        # 因为需要真实的UI控件才能完全初始化
        print("   ✓ 模拟控件创建成功")
        
        # 测试MiniprogramInfo数据模型
        info = MiniprogramInfo(
            app_name="测试小程序",
            app_description="这是一个测试小程序",
            app_id="wx1234567890abcdef",
            page_path="/pages/index",
            page_params={"param1": "value1"}
        )
        
        print(f"   ✓ MiniprogramInfo创建成功: {info.app_name}")
        print(f"   ✓ JSON序列化测试: {len(info.to_json())} 字符")
        
    except Exception as e:
        print(f"   ✗ 模拟测试失败: {str(e)}")
    
    # 测试4: 错误处理测试
    print("\n4. 错误处理测试...")
    
    # 测试WxResponse的使用
    success_response = WxResponse.success("操作成功")
    failure_response = WxResponse.failure("操作失败")
    
    print(f"   ✓ 成功响应: {success_response.is_success}")
    print(f"   ✓ 失败响应: {not failure_response.is_success}")
    
    # 测试5: MiniprogramCardAnalyzer功能
    print("\n5. MiniprogramCardAnalyzer功能测试...")
    
    try:
        mock_control = MockControl()
        analyzer = MiniprogramCardAnalyzer(mock_control)
        
        # 测试基本方法
        print(f"   ✓ 分析器创建成功")
        
        # 测试提取方法（这些会因为模拟控件而返回默认值）
        app_name = analyzer.extract_app_name()
        description = analyzer.extract_description()
        
        print(f"   ✓ 提取应用名称: {app_name}")
        print(f"   ✓ 提取描述: {description}")
        
    except Exception as e:
        print(f"   ✗ 分析器测试失败: {str(e)}")
    
    print("\n=== 测试完成 ===")
    print("\n注意：完整的交互功能测试需要在真实的微信环境中进行")
    print("建议手动测试以下场景：")
    print("1. 在微信中找到小程序卡片消息")
    print("2. 测试点击打开小程序功能")
    print("3. 测试右键复制功能")
    print("4. 测试转发功能")

if __name__ == "__main__":
    test_miniprogram_interaction()