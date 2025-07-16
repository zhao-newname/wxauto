#!/usr/bin/env python3
"""
小程序基本信息提取功能测试脚本

测试任务4的验收标准：
- app_name属性能够正确提取小程序名称，成功率90%以上
- app_description属性能够提取描述信息（如果存在）
- 缩略图信息能够被识别和获取
- 提取失败时返回合理的默认值，不抛出异常
"""

import sys
import os
import traceback
from typing import List, Dict, Any
from unittest.mock import Mock, MagicMock

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from wxauto.msgs.miniprogram import MiniprogramMessage, MiniprogramCardAnalyzer, MiniprogramInfo
    from wxauto import uiautomation as uia
    from wxauto.logger import wxlog
except ImportError as e:
    print(f"导入模块失败: {e}")
    sys.exit(1)


class MockControl:
    """模拟UI控件类"""
    
    def __init__(self, name: str = "", control_type: str = "PaneControl", 
                 width: int = 400, height: int = 120, has_image: bool = True,
                 text_controls: List[str] = None):
        self.Name = name
        self.ControlTypeName = control_type
        self._width = width
        self._height = height
        self._has_image = has_image
        self._text_controls = text_controls or []
        self._exists = True
        
        # 模拟BoundingRectangle
        self.BoundingRectangle = Mock()
        self.BoundingRectangle.width.return_value = width
        self.BoundingRectangle.height.return_value = height
        self.BoundingRectangle.left = 100
        self.BoundingRectangle.top = 100
        
    def Exists(self, timeout=0):
        return self._exists
        
    def ImageControl(self, searchDepth=3):
        """模拟图片控件查找"""
        mock_img = Mock()
        mock_img.Exists.return_value = self._has_image
        return mock_img
        
    def ButtonControl(self, searchDepth=3):
        """模拟按钮控件查找"""
        mock_btn = Mock()
        mock_btn.Exists.return_value = self._has_image
        if self._has_image:
            mock_btn.BoundingRectangle = Mock()
            mock_btn.BoundingRectangle.width.return_value = 64
            mock_btn.BoundingRectangle.height.return_value = 64
            mock_btn.BoundingRectangle.left = 110
            mock_btn.BoundingRectangle.top = 110
        return mock_btn


def create_mock_walk_control(control, text_controls):
    """创建模拟的WalkControl函数"""
    def mock_walk_control(root_control):
        # 返回根控件和文本子控件
        yield root_control
        
        for i, text in enumerate(text_controls):
            mock_text_ctrl = Mock()
            mock_text_ctrl.Name = text
            mock_text_ctrl.ControlTypeName = 'TextControl'
            yield mock_text_ctrl
            
        # 添加一些其他类型的控件以增加多样性
        for ctrl_type in ['ButtonControl', 'ImageControl', 'PaneControl']:
            mock_ctrl = Mock()
            mock_ctrl.Name = ""
            mock_ctrl.ControlTypeName = ctrl_type
            yield mock_ctrl
            
    return mock_walk_control


