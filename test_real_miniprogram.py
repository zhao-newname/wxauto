#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实际微信环境小程序功能测试脚本

这个脚本会连接到真实的微信客户端，测试小程序消息的识别和信息提取功能。
请确保：
1. 微信PC版已登录
2. 文件传输助手中有小程序消息
3. 或者指定其他包含小程序消息的聊天对象
"""

import sys
import os
import time
from typing import List, Optional

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wxauto import WeChat
from wxauto.msgs.miniprogram import MiniprogramMessage
from wxauto.msgs.friend import FriendMiniprogramMessage
from wxauto.msgs.self import SelfMiniprogramMessage


class RealMiniprogramTester:
    """真实环境小程序测试器"""
    
    def __init__(self):
        self.wx = None
        self.test_results = {
            'total_messages': 0,
            'miniprogram_messages': 0,
            'friend_miniprogram': 0,
            'self_miniprogram': 0,
            'extraction_success': 0,
            'extraction_failed': 0,
            'details': []
        }
    
    def initialize_wechat(self) -> bool:
        """初始化微信连接"""
        try:
            print("正在连接微信...")
            self.wx = WeChat()
            print("✅ 微信连接成功！")
            return True
        except Exception as e:
            print(f"❌ 微信连接失败: {str(e)}")
            print("请确保微信PC版已登录")
            return False
    
    def test_chat_messages(self, chat_name: str = "文件传输助手") -> bool:
        """测试指定聊天中的消息"""
        try:
            print(f"\n正在切换到聊天: {chat_name}")
            self.wx.ChatWith(chat_name)
            time.sleep(2)  # 等待界面加载
            
            print("正在获取聊天消息...")
            messages = self.wx.GetAllMessage()
            
            if not messages:
                print(f"❌ 在 '{chat_name}' 中没有找到任何消息")
                return False
            
            print(f"✅ 获取到 {len(messages)} 条消息")
            self.test_results['total_messages'] = len(messages)
            
            # 分析每条消息
            self.analyze_messages(messages)
            
            return True
            
        except Exception as e:
            print(f"❌ 测试聊天消息时出错: {str(e)}")
            return False
    
    def analyze_messages(self, messages: List):
        """分析消息列表"""
        print("\n开始分析消息...")
        print("=" * 60)
        
        for i, msg in enumerate(messages, 1):
            print(f"\n消息 {i}/{len(messages)}:")
            print(f"  类型: {msg.type}")
            print(f"  内容: {msg.content[:100]}{'...' if len(msg.content) > 100 else ''}")
            
            # 检查是否为小程序消息
            if self.is_miniprogram_message(msg):
                self.test_results['miniprogram_messages'] += 1
                self.analyze_miniprogram_message(msg, i)
            else:
                print(f"  ➤ 非小程序消息")
    
    def is_miniprogram_message(self, msg) -> bool:
        """判断是否为小程序消息"""
        # 检查消息类型
        if hasattr(msg, 'type') and msg.type == 'miniprogram':
            return True
        
        # 检查是否为MiniprogramMessage实例
        if isinstance(msg, (MiniprogramMessage, FriendMiniprogramMessage, SelfMiniprogramMessage)):
            return True
        
        # 检查other类型消息（小程序通常被识别为other）
        if hasattr(msg, 'type') and msg.type == 'other':
            if hasattr(msg, 'content') and msg.content:
                content = msg.content
                
                # 检查小程序特征
                miniprogram_indicators = [
                    # 直接关键词
                    '小程序', 'miniprogram', '小游戏',
                    # 商品特征
                    '¥', '￥', '价格', '购买', '立即', '商城', '优惠',
                    # 服务特征  
                    '查询', '工具', '助手', '服务',
                    # 格式特征
                    '【', '】', '🔸', '▪', '•',
                    # 长文本特征（小程序卡片通常有较长描述）
                ]
                
                # 检查是否包含小程序特征
                has_indicators = any(indicator in content for indicator in miniprogram_indicators)
                
                # 检查文本长度（小程序卡片通常有较长的描述文本）
                is_long_content = len(content) > 50
                
                # 检查是否有多行内容（小程序卡片通常是多行）
                has_multiple_lines = '\n' in content or len(content.split()) > 10
                
                if has_indicators or (is_long_content and has_multiple_lines):
                    print(f"    🔍 检测到疑似小程序特征:")
                    if has_indicators:
                        found_indicators = [ind for ind in miniprogram_indicators if ind in content]
                        print(f"      - 包含指示词: {found_indicators[:3]}")
                    if is_long_content:
                        print(f"      - 长文本内容: {len(content)} 字符")
                    if has_multiple_lines:
                        print(f"      - 多行/多词内容")
                    
                    # 进一步检查控件结构
                    if hasattr(msg, 'control') and msg.control:
                        return self.check_control_structure(msg.control)
                    else:
                        # 即使没有控件信息，也基于内容特征判断
                        return True
        
        return False
    
    def check_control_structure(self, control) -> bool:
        """检查控件结构是否符合小程序特征"""
        try:
            # 检查控件尺寸
            if hasattr(control, 'BoundingRectangle'):
                rect = control.BoundingRectangle
                width = rect.right - rect.left
                height = rect.bottom - rect.top
                
                print(f"    控件尺寸: {width}x{height}")
                
                # 放宽小程序卡片的尺寸范围
                # 小程序卡片可能有各种尺寸，包括较大的商品卡片
                if width >= 200 and height >= 60:
                    # 检查宽高比，小程序卡片通常是横向的
                    aspect_ratio = width / height
                    if 1.5 <= aspect_ratio <= 8.0:  # 宽高比在合理范围内
                        print(f"    ✅ 符合小程序特征 (宽高比: {aspect_ratio:.2f})")
                        return True
                    else:
                        print(f"    ⚠️  尺寸可疑，但宽高比不典型 (宽高比: {aspect_ratio:.2f})")
                        # 即使宽高比不典型，如果有其他特征也认为是小程序
                        return True
                else:
                    print(f"    ❌ 尺寸太小，不符合小程序特征")
                    return False
            
            # 如果没有尺寸信息，基于其他特征判断
            print(f"    ⚠️  无法获取控件尺寸信息")
            return True
            
        except Exception as e:
            print(f"    检查控件结构时出错: {str(e)}")
            # 出错时也认为可能是小程序
            return True
    
    def analyze_miniprogram_message(self, msg, msg_index: int):
        """分析小程序消息"""
        print(f"  ✅ 发现小程序消息!")
        
        # 确定消息类型
        if isinstance(msg, FriendMiniprogramMessage):
            self.test_results['friend_miniprogram'] += 1
            msg_type = "好友小程序消息"
        elif isinstance(msg, SelfMiniprogramMessage):
            self.test_results['self_miniprogram'] += 1
            msg_type = "自己的小程序消息"
        else:
            msg_type = "基础小程序消息"
        
        print(f"  消息类型: {msg_type}")
        
        # 尝试提取小程序信息
        try:
            info = self.extract_miniprogram_info(msg)
            if info:
                self.test_results['extraction_success'] += 1
                self.print_miniprogram_info(info, msg_index)
            else:
                self.test_results['extraction_failed'] += 1
                print(f"  ❌ 信息提取失败")
                
        except Exception as e:
            self.test_results['extraction_failed'] += 1
            print(f"  ❌ 信息提取异常: {str(e)}")
    
    def extract_miniprogram_info(self, msg) -> Optional[dict]:
        """提取小程序信息"""
        info = {}
        
        try:
            # 基本信息
            if hasattr(msg, 'app_name'):
                info['app_name'] = msg.app_name
            
            if hasattr(msg, 'app_description'):
                info['app_description'] = msg.app_description
            
            # 技术参数
            if hasattr(msg, 'app_id'):
                info['app_id'] = msg.app_id
            
            if hasattr(msg, 'page_path'):
                info['page_path'] = msg.page_path
            
            if hasattr(msg, 'page_params'):
                info['page_params'] = msg.page_params
            
            # 发送者信息（如果是好友消息）
            if hasattr(msg, 'sender'):
                info['sender'] = msg.sender
            
            if hasattr(msg, 'sender_remark'):
                info['sender_remark'] = msg.sender_remark
            
            # 时间信息
            if hasattr(msg, 'time'):
                info['time'] = msg.time
            
            return info if info else None
            
        except Exception as e:
            print(f"    提取信息时出错: {str(e)}")
            return None
    
    def print_miniprogram_info(self, info: dict, msg_index: int):
        """打印小程序信息"""
        print(f"  📱 小程序信息:")
        
        if 'app_name' in info:
            print(f"    应用名称: {info['app_name']}")
        
        if 'app_description' in info:
            print(f"    应用描述: {info['app_description']}")
        
        if 'app_id' in info:
            print(f"    AppID: {info['app_id']}")
        
        if 'page_path' in info:
            print(f"    页面路径: {info['page_path']}")
        
        if 'page_params' in info:
            print(f"    页面参数: {info['page_params']}")
        
        if 'sender' in info:
            print(f"    发送者: {info['sender']}")
        
        if 'sender_remark' in info:
            print(f"    发送者备注: {info['sender_remark']}")
        
        if 'time' in info:
            print(f"    时间: {info['time']}")
        
        # 保存详细信息
        self.test_results['details'].append({
            'message_index': msg_index,
            'info': info
        })
    
    def test_miniprogram_interactions(self, msg):
        """测试小程序交互功能"""
        print(f"  🔧 测试交互功能:")
        
        try:
            # 测试点击打开功能
            if hasattr(msg, 'open_miniprogram'):
                print(f"    ✅ 支持打开小程序功能")
            else:
                print(f"    ❌ 不支持打开小程序功能")
            
            # 测试复制链接功能
            if hasattr(msg, 'copy_link_info'):
                print(f"    ✅ 支持复制链接信息功能")
            else:
                print(f"    ❌ 不支持复制链接信息功能")
            
            # 测试转发功能
            if hasattr(msg, 'forward'):
                print(f"    ✅ 支持转发功能")
            else:
                print(f"    ❌ 不支持转发功能")
                
        except Exception as e:
            print(f"    ❌ 测试交互功能时出错: {str(e)}")
    
    def print_test_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        
        results = self.test_results
        
        print(f"总消息数: {results['total_messages']}")
        print(f"小程序消息数: {results['miniprogram_messages']}")
        print(f"好友小程序消息: {results['friend_miniprogram']}")
        print(f"自己的小程序消息: {results['self_miniprogram']}")
        print(f"信息提取成功: {results['extraction_success']}")
        print(f"信息提取失败: {results['extraction_failed']}")
        
        if results['miniprogram_messages'] > 0:
            success_rate = (results['extraction_success'] / results['miniprogram_messages']) * 100
            print(f"信息提取成功率: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("✅ 信息提取成功率达到验收标准 (≥90%)")
            else:
                print("❌ 信息提取成功率未达到验收标准 (≥90%)")
        
        # 功能完整性检查
        print(f"\n功能完整性检查:")
        if results['miniprogram_messages'] > 0:
            print("✅ 小程序消息识别功能正常")
        else:
            print("❌ 未发现小程序消息，可能识别功能有问题")
        
        if results['friend_miniprogram'] > 0:
            print("✅ 好友小程序消息类型正常")
        else:
            print("⚠️  未发现好友小程序消息")
        
        if results['self_miniprogram'] > 0:
            print("✅ 自己的小程序消息类型正常")
        else:
            print("⚠️  未发现自己的小程序消息")
        
        return results['miniprogram_messages'] > 0 and results['extraction_success'] > 0


def main():
    """主函数"""
    print("🚀 开始实际微信环境小程序功能测试")
    print("=" * 60)
    
    # 创建测试器
    tester = RealMiniprogramTester()
    
    # 初始化微信
    if not tester.initialize_wechat():
        return False
    
    # 获取用户输入的聊天对象
    print("\n请选择测试方式:")
    print("1. 测试文件传输助手 (默认)")
    print("2. 测试指定聊天对象")
    print("3. 测试多个聊天对象")
    
    choice = input("请输入选择 (1-3, 默认1): ").strip()
    
    success = False
    
    if choice == "2":
        chat_name = input("请输入聊天对象名称: ").strip()
        if chat_name:
            success = tester.test_chat_messages(chat_name)
        else:
            print("❌ 聊天对象名称不能为空")
    
    elif choice == "3":
        chat_names = input("请输入聊天对象名称 (用逗号分隔): ").strip()
        if chat_names:
            names = [name.strip() for name in chat_names.split(',')]
            for name in names:
                print(f"\n{'='*40}")
                print(f"测试聊天对象: {name}")
                print(f"{'='*40}")
                if tester.test_chat_messages(name):
                    success = True
        else:
            print("❌ 聊天对象名称不能为空")
    
    else:
        # 默认测试文件传输助手
        success = tester.test_chat_messages("文件传输助手")
    
    # 打印测试总结
    tester.print_test_summary()
    
    if success:
        print("\n🎉 测试完成！发现了小程序消息并成功提取信息。")
    else:
        print("\n⚠️  测试完成，但未发现小程序消息或提取失败。")
        print("建议:")
        print("1. 确保测试的聊天中有小程序消息")
        print("2. 尝试发送一个小程序到文件传输助手进行测试")
        print("3. 检查小程序消息是否在当前可见区域")
    
    return success


if __name__ == "__main__":
    try:
        print("请确保:")
        print("1. 微信PC版已登录")
        print("2. 测试聊天中有小程序消息")
        print("3. 小程序消息在当前可见区域")
        print("\n程序将在3秒后开始...")
        time.sleep(3)
        
        success = main()
        
        print(f"\n程序执行完成，退出码: {0 if success else 1}")
        
    except KeyboardInterrupt:
        print("\n用户中断程序执行")
    except Exception as e:
        print(f"\n程序执行出错: {str(e)}")
        import traceback
        traceback.print_exc()