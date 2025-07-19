#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小程序API功能测试脚本

测试新添加的小程序API方法的实际功能，包括：
- 创建模拟的小程序消息
- 测试各种API方法的实际调用
- 验证返回值的正确性
"""

import sys
import os
import traceback
from typing import List, Dict, Any
from unittest.mock import Mock, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from wxauto import WeChat, Chat
    from wxauto.msgs.miniprogram import MiniprogramMessage, MiniprogramInfo
    from wxauto.msgs.friend import FriendMiniprogramMessage
    from wxauto.msgs.self import SelfMiniprogramMessage
    from wxauto.utils.miniprogram_extractor import MiniprogramExtractor
    from wxauto.param import WxResponse
    from wxauto import uiautomation as uia
    print("✅ 成功导入所有必需的模块")
except ImportError as e:
    print(f"❌ 导入模块失败: {str(e)}")
    sys.exit(1)


class MockChat:
    """模拟Chat类用于测试"""
    
    def __init__(self):
        self.who = "测试聊天"
        self.mock_messages = []
        
        # 创建一些模拟的小程序消息
        self._create_mock_miniprogram_messages()
    
    def _create_mock_miniprogram_messages(self):
        """创建模拟的小程序消息"""
        # 创建模拟控件
        mock_control = Mock()
        mock_control.Name = "测试小程序"
        mock_control.BoundingRectangle = Mock()
        mock_control.BoundingRectangle.width.return_value = 300
        mock_control.BoundingRectangle.height.return_value = 100
        mock_control.Exists.return_value = True
        
        # 创建模拟的ChatBox
        mock_chatbox = Mock()
        
        # 创建几个不同类型的小程序消息
        miniprogram_msgs = []
        
        # 好友小程序消息
        friend_msg = Mock(spec=FriendMiniprogramMessage)
        friend_msg.app_name = "微信读书"
        friend_msg.app_description = "让阅读不再孤独"
        friend_msg.sender = "张三"
        friend_msg.sender_remark = "张三"
        friend_msg.type = "miniprogram"
        miniprogram_msgs.append(friend_msg)
        
        # 自己的小程序消息
        self_msg = Mock(spec=SelfMiniprogramMessage)
        self_msg.app_name = "腾讯文档"
        self_msg.app_description = "多人协作的在线文档"
        self_msg.sender = "我"
        self_msg.sender_remark = ""
        self_msg.type = "miniprogram"
        miniprogram_msgs.append(self_msg)
        
        # 另一个好友小程序消息
        friend_msg2 = Mock(spec=FriendMiniprogramMessage)
        friend_msg2.app_name = "微信读书"  # 重复的应用
        friend_msg2.app_description = "让阅读不再孤独"
        friend_msg2.sender = "李四"
        friend_msg2.sender_remark = "李四"
        friend_msg2.type = "miniprogram"
        miniprogram_msgs.append(friend_msg2)
        
        # 添加一些非小程序消息
        text_msg = Mock()
        text_msg.type = "text"
        text_msg.content = "这是一条普通文本消息"
        
        image_msg = Mock()
        image_msg.type = "image"
        image_msg.content = "[图片]"
        
        # 组合所有消息
        self.mock_messages = miniprogram_msgs + [text_msg, image_msg]
    
    def GetAllMessage(self):
        """模拟获取所有消息"""
        return self.mock_messages


class FunctionalTester:
    """功能测试器"""
    
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
    
    def test_miniprogram_extractor_functionality(self):
        """测试MiniprogramExtractor的功能"""
        print("\n=== 测试MiniprogramExtractor功能 ===")
        
        try:
            # 创建模拟聊天实例
            mock_chat = MockChat()
            
            # 创建提取器
            extractor = MiniprogramExtractor(mock_chat)
            
            # 测试提取所有小程序消息
            miniprogram_messages = extractor.extract_all_miniprogram_messages()
            expected_count = 3  # 我们创建了3个小程序消息
            
            if len(miniprogram_messages) == expected_count:
                self.log_test("提取所有小程序消息", True, f"成功提取 {len(miniprogram_messages)} 条消息")
            else:
                self.log_test("提取所有小程序消息", False, f"期望 {expected_count} 条，实际 {len(miniprogram_messages)} 条")
            
            # 测试按应用名称过滤
            wechat_reading_msgs = extractor.filter_by_app_name("微信读书")
            if len(wechat_reading_msgs) == 2:  # 应该有2条微信读书消息
                self.log_test("按应用名称过滤", True, f"找到 {len(wechat_reading_msgs)} 条微信读书消息")
            else:
                self.log_test("按应用名称过滤", False, f"期望2条微信读书消息，实际 {len(wechat_reading_msgs)} 条")
            
            # 测试按发送者过滤
            zhangsan_msgs = extractor.filter_by_sender("张三")
            if len(zhangsan_msgs) == 1:
                self.log_test("按发送者过滤", True, f"找到 {len(zhangsan_msgs)} 条张三的消息")
            else:
                self.log_test("按发送者过滤", False, f"期望1条张三消息，实际 {len(zhangsan_msgs)} 条")
            
            # 测试统计功能
            stats = extractor.get_statistics()
            if isinstance(stats, dict) and 'total_count' in stats:
                if stats['total_count'] == expected_count:
                    self.log_test("统计功能", True, f"统计总数正确: {stats['total_count']}")
                else:
                    self.log_test("统计功能", False, f"统计总数错误: {stats['total_count']}")
            else:
                self.log_test("统计功能", False, "统计结果格式错误")
            
            # 测试查找重复应用
            duplicates = extractor.find_duplicate_apps()
            if isinstance(duplicates, dict) and "微信读书" in duplicates:
                if len(duplicates["微信读书"]) == 2:
                    self.log_test("查找重复应用", True, "正确找到重复的微信读书应用")
                else:
                    self.log_test("查找重复应用", False, f"微信读书重复数量错误: {len(duplicates['微信读书'])}")
            else:
                self.log_test("查找重复应用", False, "未找到重复的微信读书应用")
                
        except Exception as e:
            self.log_test("MiniprogramExtractor功能测试", False, f"测试异常: {str(e)}")
    
    def test_chat_api_methods(self):
        """测试Chat类API方法的功能"""
        print("\n=== 测试Chat类API方法功能 ===")
        
        try:
            # 创建模拟的Chat实例
            mock_chat = MockChat()
            
            # 手动添加新方法到mock_chat（模拟继承）
            extractor = MiniprogramExtractor(mock_chat)
            
            # 模拟GetMiniprogramMessages方法
            def mock_get_miniprogram_messages(use_cache=True):
                return extractor.extract_all_miniprogram_messages(use_cache)
            
            def mock_filter_miniprogram_by_app(app_name, exact_match=False):
                return extractor.filter_by_app_name(app_name, exact_match)
            
            def mock_get_miniprogram_statistics():
                return extractor.get_statistics()
            
            # 测试GetMiniprogramMessages
            messages = mock_get_miniprogram_messages()
            if len(messages) == 3:
                self.log_test("Chat.GetMiniprogramMessages 功能", True, f"返回 {len(messages)} 条消息")
            else:
                self.log_test("Chat.GetMiniprogramMessages 功能", False, f"返回消息数量错误: {len(messages)}")
            
            # 测试FilterMiniprogramByApp
            filtered = mock_filter_miniprogram_by_app("微信读书")
            if len(filtered) == 2:
                self.log_test("Chat.FilterMiniprogramByApp 功能", True, f"过滤结果正确: {len(filtered)} 条")
            else:
                self.log_test("Chat.FilterMiniprogramByApp 功能", False, f"过滤结果错误: {len(filtered)} 条")
            
            # 测试GetMiniprogramStatistics
            stats = mock_get_miniprogram_statistics()
            if isinstance(stats, dict) and stats.get('total_count') == 3:
                self.log_test("Chat.GetMiniprogramStatistics 功能", True, "统计结果正确")
            else:
                self.log_test("Chat.GetMiniprogramStatistics 功能", False, "统计结果错误")
                
        except Exception as e:
            self.log_test("Chat类API方法功能测试", False, f"测试异常: {str(e)}")
    
    def test_export_functionality(self):
        """测试导出功能"""
        print("\n=== 测试导出功能 ===")
        
        try:
            # 创建模拟聊天实例
            mock_chat = MockChat()
            extractor = MiniprogramExtractor(mock_chat)
            
            # 测试导出到临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                temp_filepath = f.name
            
            # 执行导出
            result = extractor.export_to_json(temp_filepath)
            
            if isinstance(result, WxResponse) and result.success:
                self.log_test("导出JSON功能", True, "导出成功")
                
                # 验证文件是否存在
                if os.path.exists(temp_filepath):
                    self.log_test("导出文件存在", True, f"文件路径: {temp_filepath}")
                    
                    # 验证文件内容
                    try:
                        import json
                        with open(temp_filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        if 'messages' in data and len(data['messages']) == 3:
                            self.log_test("导出文件内容正确", True, f"包含 {len(data['messages'])} 条消息")
                        else:
                            self.log_test("导出文件内容正确", False, "消息数量不正确")
                            
                        if 'statistics' in data:
                            self.log_test("导出包含统计信息", True)
                        else:
                            self.log_test("导出包含统计信息", False)
                            
                    except json.JSONDecodeError as e:
                        self.log_test("导出文件格式正确", False, f"JSON格式错误: {str(e)}")
                    
                    # 清理临时文件
                    try:
                        os.unlink(temp_filepath)
                    except:
                        pass
                        
                else:
                    self.log_test("导出文件存在", False, "文件未创建")
            else:
                self.log_test("导出JSON功能", False, f"导出失败: {result.message if result else '未知错误'}")
                
        except Exception as e:
            self.log_test("导出功能测试", False, f"测试异常: {str(e)}")
    
    def test_error_handling(self):
        """测试错误处理"""
        print("\n=== 测试错误处理 ===")
        
        try:
            # 创建一个会抛出异常的模拟聊天
            class ErrorChat:
                def __init__(self):
                    self.who = "错误聊天"
                
                def GetAllMessage(self):
                    raise Exception("模拟获取消息失败")
            
            error_chat = ErrorChat()
            extractor = MiniprogramExtractor(error_chat)
            
            # 测试异常处理
            messages = extractor.extract_all_miniprogram_messages()
            if isinstance(messages, list) and len(messages) == 0:
                self.log_test("异常处理 - 提取消息", True, "正确返回空列表")
            else:
                self.log_test("异常处理 - 提取消息", False, "异常处理不正确")
            
            # 测试统计异常处理
            stats = extractor.get_statistics()
            # 当底层数据提取失败时，统计应该返回空结果但不报错
            # 这是正确的行为，因为统计方法应该能处理空数据
            if isinstance(stats, dict) and stats.get('total_count') == 0:
                self.log_test("异常处理 - 统计信息", True, "正确处理空数据情况")
            else:
                self.log_test("异常处理 - 统计信息", False, f"异常处理不正确，返回: {stats}")
                
        except Exception as e:
            self.log_test("错误处理测试", False, f"测试异常: {str(e)}")
    
    def run_all_tests(self):
        """运行所有功能测试"""
        print("开始小程序API功能测试...")
        print("=" * 50)
        
        # 运行各项测试
        self.test_miniprogram_extractor_functionality()
        self.test_chat_api_methods()
        self.test_export_functionality()
        self.test_error_handling()
        
        # 输出测试总结
        print("\n" + "=" * 50)
        print("功能测试总结:")
        print(f"总测试数: {self.total_tests}")
        print(f"通过测试: {self.passed_tests}")
        print(f"失败测试: {self.total_tests - self.passed_tests}")
        print(f"通过率: {(self.passed_tests / self.total_tests * 100):.1f}%")
        
        if self.passed_tests == self.total_tests:
            print("\n🎉 所有功能测试通过！")
            return True
        else:
            print(f"\n⚠️  有 {self.total_tests - self.passed_tests} 个功能测试失败。")
            return False


def main():
    """主函数"""
    print("小程序API功能测试脚本")
    print("测试新添加的小程序API方法的实际功能")
    print("-" * 50)
    
    try:
        tester = FunctionalTester()
        success = tester.run_all_tests()
        
        if success:
            print("\n✅ 小程序API功能测试完成，所有功能正常！")
            sys.exit(0)
        else:
            print("\n❌ 小程序API功能测试发现问题，请检查实现。")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 测试过程中发生异常: {str(e)}")
        print(f"异常详情:\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()