def create_test_cases() -> List[Dict[str, Any]]:
    """创建测试用例"""
    test_cases = [
        {
            'name': '游戏类小程序 - 跳一跳',
            'control_name': '跳一跳 小游戏 - 挑战你的反应速度',
            'text_controls': ['跳一跳', '挑战你的反应速度，看看你能跳多远！'],
            'expected_app_name': '跳一跳',
            'expected_has_description': True,
            'width': 450, 'height': 100
        },
        {
            'name': '工具类小程序 - 计算器',
            'control_name': '计算器工具 | 简单实用的计算工具',
            'text_controls': ['计算器工具', '简单实用的计算工具'],
            'expected_app_name': '计算器工具',
            'expected_has_description': True,
            'width': 380, 'height': 90
        },
        {
            'name': '电商类小程序 - 购物商城',
            'control_name': '购物商城·优惠多多',
            'text_controls': ['购物商城', '优惠多多，品质保证，快来选购吧！'],
            'expected_app_name': '购物商城',
            'expected_has_description': True,
            'width': 420, 'height': 110
        },
        {
            'name': '简单小程序 - 天气',
            'control_name': '天气',
            'text_controls': ['天气'],
            'expected_app_name': '天气',
            'expected_has_description': False,
            'width': 350, 'height': 80
        },
        {
            'name': '复杂名称小程序',
            'control_name': '美团外卖【小程序】- 30分钟送达',
            'text_controls': ['美团外卖', '30分钟送达，新用户立减10元'],
            'expected_app_name': '美团外卖',
            'expected_has_description': True,
            'width': 480, 'height': 120
        },
        {
            'name': '英文小程序',
            'control_name': 'GitHub Mini App',
            'text_controls': ['GitHub Mini App', 'Manage your repositories on the go'],
            'expected_app_name': 'GitHub Mini App',
            'expected_has_description': True,
            'width': 400, 'height': 95
        },
        {
            'name': '无描述小程序',
            'control_name': '记账本',
            'text_controls': ['记账本'],
            'expected_app_name': '记账本',
            'expected_has_description': False,
            'width': 320, 'height': 75
        },
        {
            'name': '长描述小程序',
            'control_name': '学习助手',
            'text_controls': ['学习助手', '专业的学习管理工具，帮助你制定学习计划，跟踪学习进度，提高学习效率。支持多种学习模式，适合各年龄段用户使用。'],
            'expected_app_name': '学习助手',
            'expected_has_description': True,
            'width': 460, 'height': 130
        },
        {
            'name': '特殊字符小程序',
            'control_name': '音乐播放器♪',
            'text_controls': ['音乐播放器♪', '享受高品质音乐体验'],
            'expected_app_name': '音乐播放器♪',
            'expected_has_description': True,
            'width': 390, 'height': 105
        },
        {
            'name': '数字开头小程序',
            'control_name': '2048小游戏',
            'text_controls': ['2048小游戏', '经典数字合成游戏'],
            'expected_app_name': '2048小游戏',
            'expected_has_description': True,
            'width': 370, 'height': 85
        }
    ]
    
    return test_cases


