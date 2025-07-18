#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试小程序识别功能
"""

import sys
import os
import time

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wxauto import WeChat
from wxauto.msgs.msg import _is_miniprogram_message
from wxauto.msgs.miniprogram import MiniprogramCardAnalyzer
from wxauto.logger import wxlog

def debug_miniprogram_recognition():
    """调试小程序识别功能"""
    print("🔍 开始调试小程序识别功能")
    
    try:
        # 连接微信
        wx = WeChat()
        print("✅ 微信连接成功")
        
        # 切换到文件传输助手
        wx.ChatWith("文件传输助手")
        time.sleep(2)
        
        # 获取消息
        messages = wx.GetAllMessage()
        print(f"✅ 获取到 {len(messages)} 条消息")
        
        for i, msg in enumerate(messages, 1):
            print(f"\n{'='*50}")
            print(f"消息 {i}: {msg.type}")
            print(f"内容: {msg.content[:100]}...")
            
            if hasattr(msg, 'control') and msg.control:
                print(f"控件存在: True")
                
                # 测试控件尺寸
                if hasattr(msg.control, 'BoundingRectangle') and msg.control.BoundingRectangle:
                    rect = msg.control.BoundingRectangle
                    width = rect.right - rect.left
                    height = rect.bottom - rect.top
                    print(f"控件尺寸: {width}x{height}")
                
                # 测试_is_miniprogram_message函数
                print("🔍 测试 _is_miniprogram_message 函数:")
                try:
                    is_miniprogram = _is_miniprogram_message(msg.control)
                    print(f"  结果: {is_miniprogram}")
                    
                    if is_miniprogram:
                        print("  ✅ 识别为小程序消息!")
                    else:
                        print("  ❌ 未识别为小程序消息")
                        
                        # 详细调试MiniprogramCardAnalyzer
                        print("  🔍 详细调试 MiniprogramCardAnalyzer:")
                        try:
                            analyzer = MiniprogramCardAnalyzer(msg.control)
                            
                            # 测试尺寸检查
                            size_ok = analyzer._check_size_features()
                            print(f"    尺寸检查: {size_ok}")
                            
                            if size_ok:
                                # 测试其他特征
                                structure_ok = analyzer._check_structure_features()
                                print(f"    结构特征: {structure_ok}")
                                
                                child_ok = analyzer._check_child_control_features()
                                print(f"    子控件特征: {child_ok}")
                                
                                name_ok = analyzer._check_name_indicators()
                                print(f"    名称特征: {name_ok}")
                                
                                layout_ok = analyzer._check_layout_features()
                                print(f"    布局特征: {layout_ok}")
                                
                                # 手动计算分数
                                score = 0
                                if structure_ok: score += 40
                                if child_ok: score += 30
                                if name_ok: score += 20
                                if layout_ok: score += 10
                                
                                print(f"    总分: {score}/100 (阈值: 70)")
                                
                                if score >= 70:
                                    print("    ✅ 应该被识别为小程序")
                                else:
                                    print("    ❌ 分数不足，未达到识别阈值")
                            else:
                                print("    ❌ 尺寸检查失败，直接排除")
                                
                        except Exception as e:
                            print(f"    ❌ MiniprogramCardAnalyzer 异常: {str(e)}")
                            import traceback
                            traceback.print_exc()
                        
                except Exception as e:
                    print(f"  ❌ _is_miniprogram_message 异常: {str(e)}")
                    import traceback
                    traceback.print_exc()
            else:
                print("控件不存在或无效")
                
    except Exception as e:
        print(f"❌ 调试过程异常: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 设置日志级别为DEBUG以获取更多信息
    # wxlog.setLevel('DEBUG')  # WxautoLogger没有setLevel方法
    debug_miniprogram_recognition()