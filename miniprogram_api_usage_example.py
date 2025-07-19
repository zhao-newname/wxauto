#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小程序API使用示例

展示如何使用新添加的小程序消息相关API方法
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wxauto import WeChat, Chat


def example_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 注意：这里只是示例代码，实际使用时需要有真实的微信窗口
    print("# 初始化微信实例")
    print("wx = WeChat()")
    print()
    
    print("# 打开聊天窗口")
    print("wx.ChatWith('好友名称')")
    print()
    
    print("# 获取当前聊天的所有小程序消息")
    print("miniprogram_messages = wx.GetMiniprogramMessages()")
    print("print(f'找到 {len(miniprogram_messages)} 条小程序消息')")
    print()
    
    print("# 遍历小程序消息")
    print("for msg in miniprogram_messages:")
    print("    print(f'应用名称: {msg.app_name}')")
    print("    print(f'应用描述: {msg.app_description}')")
    print("    print(f'发送者: {msg.sender}')")
    print("    print('---')")
    print()


def example_filtering():
    """过滤功能示例"""
    print("=== 过滤功能示例 ===")
    
    print("# 按应用名称过滤小程序消息")
    print("wechat_reading_msgs = wx.FilterMiniprogramByApp('微信读书')")
    print("print(f'找到 {len(wechat_reading_msgs)} 条微信读书消息')")
    print()
    
    print("# 精确匹配应用名称")
    print("exact_msgs = wx.FilterMiniprogramByApp('腾讯文档', exact_match=True)")
    print()
    
    print("# 按发送者过滤小程序消息")
    print("sender_msgs = wx.FilterMiniprogramBySender('张三')")
    print("print(f'张三发送了 {len(sender_msgs)} 条小程序消息')")
    print()
    
    print("# 获取最近7天的小程序消息")
    print("recent_msgs = wx.GetRecentMiniprogramMessages(days=7)")
    print("print(f'最近7天有 {len(recent_msgs)} 条小程序消息')")
    print()


def example_statistics():
    """统计功能示例"""
    print("=== 统计功能示例 ===")
    
    print("# 获取小程序消息统计信息")
    print("stats = wx.GetMiniprogramStatistics()")
    print("print(f'总计: {stats[\"total_count\"]} 条小程序消息')")
    print("print(f'好友消息: {stats[\"friend_messages\"]} 条')")
    print("print(f'自己消息: {stats[\"self_messages\"]} 条')")
    print("print(f'不同应用数量: {stats[\"unique_apps\"]} 个')")
    print()
    
    print("# 查看热门应用")
    print("print('热门小程序应用:')")
    print("for app_name, count in stats['top_apps'].items():")
    print("    print(f'  {app_name}: {count} 次')")
    print()
    
    print("# 查看热门发送者")
    print("print('热门发送者:')")
    print("for sender, count in stats['top_senders'].items():")
    print("    print(f'  {sender}: {count} 条消息')")
    print()


def example_duplicate_detection():
    """重复检测示例"""
    print("=== 重复检测示例 ===")
    
    print("# 查找重复的小程序应用")
    print("duplicates = wx.FindDuplicateMiniprogram()")
    print("print(f'发现 {len(duplicates)} 个重复的小程序应用')")
    print()
    
    print("for app_name, messages in duplicates.items():")
    print("    print(f'{app_name}: {len(messages)} 条消息')")
    print("    for msg in messages:")
    print("        print(f'  - 发送者: {msg.sender}, 时间: {msg.share_time}')")
    print()


def example_export():
    """导出功能示例"""
    print("=== 导出功能示例 ===")
    
    print("# 导出小程序消息为JSON文件")
    print("result = wx.ExportMiniprogramMessages('miniprogram_messages.json')")
    print("if result.success:")
    print("    print('导出成功!')")
    print("else:")
    print("    print(f'导出失败: {result.message}')")
    print()
    
    print("# 导出时不包含统计信息")
    print("result = wx.ExportMiniprogramMessages('messages_only.json', include_statistics=False)")
    print()


def example_interaction():
    """交互功能示例"""
    print("=== 交互功能示例 ===")
    
    print("# 获取小程序消息并进行交互")
    print("miniprogram_messages = wx.GetMiniprogramMessages()")
    print("if miniprogram_messages:")
    print("    msg = miniprogram_messages[0]  # 获取第一条小程序消息")
    print("    ")
    print("    # 打开小程序")
    print("    result = msg.open_miniprogram()")
    print("    if result.success:")
    print("        print('成功打开小程序')")
    print("    ")
    print("    # 复制小程序链接信息")
    print("    result = msg.copy_link_info()")
    print("    if result.success:")
    print("        print('成功复制链接信息到剪贴板')")
    print("    ")
    print("    # 转发小程序消息")
    print("    result = msg.Forward('目标好友')")
    print("    if result.success:")
    print("        print('成功转发小程序消息')")
    print()