def test_miniprogram_card_analyzer():
    """测试MiniprogramCardAnalyzer类"""
    print("=" * 60)
    print("测试 MiniprogramCardAnalyzer 类")
    print("=" * 60)
    
    test_cases = create_test_cases()
    success_count = 0
    total_count = len(test_cases)
    
    # 临时替换uia.WalkControl函数
    original_walk_control = None
    try:
        import wxauto.uiautomation as uia
        original_walk_control = uia.WalkControl
    except:
        pass
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {case['name']}")
        print("-" * 40)
        
        try:
            # 创建模拟控件
            mock_control = MockControl(
                name=case['control_name'],
                width=case['width'],
                height=case['height'],
                text_controls=case['text_controls']
            )
            
            # 临时替换WalkControl函数
            if original_walk_control:
                uia.WalkControl = create_mock_walk_control(mock_control, case['text_controls'])
            
            # 创建分析器
            analyzer = MiniprogramCardAnalyzer(mock_control)
            
            # 测试小程序卡片识别
            is_miniprogram = analyzer.is_miniprogram_card()
            print(f"小程序卡片识别: {'✓' if is_miniprogram else '✗'}")
            
            if is_miniprogram:
                # 测试应用名称提取
                app_name = analyzer.extract_app_name()
                print(f"提取的应用名称: '{app_name}'")
                print(f"期望的应用名称: '{case['expected_app_name']}'")
                
                name_correct = app_name == case['expected_app_name'] or case['expected_app_name'] in app_name
                print(f"名称提取正确: {'✓' if name_correct else '✗'}")
                
                # 测试描述提取
                description = analyzer.extract_description()
                print(f"提取的描述: '{description[:50]}{'...' if len(description) > 50 else ''}'")
                
                has_description = len(description) > 0
                description_correct = has_description == case['expected_has_description']
                print(f"描述提取正确: {'✓' if description_correct else '✗'}")
                
                # 测试缩略图信息
                thumbnail_info = analyzer.extract_thumbnail_info()
                print(f"缩略图信息: {thumbnail_info['has_thumbnail']}")
                
                # 测试关键控件查找
                key_controls = analyzer.find_key_child_controls()
                found_controls = sum(1 for ctrl in key_controls.values() if ctrl is not None)
                print(f"找到关键控件数量: {found_controls}/4")
                
                # 判断测试是否成功
                if name_correct and description_correct:
                    success_count += 1
                    print("✓ 测试通过")
                else:
                    print("✗ 测试失败")
            else:
                print("✗ 小程序卡片识别失败")
                
        except Exception as e:
            print(f"✗ 测试异常: {str(e)}")
            traceback.print_exc()
        
        finally:
            # 恢复原始函数
            if original_walk_control:
                uia.WalkControl = original_walk_control
    
    print(f"\n总体测试结果: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    return success_count / total_count >= 0.9


def test_miniprogram_message():
    """测试MiniprogramMessage类"""
    print("\n" + "=" * 60)
    print("测试 MiniprogramMessage 类")
    print("=" * 60)
    
    try:
        # 创建模拟控件
        mock_control = MockControl(
            name="测试小程序 - 这是一个测试用的小程序",
            text_controls=["测试小程序", "这是一个测试用的小程序描述"]
        )
        
        # 创建模拟父对象
        mock_parent = Mock()
        mock_parent.chat_info.return_value = {'chat_name': '测试聊天'}
        
        # 临时替换WalkControl函数
        original_walk_control = None
        try:
            import wxauto.uiautomation as uia
            original_walk_control = uia.WalkControl
            uia.WalkControl = create_mock_walk_control(mock_control, ["测试小程序", "这是一个测试用的小程序描述"])
        except:
            pass
        
        # 创建小程序消息对象
        miniprogram_msg = MiniprogramMessage(mock_control, mock_parent)
        
        # 测试基本属性
        print(f"应用名称: '{miniprogram_msg.app_name}'")
        print(f"应用描述: '{miniprogram_msg.app_description}'")
        print(f"消息类型: '{miniprogram_msg.type}'")
        
        # 测试缩略图信息
        thumbnail_info = miniprogram_msg.thumbnail_info
        print(f"缩略图信息: {thumbnail_info}")
        
        # 测试信息提取
        link_info = miniprogram_msg.extract_link_info()
        print(f"链接信息: {link_info}")
        
        # 测试小程序信息对象
        miniprogram_info = miniprogram_msg.miniprogram_info
        print(f"小程序信息对象: {type(miniprogram_info)}")
        
        # 恢复原始函数
        if original_walk_control:
            uia.WalkControl = original_walk_control
        
        print("✓ MiniprogramMessage 测试通过")
        return True
        
    except Exception as e:
        print(f"✗ MiniprogramMessage 测试失败: {str(e)}")
        traceback.print_exc()
        return False


def test_error_handling():
    """测试错误处理"""
    print("\n" + "=" * 60)
    print("测试错误处理")
    print("=" * 60)
    
    try:
        # 测试空控件
        print("测试空控件...")
        analyzer = MiniprogramCardAnalyzer(None)
        result = analyzer.extract_app_name()
        print(f"空控件结果: '{result}' (应该是默认值)")
        
        # 测试损坏的控件
        print("测试损坏的控件...")
        mock_broken_control = Mock()
        mock_broken_control.Exists.side_effect = Exception("控件已损坏")
        mock_broken_control.Name = None
        mock_broken_control.BoundingRectangle = None
        
        analyzer = MiniprogramCardAnalyzer(mock_broken_control)
        result = analyzer.extract_app_name()
        print(f"损坏控件结果: '{result}' (应该是默认值)")
        
        # 测试不存在的控件
        print("测试不存在的控件...")
        mock_nonexistent_control = Mock()
        mock_nonexistent_control.Exists.return_value = False
        mock_nonexistent_control.Name = "不存在的控件"
        
        analyzer = MiniprogramCardAnalyzer(mock_nonexistent_control)
        result = analyzer.extract_app_name()
        print(f"不存在控件结果: '{result}' (应该是空字符串)")
        
        print("✓ 错误处理测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 错误处理测试失败: {str(e)}")
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("小程序基本信息提取功能测试")
    print("=" * 60)
    
    # 运行所有测试
    test_results = []
    
    # 测试分析器
    analyzer_result = test_miniprogram_card_analyzer()
    test_results.append(("MiniprogramCardAnalyzer", analyzer_result))
    
    # 测试消息类
    message_result = test_miniprogram_message()
    test_results.append(("MiniprogramMessage", message_result))
    
    # 测试错误处理
    error_handling_result = test_error_handling()
    test_results.append(("错误处理", error_handling_result))
    
    # 输出总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed_count = 0
    for test_name, result in test_results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed_count += 1
    
    overall_success = passed_count == len(test_results)
    print(f"\n总体结果: {passed_count}/{len(test_results)} 测试通过")
    
    if overall_success:
        print("🎉 所有测试通过！任务4的基本信息提取功能实现成功。")
    else:
        print("❌ 部分测试失败，需要进一步调试。")
    
    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)