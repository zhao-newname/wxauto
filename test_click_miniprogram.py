#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小程序点击测试脚本
专门测试小程序卡片的点击功能
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_click():
    """测试点击功能"""
    print("🔧 小程序点击测试")
    print("=" * 30)
    
    try:
        from wxauto import WeChat
        import win32api, win32gui, win32con
        
        # 连接微信
        print("1. 连接微信...")
        wx = WeChat(debug=False)
        print(f"   ✅ 连接成功: {wx.nickname}")
        
        # 获取小程序消息
        print("2. 获取小程序消息...")
        messages = wx.GetMiniprogramMessages()
        print(f"   ✅ 找到 {len(messages)} 条小程序消息")
        
        if not messages:
            print("   ⚠️  没有小程序消息")
            return
        
        # 选择第一条消息
        msg = messages[0]
        print(f"3. 准备点击: {msg.app_name}")
        
        # 获取控件位置
        rect = msg.control.BoundingRectangle
        if not rect:
            print("   ❌ 无法获取控件位置")
            return
            
        center_x = rect.left + rect.width() // 2
        center_y = rect.top + rect.height() // 2
        print(f"   控件位置: ({rect.left}, {rect.top}) 大小: {rect.width()}x{rect.height()}")
        print(f"   点击位置: ({center_x}, {center_y})")
        
        # 激活微信窗口
        print("4. 激活微信窗口...")
        wechat_hwnd = win32gui.FindWindow("WeChatMainWndForPC", None)
        if wechat_hwnd:
            win32gui.ShowWindow(wechat_hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(wechat_hwnd)
            time.sleep(0.5)
            print("   ✅ 微信窗口已激活")
        
        # 询问是否继续
        input("   按回车键开始点击测试...")
        
        # 移动鼠标并点击
        print("5. 执行点击...")
        win32api.SetCursorPos((center_x, center_y))
        time.sleep(0.3)
        
        # 单击
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        print("   ✅ 已执行单击")
        
        # 等待并询问结果
        time.sleep(2)
        result = input("   小程序是否打开了? (y/n): ").strip().lower()
        
        if result == 'y':
            print("   🎉 单击成功！")
            
            # 测试复制链接
            print("6. 现在测试复制链接功能...")
            input("   请手动点击小程序右上角的'...'按钮，然后按回车继续...")
            
            # 查找复制链接按钮
            print("   正在查找复制链接选项...")
            time.sleep(1)
            
            # 尝试查找复制相关的按钮
            from wxauto import uiautomation as uia
            copy_options = ["复制链接", "复制小程序链接", "分享链接", "Copy Link"]
            
            found_copy = False
            for option in copy_options:
                try:
                    # 查找菜单项
                    menu_item = uia.MenuItemControl(searchDepth=3, Name=option)
                    if not menu_item.Exists(0.5):
                        menu_item = uia.ButtonControl(searchDepth=3, Name=option)
                    
                    if menu_item.Exists(0.5):
                        print(f"   找到复制选项: {option}")
                        menu_item.Click()
                        found_copy = True
                        break
                except Exception as e:
                    continue
            
            if found_copy:
                print("   ✅ 已点击复制选项")
                
                # 检查剪贴板
                try:
                    import pyperclip
                    time.sleep(1)
                    clipboard_content = pyperclip.paste()
                    print(f"   📋 剪贴板内容: {clipboard_content[:100]}...")
                    
                    if 'http' in clipboard_content or 'weixin://' in clipboard_content:
                        print("   🎯 检测到URL链接！")
                    else:
                        print("   ℹ️  剪贴板内容不包含明显的URL")
                        
                except Exception as e:
                    print(f"   ❌ 检查剪贴板失败: {str(e)}")
            else:
                print("   ❌ 未找到复制链接选项")
                
        else:
            print("   ❌ 单击未能打开小程序")
            
            # 尝试双击
            print("   尝试双击...")
            win32api.SetCursorPos((center_x, center_y))
            time.sleep(0.3)
            
            # 双击
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            print("   ✅ 已执行双击")
            
            time.sleep(2)
            result2 = input("   双击后小程序是否打开了? (y/n): ").strip().lower()
            
            if result2 == 'y':
                print("   🎉 双击成功！")
            else:
                print("   ❌ 双击也未能打开小程序")
                print("   💡 可能需要调整点击位置或方式")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    test_click()

if __name__ == "__main__":
    main()