def example_chat_vs_wechat():
    """Chat类与WeChat类方法对比示例"""
    print("=== Chat类与WeChat类方法对比 ===")
    
    print("# Chat类方法（适用于单个聊天窗口）")
    print("chat = Chat()  # 或者通过wx.ChatWith()获得")
    print("messages = chat.GetMiniprogramMessages()")
    print("filtered = chat.FilterMiniprogramByApp('微信读书')")
    print("stats = chat.GetMiniprogramStatistics()")
    print("chat.ExportMiniprogramMessages('chat_miniprogram.json')")
    print()
    
    print("# WeChat类方法（继承Chat类方法，并添加额外功能）")
    print("wx = WeChat()")
    print("# 基础方法（继承自Chat类）")
    print("messages = wx.GetMiniprogramMessages()")
    print("filtered = wx.FilterMiniprogramByApp('微信读书')")
    print()
    
    print("# WeChat类特有的便捷方法")
    print("all_messages = wx.GetAllMiniprogramMessages()  # 等同于GetMiniprogramMessages")
    print("search_results = wx.SearchMiniprogramByApp('腾讯文档')  # 等同于FilterMiniprogramByApp")
    print("summary = wx.GetMiniprogramSummary()  # 等同于GetMiniprogramStatistics")
    print("wx.ExportCurrentChatMiniprogram('export.json')  # 等同于ExportMiniprogramMessages")
    print()
    
    print("# WeChat类独有的高级功能")
    print("recent = wx.GetRecentMiniprogramMessages(days=30)")
    print("duplicates = wx.FindDuplicateMiniprogram()")
    print("by_sender = wx.FilterMiniprogramBySender('张三')")
    print()


def example_error_handling():
    """错误处理示例"""
    print("=== 错误处理示例 ===")
    
    print("# 所有方法都有适当的错误处理")
    print("try:")
    print("    messages = wx.GetMiniprogramMessages()")
    print("    if not messages:")
    print("        print('当前聊天中没有小程序消息')")
    print("    ")
    print("    stats = wx.GetMiniprogramStatistics()")
    print("    if 'error' in stats:")
    print("        print(f'获取统计信息时出错: {stats[\"error\"]}')")
    print("    ")
    print("    result = wx.ExportMiniprogramMessages('export.json')")
    print("    if not result.success:")
    print("        print(f'导出失败: {result.message}')")
    print("    ")
    print("except Exception as e:")
    print("    print(f'发生异常: {str(e)}')")
    print()


def example_performance_tips():
    """性能优化提示"""
    print("=== 性能优化提示 ===")
    
    print("# 使用缓存提高性能")
    print("# 第一次调用会提取并缓存消息")
    print("messages1 = wx.GetMiniprogramMessages(use_cache=True)")
    print("# 第二次调用会使用缓存（如果缓存仍然有效）")
    print("messages2 = wx.GetMiniprogramMessages(use_cache=True)")
    print()
    
    print("# 强制重新提取消息（不使用缓存）")
    print("fresh_messages = wx.GetMiniprogramMessages(use_cache=False)")
    print()
    
    print("# 批量操作比多次单独操作更高效")
    print("# 好的做法：")
    print("all_messages = wx.GetMiniprogramMessages()")
    print("wechat_reading = [msg for msg in all_messages if '微信读书' in msg.app_name]")
    print("tencent_docs = [msg for msg in all_messages if '腾讯文档' in msg.app_name]")
    print()
    
    print("# 避免的做法：")
    print("# wechat_reading = wx.FilterMiniprogramByApp('微信读书')  # 第一次提取")
    print("# tencent_docs = wx.FilterMiniprogramByApp('腾讯文档')   # 第二次提取")
    print()


def main():
    """主函数"""
    print("小程序API使用示例")
    print("=" * 60)
    print()
    
    examples = [
        example_basic_usage,
        example_filtering,
        example_statistics,
        example_duplicate_detection,
        example_export,
        example_interaction,
        example_chat_vs_wechat,
        example_error_handling,
        example_performance_tips
    ]
    
    for example in examples:
        example()
        print()
    
    print("=" * 60)
    print("注意：以上代码仅为示例，实际使用时需要：")
    print("1. 确保微信客户端已打开")
    print("2. 有相应的聊天窗口和小程序消息")
    print("3. 根据实际情况调整参数和错误处理")
    print()
    print("更多详细信息请参考wxauto文档和小程序消息类的源代码。")


if __name__ == "__main__":
    main()