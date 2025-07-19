#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的点击测试 - 专门测试小程序卡片点击是否有效
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_simple_click():
    """简单点击测试"""
    print("🔧 简单点击测试")
    print("=" * 30)
    
    try:
        from wxauto import WeChat
        import win32api, win32gui, win32con
        
        # 连接微信
        wx = WeChat(debug=False)
        print(f"✅ 连接成功: {wx.nickname}")
        
        # 获取小程序消息
        messages = wx.GetMiniprogramMessages()
        print(f"✅ 找到 {len(messages)} 条小程序消息")
        
        if not messages:
            print("❌ 没有小程序消息")
            return
        
        msg = messages[0]
        print(f"📱 准备点击: {msg.app_name}")
        
        # 获取控件位置
        rect = msg.control.BoundingRectangle
        if not rect:
            print("❌ 无法获取控件位置")
            return
            
        center_x = rect.left + rect.width() // 2
        center_y = rect.top + rect.height() // 2
        
        print(f"📍 控件位置: ({rect.left}, {rect.top}) - ({rect.right}, {rect.bottom})")
        print(f"📍 点击位置: ({center_x}, {center_y})")
        
        # 激活微信窗口
        wechat_hwnd = win32gui.FindWindow("WeChatMainWndForPC", None)
        if wechat_hwnd:
            win32gui.ShowWindow(wechat_hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(wechat_hwnd)
            time.sleep(0.5)
            print("✅ 微信窗口已激活")
        
        print("🖱️  3秒后自动开始点击...")
        time.sleep(3)
        
        # 移动鼠标到目标位置
        win32api.SetCursorPos((center_x, center_y))
        print(f"✅ 鼠标移动到 ({center_x}, {center_y})")
        time.sleep(0.5)
        
        # 执行点击
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        print("✅ 已执行点击")
        
        # 等待小程序打开
        print("⏳ 等待5秒观察小程序是否打开...")
        time.sleep(5)
        
        # 重新激活命令行窗口询问结果
        print("👀 请查看微信窗口")
        result = input("您看到小程序打开了吗？(y/n): ").strip().lower()
        
        if result == 'y':
            print("🎉 点击成功！小程序已打开")
            return True
        else:
            print("❌ 点击无效，小程序未打开")
            
            # 尝试双击
            print("🖱️  尝试双击...")
            win32api.SetCursorPos((center_x, center_y))
            time.sleep(0.3)
            
            # 双击
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            print("✅ 已执行双击")
            
            time.sleep(2)
            result2 = input("👀 双击后小程序打开了吗？(y/n): ").strip().lower()
            
            if result2 == 'y':
                print("🎉 双击成功！")
                return True
            else:
                print("❌ 双击也无效")
                return False
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    success = test_simple_click()
    
    if success:
        print("\n✅ 点击功能正常，可以继续下一步")
    else:
        print("\n❌ 点击功能有问题，需要先解决这个问题")

if __name__ == "__main__":
    main()