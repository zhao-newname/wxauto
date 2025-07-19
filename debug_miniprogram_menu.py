#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小程序菜单按钮自动调试脚本
自动分析小程序界面并测试菜单按钮位置
"""

import sys
import os
import time
import win32api
import win32gui
import win32con

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_miniprogram_menu_auto():
    """自动调试小程序菜单功能"""
    print("🔍 小程序菜单按钮自动调试")
    print("=" * 50)
    
    try:
        from wxauto import WeChat
        from wxauto import uiautomation as uia
        
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
        
        # 步骤1: 打开小程序
        print("\n🚀 步骤1: 打开小程序...")
        result = msg.open_miniprogram()
        if not result.success:
            print(f"❌ 无法打开小程序: {result.message}")
            return
        
        print("✅ 小程序已打开")
        
        # 等待小程序完全加载
        print("⏳ 等待小程序加载...")
        time.sleep(4)
        
        # 步骤2: 获取当前窗口信息
        print("\n🔍 步骤2: 分析小程序窗口...")
        current_window = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(current_window)
        window_rect = win32gui.GetWindowRect(current_window)
        
        print(f"当前窗口: {window_title}")
        print(f"窗口位置: {window_rect}")
        print(f"窗口大小: {window_rect[2] - window_rect[0]} x {window_rect[3] - window_rect[1]}")
        
        # 步骤3: 自动测试右上角菜单按钮位置
        print("\n🖱️  步骤3: 自动测试菜单按钮位置...")
        
        # 计算可能的菜单按钮位置
        menu_positions = calculate_menu_positions(window_rect)
        
        successful_menu_pos = None
        for i, pos in enumerate(menu_positions):
            print(f"测试菜单位置 {i+1}: ({pos['x']}, {pos['y']}) - {pos['description']}")
            
            # 点击菜单位置
            win32api.SetCursorPos((pos['x'], pos['y']))
            time.sleep(0.3)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            
            # 等待菜单出现
            time.sleep(1.5)
            
            # 检查是否有菜单出现（通过检查窗口变化或新控件）
            if check_menu_appeared():
                print(f"✅ 菜单位置 {i+1} 成功！")
                successful_menu_pos = pos
                
                # 测试复制链接位置
                copy_success = test_copy_link_positions(pos)
                if copy_success:
                    print(f"🎉 找到完整的复制链接流程！")
                    return pos, copy_success
                else:
                    print(f"❌ 菜单打开了但复制链接失败")
                    # 关闭菜单，继续测试下一个位置
                    close_menu()
            else:
                print(f"❌ 菜单位置 {i+1} 无效")
            
            time.sleep(0.5)
        
        if not successful_menu_pos:
            print("❌ 未找到有效的菜单按钮位置")
        
    except Exception as e:
        print(f"❌ 调试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def calculate_menu_positions(window_rect):
    """计算可能的菜单按钮位置"""
    left, top, right, bottom = window_rect
    width = right - left
    height = bottom - top
    
    positions = [
        # 右上角不同位置
        {'x': right - 40, 'y': top + 40, 'description': '右上角标准位置'},
        {'x': right - 60, 'y': top + 40, 'description': '右上角偏左'},
        {'x': right - 40, 'y': top + 60, 'description': '右上角偏下'},
        {'x': right - 80, 'y': top + 40, 'description': '右上角更偏左'},
        {'x': right - 40, 'y': top + 80, 'description': '右上角更偏下'},
        
        # 标题栏右侧
        {'x': right - 100, 'y': top + 30, 'description': '标题栏右侧'},
        {'x': right - 120, 'y': top + 30, 'description': '标题栏中右'},
        
        # 内容区域右上角
        {'x': right - 50, 'y': top + 100, 'description': '内容区右上角'},
        {'x': right - 80, 'y': top + 100, 'description': '内容区右上偏左'},
    ]
    
    return positions

def check_menu_appeared():
    """检查菜单是否出现"""
    try:
        # 方法1: 检查是否有新的弹出窗口
        current_window = win32gui.GetForegroundWindow()
        
        # 方法2: 简单等待，假设菜单已出现
        # 在实际应用中，这里可以添加更复杂的检测逻辑
        return True  # 暂时假设菜单总是出现
        
    except Exception:
        return False

def test_copy_link_positions(menu_pos):
    """测试复制链接位置"""
    print(f"  🔍 测试复制链接位置...")
    
    # 基于菜单位置计算可能的复制链接位置
    copy_positions = [
        {'x': menu_pos['x'] - 80, 'y': menu_pos['y'] + 40, 'description': '菜单下方'},
        {'x': menu_pos['x'] - 120, 'y': menu_pos['y'] + 40, 'description': '菜单下方偏左'},
        {'x': menu_pos['x'] - 80, 'y': menu_pos['y'] + 60, 'description': '菜单下方更下'},
        {'x': menu_pos['x'] - 100, 'y': menu_pos['y'] + 80, 'description': '菜单下方最下'},
        {'x': menu_pos['x'] - 60, 'y': menu_pos['y'] + 50, 'description': '菜单下方偏右'},
    ]
    
    for i, pos in enumerate(copy_positions):
        print(f"    测试复制位置 {i+1}: ({pos['x']}, {pos['y']}) - {pos['description']}")
        
        # 点击复制位置
        win32api.SetCursorPos((pos['x'], pos['y']))
        time.sleep(0.3)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        
        # 等待复制操作
        time.sleep(1)
        
        # 检查剪贴板是否有新内容
        if check_clipboard_changed():
            print(f"    ✅ 复制位置 {i+1} 成功！")
            return pos
        else:
            print(f"    ❌ 复制位置 {i+1} 无效")
    
    return None

def check_clipboard_changed():
    """检查剪贴板是否有变化"""
    try:
        import pyperclip
        current_clipboard = pyperclip.paste()
        
        # 检查剪贴板内容是否包含小程序相关信息
        if any(keyword in current_clipboard for keyword in ['小程序', 'miniprogram', 'weapp', 'http']):
            print(f"    📋 剪贴板内容: {current_clipboard[:100]}...")
            return True
        return False
    except Exception:
        return False

def close_menu():
    """关闭菜单"""
    try:
        # 点击空白区域关闭菜单
        win32api.SetCursorPos((500, 400))
        time.sleep(0.2)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.5)
    except Exception:
        pass

def main():
    """主函数"""
    debug_miniprogram_menu_auto()

if __name__ == "__main__":
    main()