#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API集成测试脚本

测试新添加的小程序消息相关API方法是否正常工作，包括：
- Chat类的GetMiniprogramMessages方法
- WeChat类的小程序相关便捷方法
- 新方法的返回值和类型注解
- 向后兼容性验证
"""

import sys
import os
import traceback
from typing import List, Dict, Any
import inspect

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from wxauto import WeChat, Chat
    from wxauto.msgs.miniprogram import MiniprogramMessage
    from wxauto.utils.miniprogram_extractor import MiniprogramExtractor
    from wxauto.param import WxResponse
    print("✅ 成功导入所有必需的模块")
except ImportError as e:
    print(f"❌ 导入模块失败: {str(e)}")
    sys.exit(1)


class APIIntegrationTester:
    """API集成测试器"""
    
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """记录测试结果"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status} - {test_name}"
        if message:
            result += f": {message}"
        
        print(result)
        self.test_results.append((test_name, passed, message))
    
    def test_chat_class_methods(self):
        """测试Chat类的新方法"""
        print("\n=== 测试Chat类新方法 ===")
        
        # 测试方法是否存在
        chat_methods = [
            'GetMiniprogramMessages',
            'FilterMiniprogramByApp', 
            'GetMiniprogramStatistics',
            'ExportMiniprogramMessages'
        ]
        
        for method_name in chat_methods:
            try:
                method = getattr(Chat, method_name, None)
                if method and callable(method):
                    self.log_test(f"Chat.{method_name} 方法存在", True)
                    
                    # 检查方法签名和文档字符串
                    sig = inspect.signature(method)
                    doc = method.__doc__
                    
                    if doc and len(doc.strip()) > 10:
                        self.log_test(f"Chat.{method_name} 有文档字符串", True)
                    else:
                        self.log_test(f"Chat.{method_name} 有文档字符串", False, "缺少或过短的文档字符串")
                        
                    # 检查类型注解
                    if sig.return_annotation != inspect.Signature.empty:
                        self.log_test(f"Chat.{method_name} 有返回类型注解", True)
                    else:
                        self.log_test(f"Chat.{method_name} 有返回类型注解", False, "缺少返回类型注解")
                        
                else:
                    self.log_test(f"Chat.{method_name} 方法存在", False, "方法不存在或不可调用")
                    
            except Exception as e:
                self.log_test(f"Chat.{method_name} 方法检查", False, f"检查异常: {str(e)}")
    
    def test_wechat_class_methods(self):
        """测试WeChat类的新方法"""
        print("\n=== 测试WeChat类新方法 ===")
        
        # 测试WeChat类特有的方法
        wechat_methods = [
            'GetAllMiniprogramMessages',
            'SearchMiniprogramByApp',
            'GetMiniprogramSummary', 
            'ExportCurrentChatMiniprogram',
            'GetRecentMiniprogramMessages',
            'FindDuplicateMiniprogram',
            'FilterMiniprogramBySender'
        ]
        
        for method_name in wechat_methods:
            try:
                method = getattr(WeChat, method_name, None)
                if method and callable(method):
                    self.log_test(f"WeChat.{method_name} 方法存在", True)
                    
                    # 检查方法签名和文档字符串
                    sig = inspect.signature(method)
                    doc = method.__doc__
                    
                    if doc and len(doc.strip()) > 10:
                        self.log_test(f"WeChat.{method_name} 有文档字符串", True)
                    else:
                        self.log_test(f"WeChat.{method_name} 有文档字符串", False, "缺少或过短的文档字符串")
                        
                    # 检查类型注解
                    if sig.return_annotation != inspect.Signature.empty:
                        self.log_test(f"WeChat.{method_name} 有返回类型注解", True)
                    else:
                        self.log_test(f"WeChat.{method_name} 有返回类型注解", False, "缺少返回类型注解")
                        
                else:
                    self.log_test(f"WeChat.{method_name} 方法存在", False, "方法不存在或不可调用")
                    
            except Exception as e:
                self.log_test(f"WeChat.{method_name} 方法检查", False, f"检查异常: {str(e)}")
    
    def test_inheritance_relationship(self):
        """测试继承关系"""
        print("\n=== 测试继承关系 ===")
        
        try:
            # WeChat应该继承自Chat
            if issubclass(WeChat, Chat):
                self.log_test("WeChat继承自Chat", True)
                
                # WeChat应该能访问Chat的所有小程序方法
                chat_miniprogram_methods = [
                    'GetMiniprogramMessages',
                    'FilterMiniprogramByApp',
                    'GetMiniprogramStatistics', 
                    'ExportMiniprogramMessages'
                ]
                
                for method_name in chat_miniprogram_methods:
                    if hasattr(WeChat, method_name):
                        self.log_test(f"WeChat可访问Chat.{method_name}", True)
                    else:
                        self.log_test(f"WeChat可访问Chat.{method_name}", False, "方法不可访问")
                        
            else:
                self.log_test("WeChat继承自Chat", False, "继承关系不正确")
                
        except Exception as e:
            self.log_test("继承关系测试", False, f"测试异常: {str(e)}")
    
    def test_miniprogram_extractor_integration(self):
        """测试MiniprogramExtractor集成"""
        print("\n=== 测试MiniprogramExtractor集成 ===")
        
        try:
            # 测试MiniprogramExtractor类是否存在
            if MiniprogramExtractor:
                self.log_test("MiniprogramExtractor类存在", True)
                
                # 测试关键方法是否存在
                extractor_methods = [
                    'extract_all_miniprogram_messages',
                    'filter_by_app_name',
                    'filter_by_sender',
                    'get_statistics',
                    'export_to_json'
                ]
                
                for method_name in extractor_methods:
                    if hasattr(MiniprogramExtractor, method_name):
                        self.log_test(f"MiniprogramExtractor.{method_name} 存在", True)
                    else:
                        self.log_test(f"MiniprogramExtractor.{method_name} 存在", False, "方法不存在")
                        
            else:
                self.log_test("MiniprogramExtractor类存在", False, "类不存在")
                
        except Exception as e:
            self.log_test("MiniprogramExtractor集成测试", False, f"测试异常: {str(e)}")
    
    def test_backward_compatibility(self):
        """测试向后兼容性"""
        print("\n=== 测试向后兼容性 ===")
        
        try:
            # 测试原有的Chat方法是否仍然存在
            original_chat_methods = [
                'SendMsg',
                'SendFiles',
                'GetAllMessage',
                'GetNewMessage',
                'GetGroupMembers',
                'ChatInfo',
                'LoadMoreMessage',
                'Show',
                'Close'
            ]
            
            for method_name in original_chat_methods:
                if hasattr(Chat, method_name):
                    self.log_test(f"Chat.{method_name} 向后兼容", True)
                else:
                    self.log_test(f"Chat.{method_name} 向后兼容", False, "原有方法丢失")
            
            # 测试原有的WeChat方法是否仍然存在
            original_wechat_methods = [
                'ChatWith',
                'AddListenChat',
                'RemoveListenChat',
                'GetSession',
                'GetNextNewMessage',
                'SwitchToChat',
                'SwitchToContact',
                'GetSubWindow',
                'GetAllSubWindow',
                'StopListening',
                'StartListening',
                'KeepRunning'
            ]
            
            for method_name in original_wechat_methods:
                if hasattr(WeChat, method_name):
                    self.log_test(f"WeChat.{method_name} 向后兼容", True)
                else:
                    self.log_test(f"WeChat.{method_name} 向后兼容", False, "原有方法丢失")
                    
        except Exception as e:
            self.log_test("向后兼容性测试", False, f"测试异常: {str(e)}")
    
    def test_method_signatures(self):
        """测试方法签名的正确性"""
        print("\n=== 测试方法签名 ===")
        
        try:
            # 测试GetMiniprogramMessages方法签名
            method = getattr(Chat, 'GetMiniprogramMessages', None)
            if method:
                sig = inspect.signature(method)
                params = list(sig.parameters.keys())
                
                # 应该有self和use_cache参数
                expected_params = ['self', 'use_cache']
                if all(param in params for param in expected_params):
                    self.log_test("GetMiniprogramMessages 方法签名正确", True)
                else:
                    self.log_test("GetMiniprogramMessages 方法签名正确", False, f"参数不匹配: {params}")
            else:
                self.log_test("GetMiniprogramMessages 方法签名正确", False, "方法不存在")
            
            # 测试FilterMiniprogramByApp方法签名
            method = getattr(Chat, 'FilterMiniprogramByApp', None)
            if method:
                sig = inspect.signature(method)
                params = list(sig.parameters.keys())
                
                # 应该有self、app_name和exact_match参数
                expected_params = ['self', 'app_name', 'exact_match']
                if all(param in params for param in expected_params):
                    self.log_test("FilterMiniprogramByApp 方法签名正确", True)
                else:
                    self.log_test("FilterMiniprogramByApp 方法签名正确", False, f"参数不匹配: {params}")
            else:
                self.log_test("FilterMiniprogramByApp 方法签名正确", False, "方法不存在")
                
        except Exception as e:
            self.log_test("方法签名测试", False, f"测试异常: {str(e)}")
    
    def test_import_compatibility(self):
        """测试导入兼容性"""
        print("\n=== 测试导入兼容性 ===")
        
        try:
            # 测试从wxauto导入主要类
            from wxauto import WeChat, Chat, WxParam
            self.log_test("从wxauto导入主要类", True)
            
            # 测试导入小程序相关类
            from wxauto.msgs.miniprogram import MiniprogramMessage, MiniprogramInfo
            self.log_test("导入小程序消息类", True)
            
            # 测试导入提取器类
            from wxauto.utils.miniprogram_extractor import MiniprogramExtractor
            self.log_test("导入小程序提取器类", True)
            
        except ImportError as e:
            self.log_test("导入兼容性", False, f"导入失败: {str(e)}")
        except Exception as e:
            self.log_test("导入兼容性", False, f"测试异常: {str(e)}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始API集成测试...")
        print("=" * 50)
        
        # 运行各项测试
        self.test_import_compatibility()
        self.test_chat_class_methods()
        self.test_wechat_class_methods()
        self.test_inheritance_relationship()
        self.test_miniprogram_extractor_integration()
        self.test_backward_compatibility()
        self.test_method_signatures()
        
        # 输出测试总结
        print("\n" + "=" * 50)
        print("测试总结:")
        print(f"总测试数: {self.total_tests}")
        print(f"通过测试: {self.passed_tests}")
        print(f"失败测试: {self.total_tests - self.passed_tests}")
        print(f"通过率: {(self.passed_tests / self.total_tests * 100):.1f}%")
        
        if self.passed_tests == self.total_tests:
            print("\n🎉 所有测试通过！API集成成功！")
            return True
        else:
            print(f"\n⚠️  有 {self.total_tests - self.passed_tests} 个测试失败，请检查实现。")
            return False


def main():
    """主函数"""
    print("API集成测试脚本")
    print("测试新添加的小程序消息相关API方法")
    print("-" * 50)
    
    try:
        tester = APIIntegrationTester()
        success = tester.run_all_tests()
        
        if success:
            print("\n✅ API集成测试完成，所有功能正常！")
            sys.exit(0)
        else:
            print("\n❌ API集成测试发现问题，请修复后重试。")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 测试过程中发生异常: {str(e)}")
        print(f"异常详情:\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()