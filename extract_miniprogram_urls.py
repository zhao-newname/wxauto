#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小程序URL提取器 - 真实环境测试

这个脚本用于在真实微信环境中提取小程序的URL和相关信息。
主要功能：
1. 连接到真实的微信客户端
2. 扫描聊天记录中的小程序消息
3. 提取小程序的URL、AppID、页面路径等信息
4. 支持批量提取和导出
"""

import sys
import os
import time
import json
from datetime import datetime
from typing import List, Dict, Optional

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from wxauto import WeChat, Chat
    from wxauto.msgs.miniprogram import MiniprogramMessage
    from wxauto.param import WxResponse
    from wxauto.logger import wxlog
    print("✅ 成功导入wxauto模块")
except ImportError as e:
    print(f"❌ 导入wxauto模块失败: {str(e)}")
    print("请确保wxauto已正确安装")
    sys.exit(1)


class MiniprogramURLExtractor:
    """小程序URL提取器"""
    
    def __init__(self, debug: bool = False):
        """初始化提取器
        
        Args:
            debug: 是否启用调试模式
        """
        self.debug = debug
        self.wx = None
        self.extracted_urls = []
        
    def connect_to_wechat(self) -> bool:
        """连接到微信客户端
        
        Returns:
            bool: 连接是否成功
        """
        try:
            print("正在连接到微信客户端...")
            self.wx = WeChat(debug=self.debug)
            
            if self.wx and self.wx.nickname:
                print(f"✅ 成功连接到微信，当前用户: {self.wx.nickname}")
                return True
            else:
                print("❌ 连接微信失败，请确保微信客户端已打开")
                return False
                
        except Exception as e:
            print(f"❌ 连接微信异常: {str(e)}")
            print("请确保：")
            print("1. 微信客户端已打开并登录")
            print("2. 微信版本支持UI自动化")
            print("3. 没有其他程序占用微信窗口")
            return False
    
    def list_recent_chats(self, limit: int = 10) -> List[str]:
        """列出最近的聊天对话
        
        Args:
            limit: 显示的聊天数量限制
            
        Returns:
            List[str]: 聊天名称列表
        """
        try:
            print(f"\n📋 获取最近 {limit} 个聊天对话...")
            sessions = self.wx.GetSession()
            
            chat_names = []
            for i, session in enumerate(sessions[:limit]):
                chat_name = session.nickname
                chat_names.append(chat_name)
                print(f"{i+1:2d}. {chat_name}")
            
            return chat_names
            
        except Exception as e:
            print(f"❌ 获取聊天列表失败: {str(e)}")
            return []
    
    def extract_from_chat(self, chat_name: str) -> List[Dict]:
        """从指定聊天中提取小程序URL
        
        Args:
            chat_name: 聊天名称
            
        Returns:
            List[Dict]: 提取的小程序信息列表
        """
        try:
            print(f"\n🔍 正在分析聊天: {chat_name}")
            
            # 切换到指定聊天
            self.wx.ChatWith(chat_name)
            time.sleep(1)  # 等待聊天窗口加载
            
            # 获取小程序消息
            print("  📱 搜索小程序消息...")
            miniprogram_messages = self.wx.GetMiniprogramMessages()
            
            if not miniprogram_messages:
                print("  ℹ️  该聊天中没有找到小程序消息")
                return []
            
            print(f"  ✅ 找到 {len(miniprogram_messages)} 条小程序消息")
            
            # 提取每个小程序的详细信息
            extracted_info = []
            for i, msg in enumerate(miniprogram_messages):
                try:
                    print(f"  📋 提取第 {i+1}/{len(miniprogram_messages)} 条小程序信息...")
                    
                    # 基本信息
                    info = {
                        'chat_name': chat_name,
                        'app_name': msg.app_name,
                        'app_description': msg.app_description,
                        'sender': msg.sender,
                        'sender_remark': getattr(msg, 'sender_remark', ''),
                        'message_type': type(msg).__name__,
                        'extraction_time': datetime.now().isoformat()
                    }
                    
                    # 尝试提取完整链接信息
                    try:
                        link_info = msg.extract_link_info()
                        if link_info:
                            info.update(link_info)
                            print(f"    ✅ {msg.app_name} - 基本信息已提取")
                        else:
                            print(f"    ⚠️  {msg.app_name} - 无法提取链接信息")
                    except Exception as e:
                        print(f"    ❌ {msg.app_name} - 提取链接信息失败: {str(e)}")
                    
                    # 尝试复制链接信息（这可能包含URL）
                    try:
                        print(f"    🔗 尝试复制 {msg.app_name} 的链接信息...")
                        copy_result = msg.copy_link_info()
                        
                        if copy_result.success:
                            copied_content = copy_result.data.get('copied_content', '') if copy_result.data else ''
                            if copied_content:
                                info['copied_link_info'] = copied_content
                                
                                # 尝试从复制的内容中提取URL
                                urls = self._extract_urls_from_text(copied_content)
                                if urls:
                                    info['extracted_urls'] = urls
                                    print(f"    ✅ 成功提取到 {len(urls)} 个URL")
                                else:
                                    print(f"    ℹ️  复制成功但未找到URL")
                            else:
                                print(f"    ⚠️  复制成功但内容为空")
                        else:
                            print(f"    ❌ 复制链接信息失败: {copy_result.message}")
                            
                    except Exception as e:
                        print(f"    ❌ 复制链接信息异常: {str(e)}")
                    
                    extracted_info.append(info)
                    
                    # 添加延迟避免操作过快
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"  ❌ 处理第 {i+1} 条消息失败: {str(e)}")
                    continue
            
            print(f"  🎉 成功提取 {len(extracted_info)} 条小程序信息")
            return extracted_info
            
        except Exception as e:
            print(f"❌ 从聊天 {chat_name} 提取信息失败: {str(e)}")
            return []
    
    def _extract_urls_from_text(self, text: str) -> List[str]:
        """从文本中提取URL
        
        Args:
            text: 待分析的文本
            
        Returns:
            List[str]: 提取到的URL列表
        """
        import re
        
        # URL正则表达式模式
        url_patterns = [
            r'https?://[^\s<>"{}|\\^`\[\]]+',  # 标准HTTP/HTTPS URL
            r'weixin://[^\s<>"{}|\\^`\[\]]+',  # 微信协议URL
            r'wxauto://[^\s<>"{}|\\^`\[\]]+',  # 小程序协议URL
        ]
        
        urls = []
        for pattern in url_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            urls.extend(matches)
        
        # 去重并返回
        return list(set(urls))
    
    def extract_from_multiple_chats(self, chat_names: List[str]) -> List[Dict]:
        """从多个聊天中批量提取小程序URL
        
        Args:
            chat_names: 聊天名称列表
            
        Returns:
            List[Dict]: 所有提取的小程序信息
        """
        all_extracted = []
        
        for i, chat_name in enumerate(chat_names):
            print(f"\n{'='*60}")
            print(f"处理聊天 {i+1}/{len(chat_names)}: {chat_name}")
            print(f"{'='*60}")
            
            try:
                extracted = self.extract_from_chat(chat_name)
                all_extracted.extend(extracted)
                
                # 添加延迟避免切换过快
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ 处理聊天 {chat_name} 失败: {str(e)}")
                continue
        
        return all_extracted
    
    def save_results(self, results: List[Dict], filename: str = None) -> str:
        """保存提取结果到文件
        
        Args:
            results: 提取结果列表
            filename: 保存文件名，默认自动生成
            
        Returns:
            str: 保存的文件路径
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"miniprogram_urls_{timestamp}.json"
        
        try:
            # 准备保存数据
            save_data = {
                'extraction_info': {
                    'extraction_time': datetime.now().isoformat(),
                    'total_miniprogram_count': len(results),
                    'total_url_count': sum(len(item.get('extracted_urls', [])) for item in results),
                    'extractor_version': '1.0'
                },
                'miniprogram_data': results
            }
            
            # 保存到文件
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 结果已保存到: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ 保存结果失败: {str(e)}")
            return ""
    
    def print_summary(self, results: List[Dict]):
        """打印提取结果摘要
        
        Args:
            results: 提取结果列表
        """
        if not results:
            print("\n📊 提取摘要: 没有找到任何小程序信息")
            return
        
        print(f"\n📊 提取摘要:")
        print(f"{'='*50}")
        
        # 基本统计
        total_miniprogram = len(results)
        total_urls = sum(len(item.get('extracted_urls', [])) for item in results)
        
        print(f"总小程序数量: {total_miniprogram}")
        print(f"总URL数量: {total_urls}")
        
        # 按聊天分组统计
        chat_stats = {}
        for item in results:
            chat_name = item.get('chat_name', 'Unknown')
            if chat_name not in chat_stats:
                chat_stats[chat_name] = {'count': 0, 'urls': 0}
            chat_stats[chat_name]['count'] += 1
            chat_stats[chat_name]['urls'] += len(item.get('extracted_urls', []))
        
        print(f"\n按聊天分组:")
        for chat_name, stats in chat_stats.items():
            print(f"  {chat_name}: {stats['count']} 个小程序, {stats['urls']} 个URL")
        
        # 热门小程序
        app_names = [item.get('app_name', 'Unknown') for item in results]
        from collections import Counter
        app_counter = Counter(app_names)
        
        print(f"\n热门小程序 (Top 5):")
        for app_name, count in app_counter.most_common(5):
            print(f"  {app_name}: {count} 次")
        
        # 显示一些提取到的URL示例
        sample_urls = []
        for item in results:
            urls = item.get('extracted_urls', [])
            sample_urls.extend(urls)
            if len(sample_urls) >= 5:
                break
        
        if sample_urls:
            print(f"\nURL示例:")
            for i, url in enumerate(sample_urls[:5]):
                print(f"  {i+1}. {url}")
        
        print(f"{'='*50}")


