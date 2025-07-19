#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
任务12最终验证脚本

验证任务12的所有验收标准：
- Chat类已添加GetMiniprogramMessages方法
- WeChat类已添加小程序消息相关的便捷方法
- 新方法能够正确返回小程序消息列表
- 现有API功能不受影响，向后兼容性良好
"""

import sys
import os
import traceback
import inspect
from typing import List, Dict, Any

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


class Task12Verifier:
    """任务12验证器"""
    
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
    
    def verify_chat_class_methods(self):
        """验收标准1: Chat类已添加GetMiniprogramMessages方法"""
        print("\n=== 验收标准1: Chat类已添加GetMiniprogramMessages方法 ===")
        
        # 检查GetMiniprogramMessages方法
        if hasattr(Chat, 'GetMiniprogramMessages'):
            method = getattr(Chat, 'GetMiniprogramMessages')
            if callable(method):
                self.log_test("Chat.GetMiniprogramMessages 方法存在且可调用", True)
                
                # 检查方法签名
                sig = inspect.signature(method)
                params = list(sig.parameters.keys())
                if 'self' in params and 'use_cache' in params:
                    self.log_test("Chat.GetMiniprogramMessages 方法签名正确", True)
                else:
                    self.log_test("Chat.GetMiniprogramMessages 方法签名正确", False, f"参数: {params}")
                
                # 检查返回类型注解
                if sig.return_annotation != inspect.Signature.empty:
                    self.log_test("Chat.GetMiniprogramMessages 有返回类型注解", True)
                else:
                    self.log_test("Chat.GetMiniprogramMessages 有返回类型注解", False)
                
                # 检查文档字符串
                if method.__doc__ and len(method.__doc__.strip()) > 20:
                    self.log_test("Chat.GetMiniprogramMessages 有完整文档字符串", True)
                else:
                    self.log_test("Chat.GetMiniprogramMessages 有完整文档字符串", False)
            else:
                self.log_test("Chat.GetMiniprogramMessages 方法存在且可调用", False, "方法不可调用")
        else:
            self.log_test("Chat.GetMiniprogramMessages 方法存在且可调用", False, "方法不存在")
        
        # 检查其他Chat类新增方法
        other_chat_methods = [
            'FilterMiniprogramByApp',
            'GetMiniprogramStatistics', 
            'ExportMiniprogramMessages'
        ]
        
        for method_name in other_chat_methods:
            if hasattr(Chat, method_name) and callable(getattr(Chat, method_name)):
                self.log_test(f"Chat.{method_name} 方法存在", True)
            else:
                self.log_test(f"Chat.{method_name} 方法存在", False)
    
    def verify_wechat_class_methods(self):
        """验收标准2: WeChat类已添加小程序消息相关的便捷方法"""
        print("\n=== 验收标准2: WeChat类已添加小程序消息相关的便捷方法 ===")
        
        wechat_convenience_methods = [
            'GetAllMiniprogramMessages',
            'SearchMiniprogramByApp',
            'GetMiniprogramSummary',
            'ExportCurrentChatMiniprogram',
            'GetRecentMiniprogramMessages',
            'FindDuplicateMiniprogram',
            'FilterMiniprogramBySender'
        ]
        
        for method_name in wechat_convenience_methods:
            if hasattr(WeChat, method_name):
                method = getattr(WeChat, method_name)
                if callable(method):
                    self.log_test(f"WeChat.{method_name} 便捷方法存在", True)
                    
                    # 检查文档字符串
                    if method.__doc__ and len(method.__doc__.strip()) > 20:
                        self.log_test(f"WeChat.{method_name} 有文档字符串", True)
                    else:
                        self.log_test(f"WeChat.{method_name} 有文档字符串", False)
                        
                    # 检查返回类型注解
                    sig = inspect.signature(method)
                    if sig.return_annotation != inspect.Signature.empty:
                        self.log_test(f"WeChat.{method_name} 有返回类型注解", True)
                    else:
                        self.log_test(f"WeChat.{method_name} 有返回类型注解", False)
                else:
                    self.log_test(f"WeChat.{method_name} 便捷方法存在", False, "方法不可调用")
            else:
                self.log_test(f"WeChat.{method_name} 便捷方法存在", False, "方法不存在")
    
    def verify_method_functionality(self):
        """验收标准3: 新方法能够正确返回小程序消息列表"""
        print("\n=== 验收标准3: 新方法能够正确返回小程序消息列表 ===")
        
        try:
            # 创建模拟的聊天实例进行功能测试
            from unittest.mock import Mock
            
            # 创建模拟的小程序消息
            mock_miniprogram_msg = Mock()
            mock_miniprogram_msg.app_name = "测试小程序"
            mock_miniprogram_msg.app_description = "测试描述"
            mock_miniprogram_msg.sender = "测试发送者"
            mock_miniprogram_msg.type = "miniprogram"
            
            # 创建模拟的Chat实例
            mock_chat = Mock()
            mock_chat.GetAllMessage.return_value = [mock_miniprogram_msg]
            mock_chat.who = "测试聊天"
            
            # 测试MiniprogramExtractor功能
            extractor = MiniprogramExtractor(mock_chat)
            
            # 测试提取功能
            messages = extractor.extract_all_miniprogram_messages()
            if isinstance(messages, list):
                self.log_test("extract_all_miniprogram_messages 返回列表类型", True)
            else:
                self.log_test("extract_all_miniprogram_messages 返回列表类型", False, f"返回类型: {type(messages)}")
            
            # 测试过滤功能
            filtered = extractor.filter_by_app_name("测试")
            if isinstance(filtered, list):
                self.log_test("filter_by_app_name 返回列表类型", True)
            else:
                self.log_test("filter_by_app_name 返回列表类型", False, f"返回类型: {type(filtered)}")
            
            # 测试统计功能
            stats = extractor.get_statistics()
            if isinstance(stats, dict) and 'total_count' in stats:
                self.log_test("get_statistics 返回正确格式", True)
            else:
                self.log_test("get_statistics 返回正确格式", False, f"返回内容: {stats}")
            
            # 测试导出功能
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
                temp_file = f.name
            
            result = extractor.export_to_json(temp_file)
            if isinstance(result, WxResponse):
                self.log_test("export_to_json 返回WxResponse类型", True)
            else:
                self.log_test("export_to_json 返回WxResponse类型", False, f"返回类型: {type(result)}")
            
            # 清理临时文件
            try:
                os.unlink(temp_file)
            except:
                pass
                
        except Exception as e:
            self.log_test("方法功能测试", False, f"测试异常: {str(e)}")
    
    def verify_backward_compatibility(self):
        """验收标准4: 现有API功能不受影响，向后兼容性良好"""
        print("\n=== 验收标准4: 现有API功能不受影响，向后兼容性良好 ===")
        
        # 测试Chat类原有方法
        original_chat_methods = [
            'SendMsg', 'SendFiles', 'GetAllMessage', 'GetNewMessage',
            'GetGroupMembers', 'ChatInfo', 'LoadMoreMessage', 'Show', 'Close'
        ]
        
        for method_name in original_chat_methods:
            if hasattr(Chat, method_name) and callable(getattr(Chat, method_name)):
                self.log_test(f"Chat.{method_name} 原有方法保持兼容", True)
            else:
                self.log_test(f"Chat.{method_name} 原有方法保持兼容", False, "方法丢失或不可调用")
        
        # 测试WeChat类原有方法
        original_wechat_methods = [
            'ChatWith', 'AddListenChat', 'RemoveListenChat', 'GetSession',
            'GetNextNewMessage', 'SwitchToChat', 'SwitchToContact',
            'GetSubWindow', 'GetAllSubWindow', 'StopListening', 'StartListening'
        ]
        
        for method_name in original_wechat_methods:
            if hasattr(WeChat, method_name) and callable(getattr(WeChat, method_name)):
                self.log_test(f"WeChat.{method_name} 原有方法保持兼容", True)
            else:
                self.log_test(f"WeChat.{method_name} 原有方法保持兼容", False, "方法丢失或不可调用")
        
        # 测试继承关系
        if issubclass(WeChat, Chat):
            self.log_test("WeChat继承关系保持正确", True)
        else:
            self.log_test("WeChat继承关系保持正确", False, "继承关系被破坏")
        
        # 测试WeChat可以访问Chat的新方法
        chat_new_methods = ['GetMiniprogramMessages', 'FilterMiniprogramByApp', 'GetMiniprogramStatistics', 'ExportMiniprogramMessages']
        for method_name in chat_new_methods:
            if hasattr(WeChat, method_name):
                self.log_test(f"WeChat可访问Chat.{method_name}", True)
            else:
                self.log_test(f"WeChat可访问Chat.{method_name}", False, "无法访问继承的方法")
    
    def verify_integration_completeness(self):
        """验证集成完整性"""
        print("\n=== 验证集成完整性 ===")
        
        # 验证MiniprogramExtractor类集成
        try:
            from wxauto.utils.miniprogram_extractor import MiniprogramExtractor
            self.log_test("MiniprogramExtractor类可正常导入", True)
            
            # 验证关键方法存在
            key_methods = [
                'extract_all_miniprogram_messages',
                'filter_by_app_name',
                'filter_by_sender',
                'get_statistics',
                'export_to_json',
                'find_duplicate_apps',
                'get_recent_miniprogram_messages'
            ]
            
            for method_name in key_methods:
                if hasattr(MiniprogramExtractor, method_name):
                    self.log_test(f"MiniprogramExtractor.{method_name} 方法存在", True)
                else:
                    self.log_test(f"MiniprogramExtractor.{method_name} 方法存在", False)
                    
        except ImportError as e:
            self.log_test("MiniprogramExtractor类可正常导入", False, f"导入失败: {str(e)}")
        
        # 验证小程序消息类集成
        try:
            from wxauto.msgs.miniprogram import MiniprogramMessage, MiniprogramInfo
            from wxauto.msgs.friend import FriendMiniprogramMessage
            from wxauto.msgs.self import SelfMiniprogramMessage
            self.log_test("小程序消息类可正常导入", True)
        except ImportError as e:
            self.log_test("小程序消息类可正常导入", False, f"导入失败: {str(e)}")
    
    def run_verification(self):
        """运行完整验证"""
        print("任务12最终验证")
        print("=" * 60)
        print("验证任务12的所有验收标准...")
        print()
        
        # 运行各项验证
        self.verify_chat_class_methods()
        self.verify_wechat_class_methods()
        self.verify_method_functionality()
        self.verify_backward_compatibility()
        self.verify_integration_completeness()
        
        # 输出验证总结
        print("\n" + "=" * 60)
        print("验证总结:")
        print(f"总验证项: {self.total_tests}")
        print(f"通过验证: {self.passed_tests}")
        print(f"失败验证: {self.total_tests - self.passed_tests}")
        print(f"通过率: {(self.passed_tests / self.total_tests * 100):.1f}%")
        
        # 按验收标准分组显示结果
        print("\n验收标准达成情况:")
        
        # 统计各个验收标准的通过情况
        standards = {
            "标准1 - Chat类GetMiniprogramMessages方法": [
                "Chat.GetMiniprogramMessages 方法存在且可调用",
                "Chat.GetMiniprogramMessages 方法签名正确",
                "Chat.GetMiniprogramMessages 有返回类型注解",
                "Chat.GetMiniprogramMessages 有完整文档字符串"
            ],
            "标准2 - WeChat类便捷方法": [
                "WeChat.GetAllMiniprogramMessages 便捷方法存在",
                "WeChat.SearchMiniprogramByApp 便捷方法存在",
                "WeChat.GetMiniprogramSummary 便捷方法存在",
                "WeChat.ExportCurrentChatMiniprogram 便捷方法存在",
                "WeChat.GetRecentMiniprogramMessages 便捷方法存在",
                "WeChat.FindDuplicateMiniprogram 便捷方法存在",
                "WeChat.FilterMiniprogramBySender 便捷方法存在"
            ],
            "标准3 - 方法功能正确性": [
                "extract_all_miniprogram_messages 返回列表类型",
                "filter_by_app_name 返回列表类型",
                "get_statistics 返回正确格式",
                "export_to_json 返回WxResponse类型"
            ],
            "标准4 - 向后兼容性": [
                "WeChat继承关系保持正确",
                "Chat.SendMsg 原有方法保持兼容",
                "WeChat.ChatWith 原有方法保持兼容"
            ]
        }
        
        for standard, test_names in standards.items():
            passed_in_standard = sum(1 for name, passed, _ in self.test_results 
                                   if any(test_name in name for test_name in test_names) and passed)
            total_in_standard = sum(1 for name, _, _ in self.test_results 
                                  if any(test_name in name for test_name in test_names))
            
            if total_in_standard > 0:
                percentage = (passed_in_standard / total_in_standard) * 100
                status = "✅" if percentage == 100 else "⚠️" if percentage >= 80 else "❌"
                print(f"{status} {standard}: {passed_in_standard}/{total_in_standard} ({percentage:.1f}%)")
        
        if self.passed_tests == self.total_tests:
            print("\n🎉 任务12验证完全通过！所有验收标准均已达成！")
            print("\n✅ 集成功能到主要接口 - 任务完成")
            return True
        else:
            print(f"\n⚠️ 任务12验证未完全通过，有 {self.total_tests - self.passed_tests} 项验证失败。")
            return False


def main():
    """主函数"""
    print("任务12最终验证脚本")
    print("验证集成功能到主要接口的所有验收标准")
    print("-" * 60)
    
    try:
        verifier = Task12Verifier()
        success = verifier.run_verification()
        
        if success:
            print("\n✅ 任务12验证成功！集成功能已正确实现！")
            sys.exit(0)
        else:
            print("\n❌ 任务12验证失败，请检查实现。")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 验证过程中发生异常: {str(e)}")
        print(f"异常详情:\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()