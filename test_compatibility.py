#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
向后兼容性测试脚本

确保新添加的小程序功能不会破坏现有的wxauto功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """测试基本导入功能"""
    print("测试基本导入...")
    
    try:
        # 测试主要类的导入
        from wxauto import WeChat, Chat, WxParam
        print("✅ 成功导入 WeChat, Chat, WxParam")
        
        # 测试消息类的导入
        from wxauto.msgs.base import Message
        from wxauto.msgs.type import TextMessage, ImageMessage, FileMessage
        print("✅ 成功导入消息类")
        
        # 测试参数类的导入
        from wxauto.param import WxResponse
        print("✅ 成功导入参数类")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {str(e)}")
        return False

def test_class_structure():
    """测试类结构完整性"""
    print("\n测试类结构...")
    
    try:
        from wxauto import WeChat, Chat
        
        # 测试继承关系
        if issubclass(WeChat, Chat):
            print("✅ WeChat 正确继承自 Chat")
        else:
            print("❌ WeChat 继承关系错误")
            return False
        
        # 测试原有方法是否存在
        chat_methods = [
            'SendMsg', 'SendFiles', 'GetAllMessage', 'GetNewMessage',
            'GetGroupMembers', 'ChatInfo', 'LoadMoreMessage', 'Show', 'Close'
        ]
        
        for method in chat_methods:
            if hasattr(Chat, method):
                print(f"✅ Chat.{method} 方法存在")
            else:
                print(f"❌ Chat.{method} 方法缺失")
                return False
        
        wechat_methods = [
            'ChatWith', 'AddListenChat', 'RemoveListenChat', 'GetSession',
            'GetNextNewMessage', 'SwitchToChat', 'SwitchToContact'
        ]
        
        for method in wechat_methods:
            if hasattr(WeChat, method):
                print(f"✅ WeChat.{method} 方法存在")
            else:
                print(f"❌ WeChat.{method} 方法缺失")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 类结构测试失败: {str(e)}")
        return False

def test_new_methods_added():
    """测试新方法是否正确添加"""
    print("\n测试新方法...")
    
    try:
        from wxauto import WeChat, Chat
        
        # 测试Chat类新方法
        chat_new_methods = [
            'GetMiniprogramMessages', 'FilterMiniprogramByApp',
            'GetMiniprogramStatistics', 'ExportMiniprogramMessages'
        ]
        
        for method in chat_new_methods:
            if hasattr(Chat, method):
                print(f"✅ Chat.{method} 新方法已添加")
            else:
                print(f"❌ Chat.{method} 新方法缺失")
                return False
        
        # 测试WeChat类新方法
        wechat_new_methods = [
            'GetAllMiniprogramMessages', 'SearchMiniprogramByApp',
            'GetMiniprogramSummary', 'ExportCurrentChatMiniprogram',
            'GetRecentMiniprogramMessages', 'FindDuplicateMiniprogram',
            'FilterMiniprogramBySender'
        ]
        
        for method in wechat_new_methods:
            if hasattr(WeChat, method):
                print(f"✅ WeChat.{method} 新方法已添加")
            else:
                print(f"❌ WeChat.{method} 新方法缺失")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 新方法测试失败: {str(e)}")
        return False

def test_parameter_compatibility():
    """测试参数兼容性"""
    print("\n测试参数兼容性...")
    
    try:
        from wxauto.param import WxParam, WxResponse, PROJECT_NAME
        
        # 测试WxParam的基本属性
        param_attrs = [
            'LANGUAGE', 'LISTEN_INTERVAL', 'ENABLE_FILE_LOGGER',
            'DEFAULT_SAVE_PATH'
        ]
        
        for attr in param_attrs:
            if hasattr(WxParam, attr):
                print(f"✅ WxParam.{attr} 属性存在")
            else:
                print(f"❌ WxParam.{attr} 属性缺失")
                return False
        
        # 测试PROJECT_NAME模块变量
        if PROJECT_NAME:
            print("✅ PROJECT_NAME 模块变量存在")
        else:
            print("❌ PROJECT_NAME 模块变量缺失")
            return False
        
        # 测试WxResponse的基本方法
        if hasattr(WxResponse, 'success') and hasattr(WxResponse, 'failure'):
            print("✅ WxResponse.success 和 WxResponse.failure 方法存在")
        else:
            print("❌ WxResponse 方法缺失")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 参数兼容性测试失败: {str(e)}")
        return False

def test_message_system_compatibility():
    """测试消息系统兼容性"""
    print("\n测试消息系统兼容性...")
    
    try:
        # 测试消息类型导入
        from wxauto.msgs.type import (
            TextMessage, ImageMessage, FileMessage, VideoMessage,
            VoiceMessage, QuoteMessage, OtherMessage
        )
        print("✅ 基本消息类型导入成功")
        
        # 测试好友和自己消息类型导入
        from wxauto.msgs.friend import (
            FriendTextMessage, FriendImageMessage, FriendFileMessage
        )
        from wxauto.msgs.self import (
            SelfTextMessage, SelfImageMessage, SelfFileMessage
        )
        print("✅ 好友和自己消息类型导入成功")
        
        # 测试新的小程序消息类型
        from wxauto.msgs.friend import FriendMiniprogramMessage
        from wxauto.msgs.self import SelfMiniprogramMessage
        from wxauto.msgs.miniprogram import MiniprogramMessage
        print("✅ 小程序消息类型导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 消息系统兼容性测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("wxauto 向后兼容性测试")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
        test_class_structure,
        test_new_methods_added,
        test_parameter_compatibility,
        test_message_system_compatibility
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"\n❌ 测试失败: {test.__name__}")
    
    print("\n" + "=" * 50)
    print(f"兼容性测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有兼容性测试通过！新功能集成成功！")
        return True
    else:
        print("⚠️ 部分兼容性测试失败，请检查实现。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)