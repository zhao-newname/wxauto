#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
精确点击定位调试脚本
分析小程序卡片的内部结构，找到最佳点击位置
"""

import sys
import os
import time
import win32api
import win32gui
import win32con

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def analyze_miniprogram_structure():
    """分析小程序卡片的内部结构"""
    print("🔍 小程序卡片结构分析")
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
        print(f"\n📱 分析消息: {msg.app_name}")
        
        # 获取主控件信息
        main_rect = msg.control.BoundingRectangle
        if not main_rect:
            print("❌ 无法获取主控件位置")
            return
            
        print(f"📍 主控件位置: ({main_rect.left}, {main_rect.top}) - ({main_rect.right}, {main_rect.bottom})")
        print(f"📏 主控件大小: {main_rect.width()} x {main_rect.height()}")
        
        # 分析子控件结构
        print(f"\n🔍 分析子控件结构:")
        clickable_areas = []
        
        # 遍历所有子控件
        control_index = 0
        for control in uia.WalkControl(msg.control):
            if control == msg.control:
                continue  # 跳过主控件自身
                
            control_index += 1
            if control_index > 20:  # 限制输出数量
                break
                
            try:
                rect = control.BoundingRectangle
                if rect and rect.width() > 0 and rect.height() > 0:
                    control_type = getattr(control, 'ControlTypeName', 'Unknown')
                    control_name = getattr(control, 'Name', '') or ''
                    
                    print(f"  [{control_index}] {control_type}")
                    print(f"      位置: ({rect.left}, {rect.top}) - ({rect.right}, {rect.bottom})")
                    print(f"      大小: {rect.width()} x {rect.height()}")
                    if control_name:
                        print(f"      名称: {control_name[:50]}...")
                    
                    # 检查是否是可点击的控件
                    if control_type in ['ButtonControl', 'HyperlinkControl', 'ImageControl']:
                        clickable_areas.append({
                            'control': control,
                            'rect': rect,
                            'type': control_type,
                            'name': control_name,
                            'center': (rect.left + rect.width() // 2, rect.top + rect.height() // 2)
                        })
                        print(f"      ⭐ 可点击区域候选")
                    
                    print()
                    
            except Exception as e:
                print(f"  控件分析异常: {str(e)}")
        
        # 分析可点击区域
        print(f"🎯 找到 {len(clickable_areas)} 个可点击区域候选:")
        for i, area in enumerate(clickable_areas):
            print(f"  [{i+1}] {area['type']} - 中心点: {area['center']}")
            if area['name']:
                print(f"      名称: {area['name'][:30]}...")
        
        # 计算推荐的点击位置
        recommended_positions = calculate_click_positions(main_rect, clickable_areas)
        
        print(f"\n🎯 推荐点击位置:")
        for i, pos in enumerate(recommended_positions):
            print(f"  [{i+1}] {pos['description']}: ({pos['x']}, {pos['y']})")
        
        # 测试点击
        if recommended_positions:
            print(f"\n🖱️  准备测试点击...")
            test_click_positions(recommended_positions, msg.control)
        
    except Exception as e:
        print(f"❌ 分析失败: {str(e)}")
        import traceback
        traceback.print_exc()

def calculate_click_positions(main_rect, clickable_areas):
    """计算推荐的点击位置"""
    positions = []
    
    # 1. 如果有明确的可点击控件，优先使用它们的中心点
    for area in clickable_areas:
        if area['type'] == 'ButtonControl':
            positions.append({
                'x': area['center'][0],
                'y': area['center'][1],
                'description': f"按钮控件中心 ({area['type']})",
                'priority': 1
            })
        elif area['type'] == 'ImageControl':
            positions.append({
                'x': area['center'][0],
                'y': area['center'][1],
                'description': f"图片控件中心 ({area['type']})",
                'priority': 2
            })
    
    # 2. 主控件的不同区域
    # 左侧区域（通常是图标区域）
    left_x = main_rect.left + main_rect.width() // 6
    center_y = main_rect.top + main_rect.height() // 2
    positions.append({
        'x': left_x,
        'y': center_y,
        'description': "主控件左侧区域",
        'priority': 3
    })
    
    # 中心区域
    center_x = main_rect.left + main_rect.width() // 2
    positions.append({
        'x': center_x,
        'y': center_y,
        'description': "主控件中心区域",
        'priority': 4
    })
    
    # 右侧区域
    right_x = main_rect.left + main_rect.width() * 5 // 6
    positions.append({
        'x': right_x,
        'y': center_y,
        'description': "主控件右侧区域",
        'priority': 5
    })
    
    # 按优先级排序
    positions.sort(key=lambda x: x['priority'])
    
    return positions

def test_click_positions(positions, control):
    """测试不同的点击位置"""
    print(f"🧪 开始测试点击位置...")
    
    # 激活微信窗口
    wechat_hwnd = win32gui.FindWindow("WeChatMainWndForPC", None)
    if wechat_hwnd:
        win32gui.ShowWindow(wechat_hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(wechat_hwnd)
        time.sleep(1)
        print("✅ 微信窗口已激活")
    
    for i, pos in enumerate(positions[:3]):  # 只测试前3个位置
        print(f"\n🖱️  测试位置 {i+1}: {pos['description']}")
        print(f"   坐标: ({pos['x']}, {pos['y']})")
        
        try:
            # 移动鼠标到目标位置
            win32api.SetCursorPos((pos['x'], pos['y']))
            time.sleep(0.5)
            
            # 执行点击
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            
            print(f"   ✅ 已点击位置 {i+1}")
            
            # 等待观察结果
            time.sleep(2)
            
            # 检查是否有新窗口打开（简单检测）
            current_window = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(current_window)
            
            if "小程序" in window_title or current_window != wechat_hwnd:
                print(f"   🎉 位置 {i+1} 点击成功！检测到窗口变化")
                return True
            else:
                print(f"   ❌ 位置 {i+1} 点击无效果")
                
        except Exception as e:
            print(f"   ❌ 位置 {i+1} 点击异常: {str(e)}")
        
        # 重新激活微信窗口准备下次测试
        if i < len(positions) - 1:
            win32gui.SetForegroundWindow(wechat_hwnd)
            time.sleep(1)
    
    print(f"\n❌ 所有测试位置都无效果")
    return False

def main():
    """主函数"""
    analyze_miniprogram_structure()

if __name__ == "__main__":
    main()