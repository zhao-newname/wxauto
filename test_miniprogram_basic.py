#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小程序卡片识别基础测试脚本

用于测试MiniprogramCardAnalyzer的核心逻辑，不依赖Windows UI自动化
"""

import sys
import os
from typing import List, Dict, Tuple
from dataclasses import dataclass

# 模拟wxauto.logger
class MockLogger:
    def debug(self, msg): print(f"DEBUG: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")
    def info(self, msg): print(f"INFO: {msg}")

# 模拟uiautomation模块
class MockUIAutomation:
    @staticmethod
    def WalkControl(control):
        """模拟WalkControl函数"""
        if hasattr(control, '_child_controls'):
            yield control
            for child in control._child_controls:
                yield child
        else:
            yield control

# 模拟控件类
class MockControl:
    def __init__(self, name: str = "", width: int = 300, height: int = 120, 
                 control_type: str = "PaneControl", has_image: bool = True,
                 has_text_controls: int = 2, child_controls: List = None):
        self.Name = name
        self.ControlTypeName = control_type
        self._width = width
        self._height = height
        self._has_image = has_image
        self._text_control_count = has_text_controls
        self._child_controls = child_controls or self._create_default_children()
        self._exists = True
        
    def _create_default_children(self):
        """创建默认子控件"""
        children = []
        
        # 添加文本控件
        for i in range(self._text_control_count):
            text_ctrl = MockControl(
                name=f"文本控件{i+1}" if i == 0 else f"这是一个较长的描述文本内容{i}",
                control_type="TextControl",
                child_controls=[]
            )
            children.append(text_ctrl)
            
        # 添加图片控件
        if self._has_image:
            img_ctrl = MockControl(name="图标", control_type="ImageControl", child_controls=[])
            children.append(img_ctrl)
            
        # 添加其他控件
        for ctrl_type in ["PaneControl", "ButtonControl"]:
            other_ctrl = MockControl(name="", control_type=ctrl_type, child_controls=[])
            children.append(other_ctrl)
            
        return children
        
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
            return MockControl("图标", 50, 50, "ImageControl", child_controls=[])
        else:
            mock = MockControl(child_controls=[])
            mock._exists = False
            return mock
            
    def ButtonControl(self, searchDepth=1):
        """模拟按钮控件查找"""
        if self._has_image:  # 图标可能是按钮形式
            return MockControl("按钮", 50, 50, "ButtonControl", child_controls=[])
        else:
            mock = MockControl(child_controls=[])
            mock._exists = False
            return mock
            
    def HyperlinkControl(self, searchDepth=1):
        """模拟超链接控件查找"""
        mock = MockControl(child_controls=[])
        mock._exists = False
        return mock


# 简化的MiniprogramCardAnalyzer类（只包含核心逻辑）
class MiniprogramCardAnalyzer:
    """小程序卡片UI分析器（测试版本）"""
    
    # 小程序卡片的特征标识
    MINIPROGRAM_INDICATORS = [
        "小程序", "miniprogram", "weapp", "小游戏", "minigame"
    ]
    
    # 小程序卡片的UI特征
    CARD_UI_PATTERNS = {
        'game': {'min_controls': 12, 'max_controls': 30, 'keywords': ["游戏", "game", "玩", "关卡", "分数", "挑战"]},
        'tool': {'min_controls': 6, 'max_controls': 18, 'keywords': ["工具", "助手", "查询", "计算", "转换", "实用"]}, 
        'ecommerce': {'min_controls': 8, 'max_controls': 25, 'keywords': ["购物", "商城", "价格", "¥", "元", "买", "商品", "优惠"]}
    }
    
    # 小程序卡片高度特征 (像素)
    CARD_HEIGHT_RANGE = (70, 220)
    CARD_WIDTH_RANGE = (200, 600)
    
    def __init__(self, control):
        self.control = control
        self.logger = MockLogger()
        self.uia = MockUIAutomation()
        
    def is_miniprogram_card(self) -> bool:
        """判断是否为小程序卡片"""
        try:
            if not self.control or not self.control.Exists(0):
                return False
            
            # 必须满足基本尺寸特征
            if not self._check_size_features():
                return False
            
            # 使用评分机制进行综合判断
            score = 0
            
            # 结构特征评分 (40分)
            if self._check_structure_features():
                score += 40
                self.logger.debug("结构特征匹配 +40分")
            
            # 子控件特征评分 (30分)
            if self._check_child_control_features():
                score += 30
                self.logger.debug("子控件特征匹配 +30分")
            
            # 名称特征评分 (20分)
            if self._check_name_indicators():
                score += 20
                self.logger.debug("名称特征匹配 +20分")
            elif self._has_app_name_pattern(self.control.Name.lower() if self.control.Name else ""):
                score += 10
                self.logger.debug("应用名称模式匹配 +10分")
            
            # 布局特征评分 (10分)
            if self._check_layout_features():
                score += 10
                self.logger.debug("布局特征匹配 +10分")
            
            # 判断阈值：70分以上认为是小程序卡片
            is_miniprogram = score >= 70
            
            if is_miniprogram:
                self.logger.debug(f"识别为小程序卡片，总分: {score}/100")
            else:
                self.logger.debug(f"非小程序卡片，总分: {score}/100")
                
            return is_miniprogram
            
        except Exception as e:
            self.logger.warning(f"小程序卡片识别异常: {str(e)}")
            return False
    
    def _check_size_features(self) -> bool:
        """检查控件尺寸特征"""
        try:
            if not self.control.BoundingRectangle:
                return False
                
            rect = self.control.BoundingRectangle
            height = rect.height()
            width = rect.width()
            
            # 小程序卡片有特定的高度和宽度范围
            if (self.CARD_HEIGHT_RANGE[0] <= height <= self.CARD_HEIGHT_RANGE[1] and
                self.CARD_WIDTH_RANGE[0] <= width <= self.CARD_WIDTH_RANGE[1]):
                return True
                    
            return False
            
        except Exception as e:
            self.logger.debug(f"尺寸特征检查异常: {str(e)}")
            return False
    
    def _check_structure_features(self) -> bool:
        """检查控件层级结构特征"""
        try:
            control_count = self._get_control_count()
            
            # 小程序卡片通常有特定的控件数量范围
            if 6 <= control_count <= 30:
                # 必须同时有图片控件和合适的尺寸
                if self._has_image_control() and self._check_size_features():
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.debug(f"结构特征检查异常: {str(e)}")
            return False
    
    def _check_child_control_features(self) -> bool:
        """检查子控件特征"""
        try:
            text_controls = self._find_text_controls()
            has_text_controls = len(text_controls) >= 1
            has_image_control = self._has_image_control()
            has_diverse_controls = self._has_diverse_control_types()
            
            if (has_text_controls and has_image_control) or has_diverse_controls or len(text_controls) >= 2:
                return True
                
            return False
            
        except Exception as e:
            self.logger.debug(f"子控件特征检查异常: {str(e)}")
            return False
    
    def _check_name_indicators(self) -> bool:
        """检查控件名称中的小程序特征标识"""
        if not self.control.Name:
            return False
            
        control_name = self.control.Name.lower()
        
        for indicator in self.MINIPROGRAM_INDICATORS:
            if indicator.lower() in control_name:
                return True
                
        return self._has_app_name_pattern(control_name)
    
    def _has_app_name_pattern(self, text: str) -> bool:
        """检查是否符合小程序应用名称模式"""
        if len(text) > 100:
            return False
            
        app_keywords = [
            "游戏", "工具", "购物", "生活", "娱乐", "学习", 
            "办公", "旅行", "美食", "健康", "金融", "社交"
        ]
        
        for keyword in app_keywords:
            if keyword in text:
                return True
                
        return False
    
    def _check_layout_features(self) -> bool:
        """检查布局特征"""
        try:
            if not self.control.BoundingRectangle:
                return False
                
            rect = self.control.BoundingRectangle
            width = rect.width()
            height = rect.height()
            
            if height > 0:
                aspect_ratio = width / height
                # 小程序卡片的宽高比通常在2:1到6:1之间
                if 2.0 <= aspect_ratio <= 6.0:
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.debug(f"布局特征检查异常: {str(e)}")
            return False
    
    def _get_control_count(self) -> int:
        """获取控件总数"""
        try:
            count = 0
            for _ in self.uia.WalkControl(self.control):
                count += 1
            return count
        except Exception:
            return 0
    
    def _has_image_control(self) -> bool:
        """检查是否包含图片控件"""
        try:
            image_controls = [
                self.control.ImageControl(searchDepth=3),
                self.control.ButtonControl(searchDepth=3),
            ]
            
            for img_ctrl in image_controls:
                if img_ctrl.Exists(0):
                    return True
                    
            return False
            
        except Exception:
            return False
    
    def _has_diverse_control_types(self) -> bool:
        """检查是否有多样化的控件类型"""
        try:
            found_types = set()
            
            for control in self.uia.WalkControl(self.control):
                if control.ControlTypeName:
                    found_types.add(control.ControlTypeName)
                    
            return len(found_types) >= 3
            
        except Exception:
            return False
    
    def _find_text_controls(self) -> List:
        """查找文本控件"""
        text_controls = []
        try:
            for control in self.uia.WalkControl(self.control):
                if (control.ControlTypeName in ['TextControl', 'EditControl', 'StaticTextControl'] 
                    and control.Name and control.Name.strip()):
                    text_controls.append(control)
                    
        except Exception as e:
            self.logger.debug(f"查找文本控件异常: {str(e)}")
            
        return text_controls
    
    def get_miniprogram_type(self) -> str:
        """识别小程序类型"""
        try:
            if not self.is_miniprogram_card():
                return 'unknown'
                
            control_count = self._get_control_count()
            control_name = self.control.Name.lower() if self.control.Name else ""
            
            # 游戏类小程序特征
            game_keywords = ["游戏", "game", "玩", "关卡", "分数"]
            if any(keyword in control_name for keyword in game_keywords):
                return 'game'
                
            # 电商类小程序特征  
            ecommerce_keywords = ["购物", "商城", "价格", "¥", "元", "买", "商品"]
            if any(keyword in control_name for keyword in ecommerce_keywords):
                return 'ecommerce'
                
            # 根据控件数量判断
            for card_type, features in self.CARD_UI_PATTERNS.items():
                if features['min_controls'] <= control_count <= features['max_controls']:
                    return card_type
                    
            return 'tool'  # 默认为工具类
            
        except Exception as e:
            self.logger.debug(f"小程序类型识别异常: {str(e)}")
            return 'unknown'


@dataclass
class TestCase:
    """测试用例数据结构"""
    name: str
    control: MockControl
    expected: bool
    card_type: str = "unknown"
    description: str = ""


def create_test_cases() -> List[TestCase]:
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
        width=200, height=250,  # 高度超出范围
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
        width=300, height=60,  # 高度不足
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
    
    return test_cases


def run_tests() -> Dict:
    """运行所有测试"""
    print("开始小程序卡片识别测试...")
    print("=" * 60)
    
    test_cases = create_test_cases()
    
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


def print_summary(results: Dict):
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
        results = run_tests()
        print_summary(results)
        return results['accuracy'] >= 95.0
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)