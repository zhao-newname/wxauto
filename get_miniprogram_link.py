#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小程序链接获取工具 - 简化版

这是一个简化的小程序链接获取工具，专门用于快速获取小程序的URL和相关信息。
适合日常使用和快速测试。
"""

import sys
import os
import time
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from wxauto import WeChat
    print("✅ wxauto模块加载成功")
except ImportError as e:
    print(f"❌ 无法导入wxauto: {str(e)}")
    print("请确保已正确安装wxauto")
    sys.exit(1)


def get_miniprogram_links():
    """获取当前聊天中的小程序链接"""
    
    print("🚀 小程序链接获取工具")
    print("=" * 40)
    
    try:
        # 连接微信
        print("📱 正在连接微信...")
        wx = WeChat(debug=False)
        
        if not wx or not wx.nickname:
            print("❌ 无法连接到微信")
            print("请确保：")
            print("1. 微信已打开并登录")
            print("2. 微信版本支持自动化")
            return
        
        print(f"✅ 连接成功！用户: {wx.nickname}")
        
        # 获取小程序消息
        print("\n🔍 搜索小程序消息...")
        miniprogram_messages = wx.GetMiniprogramMessages()
        
        if not miniprogram_messages:
            print("⚠️  当前聊天中没有找到小程序消息")
            print("💡 请切换到包含小程序消息的聊天后重试")
            return
        
        print(f"✅ 找到 {len(miniprogram_messages)} 条小程序消息")
        
        # 提取链接信息
        results = []
        print("\n📋 正在提取链接信息...")
        
        for i, msg in enumerate(miniprogram_messages):
            print(f"  处理 {i+1}/{len(miniprogram_messages)}: {msg.app_name}")
            
            try:
                # 基本信息
                info = {
                    'index': i + 1,
                    'app_name': msg.app_name,
                    'app_description': msg.app_description,
                    'sender': msg.sender,
                    'extraction_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # 提取详细信息
                link_info = msg.extract_link_info()
                if link_info:
                    info.update(link_info)
                
                # 尝试复制链接信息
                copy_result = msg.copy_link_info()
                if copy_result.success and copy_result.data:
                    copied_content = copy_result.data.get('copied_content', '')
                    if copied_content:
                        info['copied_info'] = copied_content
                        
                        # 提取URL
                        urls = extract_urls(copied_content)
                        if urls:
                            info['urls'] = urls
                
                results.append(info)
                time.sleep(0.3)  # 避免操作过快
                
            except Exception as e:
                print(f"    ❌ 处理失败: {str(e)}")
                continue
        
        # 显示结果
        print(f"\n📊 提取完成！共处理 {len(results)} 条小程序消息")
        display_results(results)
        
        # 保存结果
        save_choice = input("\n💾 是否保存结果到文件? (y/n): ").strip().lower()
        if save_choice == 'y':
            filename = save_results(results)
            if filename:
                print(f"✅ 结果已保存到: {filename}")
        
    except KeyboardInterrupt:
        print("\n👋 用户中断操作")
    except Exception as e:
        print(f"❌ 程序异常: {str(e)}")


def extract_urls(text):
    """从文本中提取URL"""
    import re
    
    patterns = [
        r'https?://[^\s<>"{}|\\^`\[\]]+',
        r'weixin://[^\s<>"{}|\\^`\[\]]+',
    ]
    
    urls = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        urls.extend(matches)
    
    return list(set(urls))


def display_results(results):
    """显示提取结果"""
    if not results:
        print("没有结果可显示")
        return
    
    print("\n" + "=" * 60)
    print("📋 小程序链接提取结果")
    print("=" * 60)
    
    url_count = 0
    
    for item in results:
        print(f"\n{item['index']}. {item['app_name']}")
        print(f"   发送者: {item['sender']}")
        
        if item.get('app_description'):
            desc = item['app_description'][:50] + "..." if len(item['app_description']) > 50 else item['app_description']
            print(f"   描述: {desc}")
        
        if item.get('app_id'):
            print(f"   AppID: {item['app_id']}")
        
        if item.get('page_path'):
            print(f"   页面路径: {item['page_path']}")
        
        urls = item.get('urls', [])
        if urls:
            print(f"   🔗 URL ({len(urls)}个):")
            for url in urls:
                print(f"      {url}")
            url_count += len(urls)
        else:
            print(f"   🔗 URL: 未找到")
        
        if item.get('copied_info'):
            print(f"   📋 复制信息: 已获取 ({len(item['copied_info'])} 字符)")
    
    print("\n" + "=" * 60)
    print(f"📊 总结: {len(results)} 个小程序, {url_count} 个URL")
    print("=" * 60)


def save_results(results):
    """保存结果到文件"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"miniprogram_links_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'extraction_time': datetime.now().isoformat(),
                'total_count': len(results),
                'results': results
            }, f, ensure_ascii=False, indent=2)
        
        return filename
        
    except Exception as e:
        print(f"❌ 保存失败: {str(e)}")
        return None


def show_help():
    """显示帮助信息"""
    print("""
🚀 小程序链接获取工具使用说明

功能：
- 自动连接微信客户端
- 扫描当前聊天中的小程序消息
- 提取小程序的URL、AppID等信息
- 支持保存结果到JSON文件

使用方法：
1. 确保微信已打开并登录
2. 切换到包含小程序消息的聊天
3. 运行此脚本
4. 按提示操作

注意事项：
- 需要微信客户端支持UI自动化
- 建议在测试环境中使用
- 提取过程中请勿操作微信窗口

支持的URL类型：
- HTTP/HTTPS链接
- 微信协议链接 (weixin://)
- 小程序专用链接

输出信息包括：
- 小程序名称和描述
- 发送者信息
- AppID和页面路径
- 提取到的URL链接
- 完整的复制信息
""")


def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h']:
            show_help()
            return
        elif sys.argv[1] == '--version':
            print("小程序链接获取工具 v1.0")
            return
    
    try:
        get_miniprogram_links()
    except Exception as e:
        print(f"❌ 程序运行失败: {str(e)}")
        print("\n💡 如需帮助，请运行: python get_miniprogram_link.py --help")


if __name__ == "__main__":
    main()