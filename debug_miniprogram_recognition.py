#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小程序识别和点击调试脚本
专门用于调试小程序卡片的识别和点击功能
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_miniprogram_click():
    """调试小程序点击功能"""
    print("🔧 小程序点击功能调试")
    print("=" * 40)
    
    try:
        from wxauto import WeChat
        
        # 连接微信
        print("1. 连接微信...")
        wx = WeChat(debug=True)
        print(f"   ✅ 连接成功: {wx.nickname}")
        
        # 获取小程序消息
        print("2. 获取小程序消息...")
        messages = wx.GetMiniprogramMessages()
        print(f"   ✅ 找到 {len(messages)} 条小程序消息")
        
        if not messages:
            print("   ⚠️  没有小程序消息可测试")
            return
        
        # 选择第一条消息进行测试
        msg = messages[0]
        print(f"3. 测试消息: {msg.app_name}")
        
        # 获取控件位置信息
        rect = msg.control.BoundingRectangle
        if rect:
            print(f"   控件位置: ({rect.left}, {rect.top}) - ({rect.right}, {rect.bottom})")
            print(f"   控件大小: {rect.width()} x {rect.height()}")
            
            # 计算中心点
            center_x = rect.left + rect.width() // 2
            center_y = rect.top + rect.height() // 2
            print(f"   中心点: ({center_x}, {center_y})")
        else:
            print("   ❌ 无法获取控件位置")
            return
        
        # 询问是否继续测试点击
        print("\n4. 准备测试点击功能...")
        print("   注意：这将会点击小程序卡片并尝试打开小程序")
        
        choice = input("   是否继续? (y/n): ").strip().lower()
        if choice != 'y':
            print("   测试取消")
            return
        
        # 测试打开小程序
        print("5. 测试打开小程序...")
        result = msg.open_miniprogram()
        
        if result.success:
            print("   ✅ 小程序打开成功")
            
            # 等待用户确认小程序是否真的打开了
            time.sleep(2)
            actual_opened = input("   小程序是否真的打开了? (y/n): ").strip().lower()
            
            if actual_opened == 'y':
                print("   🎉 点击功能正常工作！")
                
                # 测试复制链接功能
                print("6. 测试复制链接功能...")
                copy_result = msg.copy_link_info()
                
                if copy_result.success:
                    print("   ✅ 链接复制成功")
                    # 安全访问data
                    data = copy_result.get('data') if hasattr(copy_result, 'get') else getattr(copy_result, 'data', None)
                    if data and data.get('copied_content'):
                        content = data['copied_content']
                        print(f"   📋 复制内容: {content}")
                    else:
                        print("   ℹ️  复制成功但无详细内容")
                else:
                    print(f"   ❌ 链接复制失败: {copy_result.get('message', '未知错误')}")
            else:
                print("   ❌ 小程序实际未打开，点击功能需要调试")
        else:
            print(f"   ❌ 小程序打开失败: {result.message}")
        
    except Exception as e:
        print(f"❌ 调试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    debug_miniprogram_click()

if __name__ == "__main__":
    main()