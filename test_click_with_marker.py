#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
带标记的点击测试 - 在屏幕上显示点击位置
"""

import sys
import os
import time
import tkinter as tk
from tkinter import messagebox

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class ClickMarker:
    """点击位置标记器"""
    
    def __init__(self):
        self.markers = []
    
    def show_marker(self, x, y, color='red', size=20, duration=10):
        """在指定位置显示标记"""
        # 创建一个透明的顶层窗口
        marker = tk.Toplevel()
        marker.title("点击位置")
        marker.geometry(f"{size*2}x{size*2}+{x-size}+{y-size}")
        marker.attributes('-topmost', True)
        marker.attributes('-alpha', 0.8)
        marker.overrideredirect(True)  # 无边框
        
        # 创建画布
        canvas = tk.Canvas(marker, width=size*2, height=size*2, bg='white', highlightthickness=0)
        canvas.pack()
        
        # 画十字标记
        canvas.create_line(0, size, size*2, size, fill=color, width=3)  # 横线
        canvas.create_line(size, 0, size, size*2, fill=color, width=3)  # 竖线
        
        # 画圆圈
        canvas.create_oval(size-10, size-10, size+10, size+10, outline=color, width=3)
        
        # 添加文本
        canvas.create_text(size, size-15, text=f"({x},{y})", fill=color, font=('Arial', 8))
        
        self.markers.append(marker)
        
        # 定时关闭
        marker.after(duration * 1000, marker.destroy)
        
        return marker
    
    def clear_markers(self):
        """清除所有标记"""
        for marker in self.markers:
            try:
                marker.destroy()
            except:
                pass
        self.markers.clear()

def test_click_with_marker():
    """带标记的点击测试"""
    print("🔧 带标记的点击测试")
    print("=" * 30)
    
    try:
        from wxauto import WeChat
        import win32api, win32gui, win32con
        
        # 创建标记器
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        marker = ClickMarker()
        
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
        
        # 显示控件边界
        print(f"📍 控件边界:")
        print(f"   左上角: ({rect.left}, {rect.top})")
        print(f"   右下角: ({rect.right}, {rect.bottom})")
        print(f"   大小: {rect.width()} x {rect.height()}")
        
        # 计算几个可能的点击位置
        center_x = rect.left + rect.width() // 2
        center_y = rect.top + rect.height() // 2
        
        left_x = rect.left + rect.width() // 4
        left_y = rect.top + rect.height() // 2
        
        right_x = rect.left + rect.width() * 3 // 4
        right_y = rect.top + rect.height() // 2
        
        print(f"📍 计划点击位置:")
        print(f"   中心点: ({center_x}, {center_y})")
        print(f"   左侧点: ({left_x}, {left_y})")
        print(f"   右侧点: ({right_x}, {right_y})")
        
        # 激活微信窗口
        wechat_hwnd = win32gui.FindWindow("WeChatMainWndForPC", None)
        if wechat_hwnd:
            win32gui.ShowWindow(wechat_hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(wechat_hwnd)
            time.sleep(0.5)
            print("✅ 微信窗口已激活")
        
        # 显示控件边界标记
        print("🎯 显示控件边界标记...")
        marker.show_marker(rect.left, rect.top, 'blue', 15, 15)  # 左上角
        marker.show_marker(rect.right, rect.top, 'blue', 15, 15)  # 右上角
        marker.show_marker(rect.left, rect.bottom, 'blue', 15, 15)  # 左下角
        marker.show_marker(rect.right, rect.bottom, 'blue', 15, 15)  # 右下角
        
        # 显示点击位置标记
        print("🎯 显示点击位置标记...")
        marker.show_marker(center_x, center_y, 'red', 20, 15)  # 中心点
        marker.show_marker(left_x, left_y, 'green', 15, 15)  # 左侧点
        marker.show_marker(right_x, right_y, 'orange', 15, 15)  # 右侧点
        
        print("🖱️  5秒后开始点击中心点...")
        time.sleep(5)
        
        # 点击中心点
        win32api.SetCursorPos((center_x, center_y))
        time.sleep(0.3)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        print(f"✅ 已点击中心点 ({center_x}, {center_y})")
        
        # 等待观察
        time.sleep(3)
        
        # 询问结果
        result = messagebox.askyesno("点击测试", 
                                   f"您看到小程序打开了吗？\n\n"
                                   f"点击位置: ({center_x}, {center_y})\n"
                                   f"控件范围: ({rect.left}, {rect.top}) - ({rect.right}, {rect.bottom})")
        
        if not result:
            # 尝试点击左侧
            print("🖱️  尝试点击左侧位置...")
            win32api.SetCursorPos((left_x, left_y))
            time.sleep(0.3)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            print(f"✅ 已点击左侧点 ({left_x}, {left_y})")
            
            time.sleep(3)
            result2 = messagebox.askyesno("点击测试", 
                                        f"左侧点击有效果吗？\n\n"
                                        f"点击位置: ({left_x}, {left_y})")
            
            if not result2:
                # 尝试点击右侧
                print("🖱️  尝试点击右侧位置...")
                win32api.SetCursorPos((right_x, right_y))
                time.sleep(0.3)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                time.sleep(0.1)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                print(f"✅ 已点击右侧点 ({right_x}, {right_y})")
                
                time.sleep(3)
                result3 = messagebox.askyesno("点击测试", 
                                            f"右侧点击有效果吗？\n\n"
                                            f"点击位置: ({right_x}, {right_y})")
                
                if result3:
                    print("🎉 右侧点击有效！")
                    return True
                else:
                    print("❌ 所有位置点击都无效")
                    return False
            else:
                print("🎉 左侧点击有效！")
                return True
        else:
            print("🎉 中心点击有效！")
            return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False
    finally:
        # 清理标记
        try:
            marker.clear_markers()
            root.destroy()
        except:
            pass

def main():
    """主函数"""
    success = test_click_with_marker()
    
    if success:
        print("\n✅ 找到有效的点击位置！")
    else:
        print("\n❌ 需要进一步调试点击位置")

if __name__ == "__main__":
    main()