def interactive_mode():
    """交互模式"""
    print("🚀 小程序URL提取器 - 交互模式")
    print("=" * 60)
    
    # 初始化提取器
    extractor = MiniprogramURLExtractor(debug=True)
    
    # 连接微信
    if not extractor.connect_to_wechat():
        return
    
    while True:
        print(f"\n📋 请选择操作:")
        print("1. 查看最近聊天列表")
        print("2. 从单个聊天提取小程序URL")
        print("3. 从多个聊天批量提取")
        print("4. 查看当前聊天的小程序统计")
        print("5. 退出")
        
        try:
            choice = input("\n请输入选项 (1-5): ").strip()
            
            if choice == '1':
                # 查看聊天列表
                limit = input("显示多少个最近聊天? (默认10): ").strip()
                limit = int(limit) if limit.isdigit() else 10
                extractor.list_recent_chats(limit)
                
            elif choice == '2':
                # 单个聊天提取
                chat_name = input("请输入聊天名称: ").strip()
                if chat_name:
                    results = extractor.extract_from_chat(chat_name)
                    if results:
                        extractor.print_summary(results)
                        
                        save = input("\n是否保存结果? (y/n): ").strip().lower()
                        if save == 'y':
                            filename = extractor.save_results(results)
                            if filename:
                                print(f"结果已保存到: {filename}")
                
            elif choice == '3':
                # 批量提取
                print("请输入要提取的聊天名称，每行一个，输入空行结束:")
                chat_names = []
                while True:
                    name = input().strip()
                    if not name:
                        break
                    chat_names.append(name)
                
                if chat_names:
                    print(f"\n将从 {len(chat_names)} 个聊天中提取小程序URL...")
                    confirm = input("确认开始? (y/n): ").strip().lower()
                    
                    if confirm == 'y':
                        results = extractor.extract_from_multiple_chats(chat_names)
                        if results:
                            extractor.print_summary(results)
                            filename = extractor.save_results(results)
                            if filename:
                                print(f"所有结果已保存到: {filename}")
                
            elif choice == '4':
                # 当前聊天统计
                try:
                    stats = extractor.wx.GetMiniprogramStatistics()
                    print(f"\n📊 当前聊天小程序统计:")
                    print(f"总数量: {stats.get('total_count', 0)}")
                    print(f"好友消息: {stats.get('friend_messages', 0)}")
                    print(f"自己消息: {stats.get('self_messages', 0)}")
                    
                    top_apps = stats.get('top_apps', {})
                    if top_apps:
                        print(f"\n热门应用:")
                        for app, count in list(top_apps.items())[:5]:
                            print(f"  {app}: {count} 次")
                            
                except Exception as e:
                    print(f"❌ 获取统计信息失败: {str(e)}")
                
            elif choice == '5':
                print("👋 感谢使用小程序URL提取器！")
                break
                
            else:
                print("❌ 无效选项，请重新选择")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，退出程序")
            break
        except Exception as e:
            print(f"❌ 操作失败: {str(e)}")


