#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小程序卡片识别测试脚本

用于测试MiniprogramCardAnalyzer的识别准确性，验证：
1. 能够正确识别至少3种不同样式的小程序卡片
2. 对非小程序消息返回False，准确率达到95%以上
3. UI控件层级分析方法能够找到小程序卡片的关键子控件
"""

import sys
import os
import time
from typing import List, Dict, Tuple
from dataclasses import dataclass

# 添加项目路径到sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wxauto.msgs.miniprogram import MiniprogramCardAnalyzer
from wxauto import uiautomation as uia
from wxauto.logger import wxlog


@dataclass
class TestCase:
    """测试用例数据结构"""
    name: str
    control: uia.Control
    expected: bool
    card_type: str = "unknown"
    description: str = ""


class MockControl:
    """模拟UI控件类，用于测试"""
    
    def __init__(self, name: str = "", width: int = 300, height: int = 120, 
                 control_type: str = "PaneControl", has_image: bool = True,
                 has_text_controls: int = 2, child_controls: List = None):
        self.Name = name
        self.ControlTypeName = control_type
        self._width = width
        self._height = height
        self._has_image = has_image
        self._text_control_count = has_text_controls
        self._child_controls = child_controls or []
        self._exists = True
        
    def Exists(self, timeout=0):
        return self._exists
        
    @property
    def BoundingRectangle(self):
        """模拟边界矩形"""
        class MockRect:
            def __init__(self, w, h):
                self.left = 100
                self.top = 100
                self.right = 100 + w
                self.bottom = 100 + h
                
            def width(self):
                return self.right - self.left
                
            def height(self):
                return self.bottom - self.top
                
        return MockRect(self._width, self._height)
    
    def ImageControl(self, searchDepth=1):
        """模拟图片控件查找"""
        if self._has_image:
            return MockControl("图标", 50, 50, "ImageControl")
        else:
            mock = MockControl()
            mock._exists = False
            return mock
            
    def ButtonControl(self, searchDepth=1):
        """模拟按钮控件查找"""
        if self._has_image:  # 图标可能是按钮形式
            return MockControl("按钮", 50, 50, "ButtonControl")
        else:
            mock = MockControl()
            mock._exists = False
            return mock
            
    def HyperlinkControl(self, searchDepth=1):
        """模拟超链接控件查找"""
        mock = MockControl()
        mock._exists = False
        return mock


def create_mock_walk_control(control, child_controls=None):
    """模拟WalkControl函数"""
    if child_controls is None:
        # 默认子控件
        child_controls = []
        
        # 添加文本控件
        for i in range(control._text_control_count):
            text_ctrl = MockControl(
                name=f"文本控件{i+1}" if i == 0 else f"这是一个较长的描述文本内容{i}",
                control_type="TextControl"
            )
            child_controls.append(text_ctrl)
            
        # 添加图片控件
        if control._has_image:
            img_ctrl = MockControl(name="图标", control_type="ImageControl")
            child_controls.append(img_ctrl)
            
        # 添加其他控件
        for ctrl_type in ["PaneControl", "ButtonControl"]:
            other_ctrl = MockControl(name="", control_type=ctrl_type)
            child_controls.append(other_ctrl)
    
    # 返回所有控件（包括父控件）
    yield control
    for child in child_controls:
        yield child


class MiniprogramRecognitionTester:
    """小程序识别测试器"""
    
    def __init__(self):
        self.test_cases = []
        self.results = []
        
    def create_test_cases(self) -> List[TestCase]:
        """创建测试用例"""
        test_cases = []
        
        # === 小程序卡片测试用例 (应该识别为True) ===
        
        # 1. 游戏类小程序
        game_control = MockControl(
            name="跳一跳小游戏 - 微信小程序",
            width=350, height=120,
            has_image=True,
            has_text_controls=3
        )
        test_cases.append(TestCase(
            name="游戏类小程序",
            control=game_control,
            expected=True,
            card_type="game",
            description="包含游戏关键词的小程序卡片"
        ))
        
        # 2. 工具类小程序
        tool_control = MockControl(
            name="实用工具助手",
            width=320, height=100,
            has_image=True,
            has_text_controls=2
        )
        test_cases.append(TestCase(
            name="工具类小程序",
            control=tool_control,
            expected=True,
            card_type="tool",
            description="工具类小程序卡片"
        ))
        
        # 3. 电商类小程序
        ecommerce_control = MockControl(
            name="购物商城 优惠价格¥99",
            width=380, height=140,
            has_image=True,
            has_text_controls=4
        )
        test_cases.append(TestCase(
            name="电商类小程序",
            control=ecommerce_control,
            expected=True,
            card_type="ecommerce",
            description="包含购物和价格信息的小程序卡片"
        ))
        
        # 4. 标准小程序卡片
        standard_control = MockControl(
            name="生活服务小程序",
            width=300, height=110,
            has_image=True,
            has_text_controls=2
        )
        test_cases.append(TestCase(
            name="标准小程序卡片",
            control=standard_control,
            expected=True,
            card_type="tool",
            description="标准的小程序卡片"
        ))
        
        # 5. 带明确小程序标识的卡片
        explicit_control = MockControl(
            name="天气查询 小程序",
            width=310, height=105,
            has_image=True,
            has_text_controls=2
        )
        test_cases.append(TestCase(
            name="明确标识小程序",
            control=explicit_control,
            expected=True,
            card_type="tool",
            description="包含明确小程序标识的卡片"
        ))
        
        # === 非小程序消息测试用例 (应该识别为False) ===
        
        # 6. 普通文本消息
        text_control = MockControl(
            name="这是一条普通的文本消息",
            width=200, height=30,
            has_image=False,
            has_text_controls=1
        )
        test_cases.append(TestCase(
            name="普通文本消息",
            control=text_control,
            expected=False,
            description="普通的文本消息，不是小程序卡片"
        ))
        
        # 7. 图片消息
        image_msg_control = MockControl(
            name="[图片]",
            width=200, height=200,
            has_image=True,
            has_text_controls=0
        )
        test_cases.append(TestCase(
            name="图片消息",
            control=image_msg_control,
            expected=False,
            description="图片消息，尺寸不符合小程序卡片特征"
        ))
        
        # 8. 链接分享（非小程序）
        link_control = MockControl(
            name="网页链接分享 - 新闻标题",
            width=300, height=80,
            has_image=True,
            has_text_controls=2
        )
        test_cases.append(TestCase(
            name="网页链接分享",
            control=link_control,
            expected=False,
            description="普通网页链接分享，高度不足"
        ))
        
        # 9. 文件消息
        file_control = MockControl(
            name="文档.pdf",
            width=250, height=60,
            has_image=False,
            has_text_controls=1
        )
        test_cases.append(TestCase(
            name="文件消息",
            control=file_control,
            expected=False,
            description="文件消息，缺少图片控件且尺寸不符"
        ))
        
        # 10. 语音消息
        voice_control = MockControl(
            name="语音消息 3\"",
            width=150, height=40,
            has_image=False,
            has_text_controls=1
        )
        test_cases.append(TestCase(
            name="语音消息",
            control=voice_control,
            expected=False,
            description="语音消息，尺寸和特征都不符合"
        ))
        
        # 11. 视频消息
        video_control = MockControl(
            name="[视频]",
            width=300, height=200,
            has_image=True,
            has_text_controls=0
        )
        test_cases.append(TestCase(
            name="视频消息",
            control=video_control,
            expected=False,
            description="视频消息，缺少文本控件"
        ))
        
        # 12. 系统消息
        system_control = MockControl(
            name="系统消息：用户加入群聊",
            width=250, height=25,
            has_image=False,
            has_text_controls=1
        )
        test_cases.append(TestCase(
            name="系统消息",
            control=system_control,
            expected=False,
            description="系统消息，高度太小"
        ))
        
        # 13. 表情包消息
        emoji_control = MockControl(
            name="[表情]",
            width=120, height=120,
            has_image=True,
            has_text_controls=0
        )
        test_cases.append(TestCase(
            name="表情包消息",
            control=emoji_control,
            expected=False,
            description="表情包消息，宽度太小且缺少文本"
        ))
        
        # 14. 转账消息
        transfer_control = MockControl(
            name="转账消息",
            width=200, height=80,
            has_image=False,
            has_text_controls=1
        )
        test_cases.append(TestCase(
            name="转账消息",
            control=transfer_control,
            expected=False,
            description="转账消息，缺少图片控件且高度不足"
        ))
        
        # 15. 红包消息
        redpack_control = MockControl(
            name="红包消息",
            width=250, height=70,
            has_image=True,
            has_text_controls=1
        )
        test_cases.append(TestCase(
            name="红包消息",
            control=redpack_control,
            expected=False,
            description="红包消息，高度不足"
        ))
        
        return test_cases
    
    def run_tests(self) -> Dict:
        """运行所有测试"""
        print("开始小程序卡片识别测试...")
        print("=" * 60)
        
        # 创建测试用例
        test_cases = self.create_test_cases()
        
        # 临时替换WalkControl函数
        original_walk_control = uia.WalkControl
        uia.WalkControl = create_mock_walk_control
        
        try:
            results = {
                'total': len(test_cases),
                'correct': 0,
                'incorrect': 0,
                'accuracy': 0.0,
                'miniprogram_correct': 0,
                'miniprogram_total': 0,
                'non_miniprogram_correct': 0,
                'non_miniprogram_total': 0,
                'details': []
            }
            
            for i, test_case in enumerate(test_cases, 1):
                print(f"\n测试 {i}/{len(test_cases)}: {test_case.name}")
                print(f"描述: {test_case.description}")
                print(f"预期结果: {'小程序卡片' if test_case.expected else '非小程序卡片'}")
                
                # 创建分析器并测试
                analyzer = MiniprogramCardAnalyzer(test_case.control)
                actual_result = analyzer.is_miniprogram_card()
                
                print(f"实际结果: {'小程序卡片' if actual_result else '非小程序卡片'}")
                
                # 判断是否正确
                is_correct = actual_result == test_case.expected
                if is_correct:
                    results['correct'] += 1
                    print("✅ 测试通过")
                else:
                    results['incorrect'] += 1
                    print("❌ 测试失败")
                
                # 统计小程序和非小程序的准确率
                if test_case.expected:
                    results['miniprogram_total'] += 1
                    if is_correct:
                        results['miniprogram_correct'] += 1
                else:
                    results['non_miniprogram_total'] += 1
                    if is_correct:
                        results['non_miniprogram_correct'] += 1
                
                # 如果是小程序卡片，测试类型识别
                if actual_result and test_case.expected:
                    card_type = analyzer.get_miniprogram_type()
                    print(f"识别类型: {card_type}")
                    
                    # 测试关键控件查找
                    key_controls = analyzer.find_key_child_controls()
                    print(f"关键控件: {list(key_controls.keys())}")
                
                results['details'].append({
                    'name': test_case.name,
                    'expected': test_case.expected,
                    'actual': actual_result,
                    'correct': is_correct,
                    'description': test_case.description
                })
                
                print("-" * 40)
            
            # 计算准确率
            results['accuracy'] = (results['correct'] / results['total']) * 100
            
            return results
            
        finally:
            # 恢复原始函数
            uia.WalkControl = original_walk_control
    
    def print_summary(self, results: Dict):
        """打印测试摘要"""
        print("\n" + "=" * 60)
        print("测试摘要")
        print("=" * 60)
        
        print(f"总测试数: {results['total']}")
        print(f"正确数: {results['correct']}")
        print(f"错误数: {results['incorrect']}")
        print(f"总体准确率: {results['accuracy']:.1f}%")
        
        # 小程序识别准确率
        if results['miniprogram_total'] > 0:
            miniprogram_accuracy = (results['miniprogram_correct'] / results['miniprogram_total']) * 100
            print(f"小程序卡片识别准确率: {miniprogram_accuracy:.1f}% ({results['miniprogram_correct']}/{results['miniprogram_total']})")
        
        # 非小程序识别准确率
        if results['non_miniprogram_total'] > 0:
            non_miniprogram_accuracy = (results['non_miniprogram_correct'] / results['non_miniprogram_total']) * 100
            print(f"非小程序消息识别准确率: {non_miniprogram_accuracy:.1f}% ({results['non_miniprogram_correct']}/{results['non_miniprogram_total']})")
        
        # 验收标准检查
        print("\n验收标准检查:")
        if results['accuracy'] >= 95.0:
            print("✅ 总体准确率达到95%以上")
        else:
            print("❌ 总体准确率未达到95%")
        
        # 检查是否能识别3种不同类型的小程序
        miniprogram_cases = [detail for detail in results['details'] 
                           if detail['expected'] and detail['correct']]
        if len(miniprogram_cases) >= 3:
            print("✅ 能够正确识别至少3种不同样式的小程序卡片")
        else:
            print("❌ 未能正确识别足够的小程序卡片类型")
        
        print("\n详细错误:")
        for detail in results['details']:
            if not detail['correct']:
                print(f"❌ {detail['name']}: 预期 {detail['expected']}, 实际 {detail['actual']}")


def main():
    """主函数"""
    try:
        # 设置日志级别
        wxlog.setLevel('DEBUG')
        
        # 创建测试器并运行测试
        tester = MiniprogramRecognitionTester()
        results = tester.run_tests()
        
        # 打印摘要
        tester.print_summary(results)
        
        # 返回测试结果
        return results['accuracy'] >= 95.0
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)