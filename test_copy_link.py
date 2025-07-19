#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试小程序复制链接功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_copy_link():
    """测试复制链接功能"""
    print("🔗 测试小程序复制链接功能")
    print("=" * 40)
    
    try:
        from wxauto import WeChat
        
        # 连接微信
        wx = WeChat(debug=True)
        print(f"✅ 连接成功: {wx.nickname}")
        
        # 获取小程序消息
        messages = wx.GetMiniprogramMessages()
        print(f"✅ 找到 {len(messages)} 条小程序消息")
        
        if not messages:
            print("❌ 没有小程序消息")
            return
        
        msg = messages[0]
        print(f"📱 测试消息: {msg.app_name}")
        print(f"📝 消息描述: {msg.app_description}")
        print(f"👤 发送者: {msg.sender}")
        
        # 显示控件信息
        if msg.control.Name:
            print(f"🔍 控件内容预览: {msg.control.Name[:100]}...")
        
        # 测试复制链接功能
        print(f"\n🔗 测试复制链接功能...")
        result = msg.copy_link_info()
        
        if result.success:
            print("✅ 复制链接成功！")
            
            # 显示复制的内容
            data = result.data if hasattr(result, 'data') else {}
            if data and data.get('copied_content'):
                print(f"📋 复制的内容:")
                print("-" * 30)
                print(data['copied_content'])
                print("-" * 30)
                
                # 检查是否包含小程序链接
                content = data['copied_content']
                if '#小程序://' in content:
                    print("🎉 成功提取到小程序链接！")
                else:
                    print("⚠️  复制成功但未包含小程序链接")
                    
                print(f"📊 提取方法: {data.get('extraction_method', '未知')}")
            else:
                print("⚠️  复制成功但无详细内容")
        else:
            print(f"❌ 复制链接失败: {result.message}")
        
        # 显示小程序的技术参数
        print(f"\n📊 小程序技术参数:")
        print(f"   AppID: {msg.app_id}")
        print(f"   页面路径: {msg.page_path}")
        print(f"   页面参数: {msg.page_params}")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    test_copy_link()

if __name__ == "__main__":
    main()