def batch_mode(chat_names: List[str], output_file: str = None):
    """批处理模式
    
    Args:
        chat_names: 要处理的聊天名称列表
        output_file: 输出文件路径
    """
    print("🚀 小程序URL提取器 - 批处理模式")
    print("=" * 60)
    
    # 初始化提取器
    extractor = MiniprogramURLExtractor(debug=False)
    
    # 连接微信
    if not extractor.connect_to_wechat():
        return
    
    # 批量提取
    print(f"将从 {len(chat_names)} 个聊天中提取小程序URL...")
    results = extractor.extract_from_multiple_chats(chat_names)
    
    if results:
        # 显示摘要
        extractor.print_summary(results)
        
        # 保存结果
        filename = extractor.save_results(results, output_file)
        if filename:
            print(f"\n🎉 批处理完成！结果已保存到: {filename}")
    else:
        print("\n⚠️  没有提取到任何小程序信息")


def main():
    """主函数"""
    print("🚀 小程序URL提取器")
    print("用于从微信聊天记录中提取小程序URL和相关信息")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # 命令行模式
        if sys.argv[1] == '--batch':
            if len(sys.argv) < 3:
                print("❌ 批处理模式需要指定聊天名称")
                print("用法: python extract_miniprogram_urls.py --batch 聊天名称1 聊天名称2 ...")
                return
            
            chat_names = sys.argv[2:]
            output_file = None
            
            # 检查是否指定了输出文件
            if '--output' in chat_names:
                output_index = chat_names.index('--output')
                if output_index + 1 < len(chat_names):
                    output_file = chat_names[output_index + 1]
                    chat_names = chat_names[:output_index] + chat_names[output_index + 2:]
                else:
                    chat_names.remove('--output')
            
            batch_mode(chat_names, output_file)
        else:
            print("❌ 未知参数")
            print("支持的参数:")
            print("  --batch 聊天名称1 聊天名称2 ... [--output 输出文件]")
    else:
        # 交互模式
        interactive_mode()


if __name__ == "__main__":
    main()