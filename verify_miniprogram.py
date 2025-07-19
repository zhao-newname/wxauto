#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小程序功能核心验证脚本
专注于验证小程序URL提取的核心功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_core_functionality():
    """测试核心功能"""
    print("🔧 开始核心功能验证...")
    
    try:
        # 1. 导入测试
        print("1. 测试模块导入...")
        from wxauto import WeChat
        print("   ✅ WeChat导入成功")
        
        # 2. 连接测试
        print("2. 测试微信连接...")
        wx = WeChat(debug=True)
        print(f"   ✅ 连接成功，用户: {wx.nickname}")
        
        # 3. 获取小程序消息
        print("3. 获取小程序消息...")
        messages = wx.GetMiniprogramMessages()
        print(f"   ✅ 找到 {len(messages)} 条小程序消息")
        
        if not messages:
            print("   ⚠️  当前聊天无小程序消息，请切换聊天后重试")
            return False
        
        # 4. 测试第一条消息的URL提取
        print("4. 测试URL提取...")
        msg = messages[0]
        print(f"   测试消息: {msg.app_name}")
        
        # 基本信息
        print(f"   应用名称: {msg.app_name}")
        print(f"   发送者: {msg.sender}")
        
        # 提取链接信息
        link_info = msg.extract_link_info()
        if link_info:
            print("   ✅ 链接信息提取成功")
            if link_info.get('app_id'):
                print(f"   AppID: {link_info['app_id']}")
        
        # 复制链接测试
        print("   尝试复制链接...")
        copy_result = msg.copy_link_info()
        if copy_result.success:
            print("   ✅ 链接复制成功")
            # 安全访问data属性
            data = copy_result.get('data') if hasattr(copy_result, 'get') else getattr(copy_result, 'data', None)
            if data and data.get('copied_content'):
                content = data['copied_content']
                print(f"   复制内容长度: {len(content)} 字符")
                
                # 简单URL检测
                if 'http' in content.lower() or 'weixin://' in content.lower():
                    print("   🎯 检测到可能的URL")
                else:
                    print("   ℹ️  未检测到明显URL")
            else:
                print("   ℹ️  复制成功但无详细内容")
        else:
            print(f"   ❌ 链接复制失败: {copy_result.get('message', '未知错误')}")
        
        print("\n🎉 核心功能验证完成！")
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 小程序URL提取核心功能验证")
    print("=" * 40)
    
    success = test_core_functionality()
    
    if success:
        print("\n✅ 验证通过！功能正常工作")
    else:
        print("\n❌ 验证失败，需要检查问题")
    
    print("\n💡 提示：确保微信已打开且当前聊天包含小程序消息")

if __name__ == "__main__":
    main()