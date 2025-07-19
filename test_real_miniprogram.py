#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
真实环境小程序测试脚本

这个脚本用于在真实微信环境中快速测试小程序URL提取功能。
适合用于验证功能是否正常工作。
"""

import sys
import os
import time
from typing import List, Dict, Optional

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from wxauto import WeChat
    from wxauto.msgs.miniprogram import MiniprogramMessage
    print("✅ 成功导入wxauto模块")
except ImportError as e:
    print(f"❌ 导入失败: {str(e)}")
    print("请确保wxauto已正确安装")
    sys.exit(1)


def test_connection():
    """测试微信连接"""
    print("🔗 测试微信连接...")
    
    try:
        wx = WeChat(debug=True)
        if wx and wx.nickname:
            print(f"✅ 连接成功！当前用户: {wx.nickname}")
            return wx
        else:
            print("❌ 连接失败")
            return None
    except Exception as e:
        print(f"❌ 连接异常: {str(e)}")
        return None


def test_miniprogram_detection(wx: WeChat):
    """测试小程序消息检测"""
    print("\n📱 测试小程序消息检测...")
    
    try:
        # 获取小程序消息
        miniprogram_messages = wx.GetMiniprogramMessages()
        
        print(f"✅ 找到 {len(miniprogram_messages)} 条小程序消息")
        
        if miniprogram_messages:
            print("\n📋 小程序消息列表:")
            for i, msg in enumerate(miniprogram_messages[:5]):  # 只显示前5条
                print(f"  {i+1}. {msg.app_name} (发送者: {msg.sender})")
                
        return miniprogram_messages
        
    except Exception as e:
        print(f"❌ 检测失败: {str(e)}")
        return []


def test_url_extraction(messages: List[MiniprogramMessage]):
    """测试URL提取功能"""
    print("\n🔗 测试URL提取功能...")
    
    if not messages:
        print("⚠️  没有小程序消息可供测试")
        return
    
    # 测试前3条消息
    test_messages = messages[:3]
    
    for i, msg in enumerate(test_messages):
        print(f"\n--- 测试消息 {i+1}: {msg.app_name} ---")
        
        try:
            # 测试基本信息提取
            print(f"  应用名称: {msg.app_name}")
            print(f"  应用描述: {msg.app_description}")
            print(f"  发送者: {msg.sender}")
            
            # 测试链接信息提取
            link_info = msg.extract_link_info()
            if link_info:
                print(f"  ✅ 链接信息提取成功")
                if 'app_id' in link_info and link_info['app_id']:
                    print(f"    AppID: {link_info['app_id']}")
                if 'page_path' in link_info and link_info['page_path']:
                    print(f"    页面路径: {link_info['page_path']}")
            else:
                print(f"  ⚠️  链接信息为空")
            
            # 测试复制链接功能
            print(f"  🔗 尝试复制链接信息...")
            copy_result = msg.copy_link_info()
            
            if copy_result.success:
                copied_content = copy_result.data.get('copied_content', '') if copy_result.data else ''
                if copied_content:
                    print(f"  ✅ 复制成功")
                    print(f"    复制内容预览: {copied_content[:100]}...")
                    
                    # 尝试从复制内容中提取URL
                    urls = extract_urls_from_text(copied_content)
                    if urls:
                        print(f"    🎯 提取到 {len(urls)} 个URL:")
                        for url in urls:
                            print(f"      - {url}")
                    else:
                        print(f"    ℹ️  未从复制内容中找到URL")
                else:
                    print(f"  ⚠️  复制成功但内容为空")
            else:
                print(f"  ❌ 复制失败: {copy_result.message}")
                
        except Exception as e:
            print(f"  ❌ 信息提取异常: {str(e)}")
    
    def extract_miniprogram_info(self, msg) -> Optional[dict]:
        """提取小程序信息"""
        info = {}
        try:
            info['app_name'] = msg.app_name
            info['app_description'] = msg.app_description
            info['sender'] = msg.sender
            
            # 提取链接信息
            link_info = msg.extract_link_info()
            if link_info:
                info.update(link_info)
            
            # 尝试复制链接
            copy_result = msg.copy_link_info()
            if copy_result.success and copy_result.data:
                copied_content = copy_result.data.get('copied_content', '')
                if copied_content:
                    info['copied_content'] = copied_content
                    
                    # 提取URL
                    urls = extract_urls_from_text(copied_content)
                    if urls:
                        info['urls'] = urls
            
            return info
            
        except Exception as e:
            print(f"提取信息异常: {str(e)}")
            return None


def extract_urls_from_text(text: str) -> List[str]:
    """从文本中提取URL"""
    import re
    
    url_patterns = [
        r'https?://[^\s<>"{}|\\^`\[\]]+',
        r'weixin://[^\s<>"{}|\\^`\[\]]+',
        r'wxauto://[^\s<>"{}|\\^`\[\]]+',
    ]
    
    urls = []
    for pattern in url_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        urls.extend(matches)
    
    return list(set(urls))


def test_statistics(wx: WeChat):
    """测试统计功能"""
    print("\n📊 测试统计功能...")
    
    try:
        stats = wx.GetMiniprogramStatistics()
        
        print(f"✅ 统计信息获取成功")
        print(f"  总小程序数量: {stats.get('total_count', 0)}")
        print(f"  好友消息: {stats.get('friend_messages', 0)}")
        print(f"  自己消息: {stats.get('self_messages', 0)}")
        print(f"  不同应用数: {stats.get('unique_apps', 0)}")
        
        top_apps = stats.get('top_apps', {})
        if top_apps:
            print(f"  热门应用:")
            for app, count in list(top_apps.items())[:3]:
                print(f"    - {app}: {count} 次")
                
    except Exception as e:
        print(f"❌ 统计功能测试失败: {str(e)}")


def test_filtering(wx: WeChat):
    """测试过滤功能"""
    print("\n🔍 测试过滤功能...")
    
    try:
        # 获取所有小程序消息
        all_messages = wx.GetMiniprogramMessages()
        if not all_messages:
            print("⚠️  没有小程序消息可供测试过滤功能")
            return
        
        # 获取第一个应用名称进行测试
        first_app = all_messages[0].app_name
        print(f"  测试过滤应用: {first_app}")
        
        # 测试按应用名称过滤
        filtered = wx.FilterMiniprogramByApp(first_app)
        print(f"  ✅ 按应用名称过滤: 找到 {len(filtered)} 条消息")
        
        # 测试按发送者过滤
        first_sender = all_messages[0].sender
        if first_sender:
            sender_filtered = wx.FilterMiniprogramBySender(first_sender)
            print(f"  ✅ 按发送者过滤: 找到 {len(sender_filtered)} 条消息")
        
    except Exception as e:
        print(f"❌ 过滤功能测试失败: {str(e)}")


def quick_test():
    """快速测试"""
    print("🚀 小程序URL提取功能快速测试")
    print("=" * 50)
    
    # 1. 测试连接
    wx = test_connection()
    if not wx:
        print("❌ 无法连接到微信，测试终止")
        return
    
    # 2. 测试小程序检测
    messages = test_miniprogram_detection(wx)
    
    # 3. 测试URL提取
    if messages:
        test_url_extraction(messages)
    
    # 4. 测试统计功能
    test_statistics(wx)
    
    # 5. 测试过滤功能
    test_filtering(wx)
    
    print("\n" + "=" * 50)
    print("🎉 快速测试完成！")
    
    if messages:
        print(f"✅ 在当前聊天中找到 {len(messages)} 条小程序消息")
        print("💡 提示: 使用 extract_miniprogram_urls.py 进行完整的URL提取")
    else:
        print("⚠️  当前聊天中没有小程序消息")
        print("💡 提示: 请切换到包含小程序消息的聊天后重试")


def interactive_test():
    """交互式测试"""
    print("🚀 小程序URL提取功能交互测试")
    print("=" * 50)
    
    # 连接微信
    wx = test_connection()
    if not wx:
        return
    
    while True:
        print(f"\n请选择测试项目:")
        print("1. 检测当前聊天的小程序消息")
        print("2. 提取小程序URL信息")
        print("3. 查看小程序统计")
        print("4. 测试过滤功能")
        print("5. 切换到其他聊天")
        print("6. 退出")
        
        try:
            choice = input("\n请输入选项 (1-6): ").strip()
            
            if choice == '1':
                test_miniprogram_detection(wx)
                
            elif choice == '2':
                messages = wx.GetMiniprogramMessages()
                if messages:
                    test_url_extraction(messages)
                else:
                    print("⚠️  当前聊天中没有小程序消息")
                    
            elif choice == '3':
                test_statistics(wx)
                
            elif choice == '4':
                test_filtering(wx)
                
            elif choice == '5':
                chat_name = input("请输入要切换的聊天名称: ").strip()
                if chat_name:
                    try:
                        wx.ChatWith(chat_name)
                        print(f"✅ 已切换到聊天: {chat_name}")
                        time.sleep(1)
                    except Exception as e:
                        print(f"❌ 切换失败: {str(e)}")
                        
            elif choice == '6':
                print("👋 测试结束")
                break
                
            else:
                print("❌ 无效选项")
                
        except KeyboardInterrupt:
            print("\n👋 用户中断，退出测试")
            break
        except Exception as e:
            print(f"❌ 操作失败: {str(e)}")


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_test()
    else:
        quick_test()


if __name__ == "__main__":
    main()