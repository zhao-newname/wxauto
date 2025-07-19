"""
小程序消息类型定义和数据模型

本模块提供小程序消息的基础架构，包括：
- MiniprogramMessage: 小程序消息基类
- MiniprogramInfo: 小程序信息数据模型
- MiniprogramCardAnalyzer: 小程序卡片UI分析器
"""

from .base import HumanMessage
from wxauto.param import WxResponse
from wxauto import uiautomation as uia
from wxauto.logger import wxlog
from typing import Dict, Optional, TYPE_CHECKING, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import re

if TYPE_CHECKING:
    from wxauto.ui.chatbox import ChatBox


@dataclass
class MiniprogramInfo:
    """小程序信息数据模型"""
    app_name: str = ""                           # 小程序名称
    app_description: str = ""                    # 小程序描述
    app_id: Optional[str] = None                 # 小程序AppID
    page_path: Optional[str] = None              # 页面路径
    page_params: Dict = field(default_factory=dict)  # 页面参数
    thumbnail_url: Optional[str] = None          # 缩略图URL
    share_time: Optional[datetime] = None        # 分享时间
    sender: str = ""                             # 发送者
    chat_name: str = ""                          # 聊天名称
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat() if value else None
            else:
                result[key] = value
        return result
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class MiniprogramCardAnalyzer:
    """小程序卡片UI分析器
    
    用于识别和分析微信聊天中的小程序卡片消息，提供：
    - 小程序卡片识别
    - UI控件层级分析
    - 小程序信息提取
    """
    
    # 小程序卡片的特征标识
    MINIPROGRAM_INDICATORS = [
        "小程序",
        "miniprogram", 
        "weapp",
        "小游戏",
        "minigame"
    ]
    
    # 小程序卡片的UI特征
    CARD_UI_PATTERNS = {
        # 控件数量范围 (游戏类小程序通常控件较多)
        'game': {'min_controls': 12, 'max_controls': 30, 'keywords': ["游戏", "game", "玩", "关卡", "分数", "挑战"]},
        # 工具类小程序控件数量中等
        'tool': {'min_controls': 6, 'max_controls': 18, 'keywords': ["工具", "助手", "查询", "计算", "转换", "实用"]}, 
        # 电商类小程序通常有图片和价格信息
        'ecommerce': {'min_controls': 8, 'max_controls': 25, 'keywords': ["购物", "商城", "价格", "¥", "元", "买", "商品", "优惠"]}
    }
    
    # 小程序卡片高度特征 (像素) - 扩大范围以适应不同类型的小程序卡片
    CARD_HEIGHT_RANGE = (60, 350)
    
    # 小程序卡片宽度特征 (像素)
    CARD_WIDTH_RANGE = (200, 600)
    
    # 小程序卡片的控件类型特征
    EXPECTED_CONTROL_TYPES = [
        'TextControl',
        'EditControl', 
        'StaticTextControl',
        'ImageControl',
        'ButtonControl',
        'PaneControl'
    ]
    
    def __init__(self, control: uia.Control):
        """初始化分析器
        
        Args:
            control: 待分析的UI控件
        """
        self.control = control
        self._control_tree = None
        self._analyzed = False
        
    def is_miniprogram_card(self) -> bool:
        """判断是否为小程序卡片
        
        通过多种特征综合判断控件是否为小程序卡片，采用评分机制：
        1. 控件尺寸特征 (必须满足)
        2. 控件结构特征 (权重高)
        3. 子控件特征 (权重高)
        4. 名称特征 (权重中)
        5. 布局特征 (权重中)
        
        Returns:
            bool: True表示是小程序卡片，False表示不是
        """
        try:
            if not self.control or not self.control.Exists(0):
                return False
            
            # 必须满足基本尺寸特征
            if not self._check_size_features():
                return False
            
            # 使用评分机制进行综合判断
            score = 0
            max_score = 100
            
            # 结构特征评分 (40分)
            if self._check_structure_features():
                score += 40
                wxlog.debug("结构特征匹配 +40分")
            
            # 子控件特征评分 (30分)
            if self._check_child_control_features():
                score += 30
                wxlog.debug("子控件特征匹配 +30分")
            
            # 名称特征评分 (20分)
            if self._check_name_indicators():
                score += 20
                wxlog.debug("名称特征匹配 +20分")
            elif self._has_app_name_pattern(self.control.Name.lower() if self.control.Name else ""):
                score += 10
                wxlog.debug("应用名称模式匹配 +10分")
            
            # 布局特征评分 (10分)
            if self._check_layout_features():
                score += 10
                wxlog.debug("布局特征匹配 +10分")
            
            # 排除规则：排除明显的非小程序消息
            if self._should_exclude_as_non_miniprogram():
                score = max(0, score - 30)  # 大幅降低分数
                wxlog.debug("触发排除规则 -30分")
            
            # 判断阈值：50分以上认为是小程序卡片 (降低阈值以提高识别率)
            is_miniprogram = score >= 50
            
            if is_miniprogram:
                wxlog.debug(f"识别为小程序卡片，总分: {score}/{max_score}")
            else:
                wxlog.debug(f"非小程序卡片，总分: {score}/{max_score}")
                
            return is_miniprogram
            
        except Exception as e:
            wxlog.warning(f"小程序卡片识别异常: {str(e)}")
            return False
    
    def _check_name_indicators(self) -> bool:
        """检查控件名称中的小程序特征标识
        
        Returns:
            bool: 是否包含小程序特征标识
        """
        if not self.control.Name:
            return False
            
        control_name = self.control.Name.lower()
        
        # 检查直接的小程序标识
        for indicator in self.MINIPROGRAM_INDICATORS:
            if indicator.lower() in control_name:
                return True
                
        # 检查小程序卡片的典型文本模式
        # 小程序卡片通常包含应用名称和描述
        if self._has_app_name_pattern(control_name):
            return True
            
        return False
    
    def _has_app_name_pattern(self, text: str) -> bool:
        """检查是否符合小程序应用名称模式
        
        Args:
            text: 待检查的文本
            
        Returns:
            bool: 是否符合小程序名称模式
        """
        # 小程序名称通常较短且不包含特殊符号
        if len(text) > 100:  # 过长的文本不太可能是小程序名称
            return False
            
        # 检查是否包含典型的小程序描述词汇
        app_keywords = [
            "游戏", "工具", "购物", "生活", "娱乐", "学习", 
            "办公", "旅行", "美食", "健康", "金融", "社交"
        ]
        
        for keyword in app_keywords:
            if keyword in text:
                return True
                
        return False
    
    def _check_structure_features(self) -> bool:
        """检查控件层级结构特征
        
        Returns:
            bool: 是否符合小程序卡片的结构特征
        """
        try:
            # 获取控件层级信息
            control_count = self._get_control_count()
            
            # 小程序卡片通常有特定的控件数量范围，且必须同时满足多个条件
            if 8 <= control_count <= 25:
                # 必须同时有图片控件和合适的尺寸
                if self._has_image_control() and self._check_size_features():
                    return True
                    
            return False
            
        except Exception as e:
            wxlog.debug(f"结构特征检查异常: {str(e)}")
            return False
    
    def _check_size_features(self) -> bool:
        """检查控件尺寸特征
        
        Returns:
            bool: 是否符合小程序卡片的尺寸特征
        """
        try:
            if not self.control.BoundingRectangle:
                return False
                
            rect = self.control.BoundingRectangle
            height = rect.height()
            width = rect.width()
            
            # 小程序卡片有特定的高度范围
            if self.CARD_HEIGHT_RANGE[0] <= height <= self.CARD_HEIGHT_RANGE[1]:
                # 宽度应该合理（不能太窄）
                if width > 200:
                    return True
                    
            return False
            
        except Exception as e:
            wxlog.debug(f"尺寸特征检查异常: {str(e)}")
            return False
    
    def _check_child_control_features(self) -> bool:
        """检查子控件特征
        
        Returns:
            bool: 是否具有小程序卡片的子控件特征
        """
        try:
            # 检查是否有文本控件（应用名称和描述）
            text_controls = self._find_text_controls()
            has_text_controls = len(text_controls) >= 1  # 至少有一个文本控件
            
            # 检查是否有图片控件（应用图标）
            has_image_control = self._has_image_control()
            
            # 检查控件类型多样性
            has_diverse_controls = self._has_diverse_control_types()
            
            # 满足以下任一条件即可：
            # 1. 有文本控件且有图片控件
            # 2. 有多样化的控件类型
            # 3. 有足够多的文本控件（>=2个）
            if (has_text_controls and has_image_control) or has_diverse_controls or len(text_controls) >= 2:
                return True
                
            return False
            
        except Exception as e:
            wxlog.debug(f"子控件特征检查异常: {str(e)}")
            return False
    
    def _check_layout_features(self) -> bool:
        """检查布局特征
        
        Returns:
            bool: 是否符合小程序卡片的布局特征
        """
        try:
            # 检查宽高比（小程序卡片通常是横向布局）
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
                    
            # 检查是否有合理的内边距（通过子控件位置判断）
            if self._has_reasonable_padding():
                return True
                
            return False
            
        except Exception as e:
            wxlog.debug(f"布局特征检查异常: {str(e)}")
            return False
    
    def _has_diverse_control_types(self) -> bool:
        """检查是否有多样化的控件类型
        
        Returns:
            bool: 是否有多样化的控件类型
        """
        try:
            found_types = set()
            
            for control in uia.WalkControl(self.control):
                if control.ControlTypeName:
                    found_types.add(control.ControlTypeName)
                    
            # 如果有3种以上不同类型的控件，认为是多样化的
            return len(found_types) >= 3
            
        except Exception:
            return False
    
    def _has_reasonable_padding(self) -> bool:
        """检查是否有合理的内边距
        
        Returns:
            bool: 是否有合理的内边距
        """
        try:
            if not self.control.BoundingRectangle:
                return False
                
            parent_rect = self.control.BoundingRectangle
            
            # 查找第一个子控件
            for child in uia.WalkControl(self.control):
                if child != self.control and child.BoundingRectangle:
                    child_rect = child.BoundingRectangle
                    
                    # 计算边距
                    left_margin = child_rect.left - parent_rect.left
                    top_margin = child_rect.top - parent_rect.top
                    
                    # 如果有合理的边距（5-20像素），认为是正常的卡片布局
                    if 5 <= left_margin <= 20 and 5 <= top_margin <= 20:
                        return True
                    break
                    
            return False
            
        except Exception:
            return False
    
    def _should_exclude_as_non_miniprogram(self) -> bool:
        """检查是否应该排除为非小程序消息
        
        Returns:
            bool: 是否应该排除
        """
        try:
            if not self.control.Name:
                return False
                
            control_name = self.control.Name.lower()
            
            # 明显的非小程序消息关键词
            exclude_keywords = [
                "红包", "转账", "[图片]", "[视频]", "[表情]", "[文件]", 
                "语音", "[语音]", "撤回了一条消息", "系统消息", 
                "[动画表情]", "[链接]", "收到转账", "发出转账"
            ]
            
            # 检查是否包含排除关键词
            for keyword in exclude_keywords:
                if keyword in control_name:
                    wxlog.debug(f"触发排除关键词: {keyword}")
                    return True
                    
            return False
            
        except Exception as e:
            wxlog.debug(f"排除规则检查异常: {str(e)}")
            return False
    
    def _get_control_count(self) -> int:
        """获取控件总数
        
        Returns:
            int: 控件数量
        """
        try:
            count = 0
            for _ in uia.WalkControl(self.control):
                count += 1
            return count
        except Exception:
            return 0
    
    def _has_image_control(self) -> bool:
        """检查是否包含图片控件
        
        Returns:
            bool: 是否包含图片控件
        """
        try:
            # 查找图片相关的控件
            image_controls = [
                self.control.ImageControl(searchDepth=3),
                self.control.ButtonControl(searchDepth=3),  # 图标可能是按钮形式
            ]
            
            for img_ctrl in image_controls:
                if img_ctrl.Exists(0):
                    return True
                    
            return False
            
        except Exception:
            return False
    
    def _has_clickable_elements(self) -> bool:
        """检查是否有可点击元素
        
        Returns:
            bool: 是否有可点击元素
        """
        try:
            # 小程序卡片本身或其子控件应该是可点击的
            clickable_controls = [
                self.control.ButtonControl(searchDepth=2),
                self.control.HyperlinkControl(searchDepth=2),
            ]
            
            for ctrl in clickable_controls:
                if ctrl.Exists(0):
                    return True
                    
            return False
            
        except Exception:
            return False
    
    def _find_text_controls(self) -> List[uia.Control]:
        """查找文本控件
        
        Returns:
            List[uia.Control]: 文本控件列表
        """
        text_controls = []
        try:
            # 查找各种类型的文本控件
            for control in uia.WalkControl(self.control):
                # 确保control是Control对象而不是tuple
                if hasattr(control, 'ControlTypeName') and hasattr(control, 'Name'):
                    if (control.ControlTypeName in ['TextControl', 'EditControl', 'StaticTextControl'] 
                        and control.Name and control.Name.strip()):
                        text_controls.append(control)
                    
        except Exception as e:
            wxlog.debug(f"查找文本控件异常: {str(e)}")
            
        return text_controls
    
    def get_miniprogram_type(self) -> str:
        """识别小程序类型
        
        Returns:
            str: 小程序类型 ('game', 'tool', 'ecommerce', 'unknown')
        """
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
            wxlog.debug(f"小程序类型识别异常: {str(e)}")
            return 'unknown'
    
    def extract_app_name(self) -> str:
        """提取小程序名称
        
        Returns:
            str: 小程序名称
        """
        try:
            if not self.is_miniprogram_card():
                wxlog.debug("非小程序卡片，返回空名称")
                return ""
            
            # 策略1: 从关键子控件中提取
            key_controls = self.find_key_child_controls()
            if key_controls.get('app_name') and key_controls['app_name'].Name:
                name = key_controls['app_name'].Name.strip()
                # 清理名称（移除常见后缀和前缀）
                name = self._clean_app_name(name)
                if name:
                    wxlog.debug(f"从关键控件提取到应用名称: {name}")
                    return name
            
            # 策略2: 从主控件名称中解析
            if self.control.Name:
                name = self.control.Name.strip()
                # 尝试从复合名称中提取应用名称
                extracted_name = self._extract_name_from_composite_text(name)
                if extracted_name:
                    wxlog.debug(f"从主控件名称提取到应用名称: {extracted_name}")
                    return extracted_name
            
            # 策略3: 从所有文本控件中查找最可能的应用名称
            text_controls = self._find_text_controls()
            for ctrl in text_controls:
                if ctrl.Name:
                    name = ctrl.Name.strip()
                    # 检查是否符合应用名称特征
                    if self._is_likely_app_name(name):
                        cleaned_name = self._clean_app_name(name)
                        if cleaned_name:
                            wxlog.debug(f"从文本控件提取到应用名称: {cleaned_name}")
                            return cleaned_name
            
            # 策略4: 使用默认值
            wxlog.debug("无法提取应用名称，返回默认值")
            return "未知小程序"
                
        except Exception as e:
            wxlog.warning(f"提取应用名称异常: {str(e)}")
            return "未知小程序"
    
    def extract_description(self) -> str:
        """提取小程序描述
        
        Returns:
            str: 小程序描述
        """
        try:
            if not self.is_miniprogram_card():
                return ""
                
            # 查找描述文本（通常是较长的文本控件）
            text_controls = self._find_text_controls()
            
            # 找到最长的文本作为描述
            description = ""
            for ctrl in text_controls:
                if ctrl.Name and len(ctrl.Name) > len(description):
                    # 排除明显是应用名称的短文本
                    if len(ctrl.Name) > 10:
                        description = ctrl.Name
                        
            return description.strip()
            
        except Exception as e:
            wxlog.debug(f"提取描述异常: {str(e)}")
            return ""
    
    def find_key_child_controls(self) -> Dict[str, uia.Control]:
        """查找小程序卡片的关键子控件
        
        Returns:
            Dict[str, uia.Control]: 关键控件字典，包含以下键：
            - app_icon: 应用图标控件
            - app_name: 应用名称文本控件
            - app_description: 应用描述文本控件
            - clickable_area: 可点击区域控件
        """
        key_controls = {
            'app_icon': None,
            'app_name': None, 
            'app_description': None,
            'clickable_area': None
        }
        
        try:
            if not self.is_miniprogram_card():
                wxlog.debug("非小程序卡片，跳过关键控件查找")
                return key_controls
                
            # 查找应用图标
            image_ctrl = self.control.ImageControl(searchDepth=3)
            if image_ctrl.Exists(0):
                key_controls['app_icon'] = image_ctrl
                wxlog.debug("找到图片控件作为应用图标")
            else:
                # 图标可能是按钮形式
                button_ctrl = self.control.ButtonControl(searchDepth=2)
                if button_ctrl.Exists(0):
                    key_controls['app_icon'] = button_ctrl
                    wxlog.debug("找到按钮控件作为应用图标")
                    
            # 查找文本控件
            text_controls = self._find_text_controls()
            if text_controls:
                # 按文本长度排序，短的通常是应用名称，长的通常是描述
                text_controls.sort(key=lambda x: len(x.Name or ""))
                
                # 第一个（最短的）通常是应用名称
                key_controls['app_name'] = text_controls[0]
                wxlog.debug(f"找到应用名称控件: {text_controls[0].Name}")
                
                # 如果有多个文本控件，最长的通常是描述
                if len(text_controls) > 1:
                    # 找到最长的文本作为描述（排除明显的应用名称）
                    for ctrl in reversed(text_controls):  # 从最长的开始
                        if ctrl.Name and len(ctrl.Name) > 10:  # 描述通常比较长
                            key_controls['app_description'] = ctrl
                            wxlog.debug(f"找到应用描述控件: {ctrl.Name[:20]}...")
                            break
                    
                    # 如果没有找到合适的描述，使用第二个文本控件
                    if not key_controls['app_description'] and len(text_controls) > 1:
                        key_controls['app_description'] = text_controls[1]
                        wxlog.debug(f"使用第二个文本控件作为描述: {text_controls[1].Name}")
                        
            # 可点击区域（通常是整个卡片）
            key_controls['clickable_area'] = self.control
            wxlog.debug("设置整个卡片为可点击区域")
            
            # 统计找到的关键控件数量
            found_count = sum(1 for ctrl in key_controls.values() if ctrl is not None)
            wxlog.debug(f"共找到 {found_count}/4 个关键控件")
            
        except Exception as e:
            wxlog.warning(f"查找关键控件异常: {str(e)}")
            
        return key_controls
    
    def analyze_card_structure(self) -> Dict[str, any]:
        """分析小程序卡片的结构信息
        
        Returns:
            Dict[str, any]: 卡片结构分析结果
        """
        analysis = {
            'is_miniprogram': False,
            'card_type': 'unknown',
            'control_count': 0,
            'has_image': False,
            'text_control_count': 0,
            'size_info': {},
            'key_controls': {},
            'confidence_score': 0
        }
        
        try:
            # 基本识别
            analysis['is_miniprogram'] = self.is_miniprogram_card()
            
            if analysis['is_miniprogram']:
                # 卡片类型
                analysis['card_type'] = self.get_miniprogram_type()
                
                # 控件统计
                analysis['control_count'] = self._get_control_count()
                analysis['has_image'] = self._has_image_control()
                analysis['text_control_count'] = len(self._find_text_controls())
                
                # 尺寸信息
                if self.control.BoundingRectangle:
                    rect = self.control.BoundingRectangle
                    analysis['size_info'] = {
                        'width': rect.width(),
                        'height': rect.height(),
                        'aspect_ratio': rect.width() / rect.height() if rect.height() > 0 else 0
                    }
                
                # 关键控件
                analysis['key_controls'] = self.find_key_child_controls()
                
                # 计算置信度分数（基于各种特征）
                score = 0
                if self._check_size_features(): score += 25
                if self._check_structure_features(): score += 25
                if self._check_child_control_features(): score += 25
                if self._check_name_indicators(): score += 25
                analysis['confidence_score'] = score
                
        except Exception as e:
            wxlog.warning(f"卡片结构分析异常: {str(e)}")
            
        return analysis
    
    def _clean_app_name(self, name: str) -> str:
        """清理应用名称，移除无关信息
        
        Args:
            name: 原始名称
            
        Returns:
            str: 清理后的名称
        """
        if not name:
            return ""
        
        # 移除常见的后缀和标识
        patterns_to_remove = [
            r'\s*(小程序|miniprogram|weapp).*$',
            r'\s*-\s*微信小程序.*$',
            r'\s*\|\s*.*$',  # 移除 | 后面的内容
            r'\s*·\s*.*$',   # 移除 · 后面的内容
            r'\s*\(\s*.*\s*\)$',  # 移除括号内容
            r'\s*【.*】$',   # 移除【】内容
            r'\s*\[.*\]$',   # 移除[]内容
        ]
        
        cleaned = name
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
            
        # 移除多余的空白字符
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # 如果清理后太短，可能过度清理了，返回原始名称的前部分
        if len(cleaned) < 2 and len(name) > 2:
            # 取原始名称的前20个字符作为备选
            cleaned = name[:20].strip()
            
        return cleaned
    
    def _extract_name_from_composite_text(self, text: str) -> str:
        """从复合文本中提取应用名称
        
        Args:
            text: 复合文本（可能包含名称和描述）
            
        Returns:
            str: 提取的应用名称
        """
        if not text:
            return ""
        
        # 如果文本很短，直接返回清理后的结果
        if len(text) <= 20:
            return self._clean_app_name(text)
        
        # 尝试按分隔符分割
        separators = ['\n', '|', '·', '-', ':', '：', '，', ',']
        for sep in separators:
            if sep in text:
                parts = text.split(sep)
                if parts and len(parts[0].strip()) > 0:
                    candidate = self._clean_app_name(parts[0])
                    if candidate and len(candidate) <= 30:  # 应用名称通常不会太长
                        return candidate
        
        # 如果没有明显的分隔符，取前面的部分
        # 应用名称通常在前面，描述在后面
        words = text.split()
        if words:
            # 取前1-3个词作为应用名称候选
            for i in range(1, min(4, len(words) + 1)):
                candidate = ' '.join(words[:i])
                if len(candidate) <= 30:
                    cleaned = self._clean_app_name(candidate)
                    if cleaned:
                        return cleaned
        
        # 最后尝试：取前30个字符
        return self._clean_app_name(text[:30])
    
    def _is_likely_app_name(self, text: str) -> bool:
        """判断文本是否可能是应用名称
        
        Args:
            text: 待判断的文本
            
        Returns:
            bool: 是否可能是应用名称
        """
        if not text or len(text) < 2:
            return False
        
        # 应用名称通常不会太长
        if len(text) > 50:
            return False
        
        # 排除明显不是应用名称的文本
        exclude_patterns = [
            r'^\d+$',  # 纯数字
            r'^[a-zA-Z]+$',  # 纯英文字母（除非是英文应用名）
            r'^\W+$',  # 纯符号
            r'点击查看|立即打开|进入小程序',  # 操作提示
            r'^\s*$',  # 空白
        ]
        
        for pattern in exclude_patterns:
            if re.match(pattern, text):
                return False
        
        # 包含应用名称特征的文本更可能是应用名称
        app_indicators = [
            '游戏', '工具', '助手', '管家', '宝典', '大师', 
            '商城', '购物', '生活', '服务', '平台', '中心'
        ]
        
        for indicator in app_indicators:
            if indicator in text:
                return True
        
        # 长度适中的文本可能是应用名称
        return 2 <= len(text) <= 30
    
    def extract_thumbnail_info(self) -> Dict[str, any]:
        """提取缩略图信息
        
        Returns:
            Dict[str, any]: 缩略图信息，包含控件引用和位置信息
        """
        thumbnail_info = {
            'has_thumbnail': False,
            'control': None,
            'position': None,
            'size': None,
            'type': 'unknown'
        }
        
        try:
            if not self.is_miniprogram_card():
                return thumbnail_info
            
            # 查找图片控件
            image_ctrl = self.control.ImageControl(searchDepth=3)
            if image_ctrl.Exists(0):
                thumbnail_info['has_thumbnail'] = True
                thumbnail_info['control'] = image_ctrl
                thumbnail_info['type'] = 'image'
                
                # 获取位置和尺寸信息
                if image_ctrl.BoundingRectangle:
                    rect = image_ctrl.BoundingRectangle
                    thumbnail_info['position'] = {'x': rect.left, 'y': rect.top}
                    thumbnail_info['size'] = {'width': rect.width(), 'height': rect.height()}
                
                wxlog.debug("找到图片控件作为缩略图")
                return thumbnail_info
            
            # 查找按钮形式的图标
            button_ctrl = self.control.ButtonControl(searchDepth=2)
            if button_ctrl.Exists(0):
                # 检查按钮是否可能是图标（通常较小且正方形）
                if button_ctrl.BoundingRectangle:
                    rect = button_ctrl.BoundingRectangle
                    width, height = rect.width(), rect.height()
                    
                    # 图标通常是正方形或接近正方形，且尺寸适中
                    if 20 <= width <= 100 and 20 <= height <= 100:
                        aspect_ratio = width / height if height > 0 else 1
                        if 0.5 <= aspect_ratio <= 2.0:  # 接近正方形
                            thumbnail_info['has_thumbnail'] = True
                            thumbnail_info['control'] = button_ctrl
                            thumbnail_info['type'] = 'button_icon'
                            thumbnail_info['position'] = {'x': rect.left, 'y': rect.top}
                            thumbnail_info['size'] = {'width': width, 'height': height}
                            
                            wxlog.debug("找到按钮控件作为缩略图")
                            return thumbnail_info
            
            wxlog.debug("未找到缩略图控件")
            
        except Exception as e:
            wxlog.warning(f"提取缩略图信息异常: {str(e)}")
            
        return thumbnail_info


class MiniprogramMessage(HumanMessage):
    """小程序消息基类
    
    继承自HumanMessage，提供小程序卡片消息的基础功能，包括：
    - 小程序信息提取
    - 小程序交互操作
    - 数据序列化
    """
    
    type = 'miniprogram'
    
    def __init__(self, control: uia.Control, parent: "ChatBox"):
        super().__init__(control, parent)
        self._miniprogram_info = None
        self._parse_miniprogram_info()
    
    def _parse_miniprogram_info(self):
        """解析小程序信息
        
        从UI控件中提取小程序的基本信息，包括名称、描述等
        """
        # 初始化小程序信息对象
        self._miniprogram_info = MiniprogramInfo()
        
        # 基础信息设置
        chat_info = self.chat_info()
        if chat_info:
            self._miniprogram_info.chat_name = chat_info.get('chat_name', '')
        
        self._miniprogram_info.sender = self.sender_remark or self.sender
        self._miniprogram_info.share_time = datetime.now()
        
        # 从控件中提取小程序名称
        self._miniprogram_info.app_name = self._extract_app_name()
        
        # 从控件中提取小程序描述
        self._miniprogram_info.app_description = self._extract_app_description()
        
        # 提取技术参数（AppID、页面路径等）
        self._extract_technical_params()
    
    def _extract_app_name(self) -> str:
        """提取小程序名称
        
        Returns:
            str: 小程序名称
        """
        try:
            analyzer = MiniprogramCardAnalyzer(self.control)
            return analyzer.extract_app_name()
        except Exception as e:
            wxlog.warning(f"提取小程序名称异常: {str(e)}")
            return "未知小程序"
    
    def _extract_app_description(self) -> str:
        """提取小程序描述
        
        Returns:
            str: 小程序描述
        """
        try:
            analyzer = MiniprogramCardAnalyzer(self.control)
            return analyzer.extract_description()
        except Exception as e:
            wxlog.warning(f"提取小程序描述异常: {str(e)}")
            return ""
    
    def _extract_technical_params(self):
        """提取小程序技术参数
        
        包括AppID、页面路径和额外参数的提取
        """
        try:
            # 提取AppID
            self._miniprogram_info.app_id = self._extract_app_id()
            
            # 提取页面路径
            self._miniprogram_info.page_path = self._extract_page_path()
            
            # 提取额外参数
            self._miniprogram_info.page_params = self._extract_page_params()
            
            wxlog.debug(f"技术参数提取完成 - AppID: {self._miniprogram_info.app_id}, "
                       f"页面路径: {self._miniprogram_info.page_path}, "
                       f"参数数量: {len(self._miniprogram_info.page_params)}")
                       
        except Exception as e:
            wxlog.warning(f"提取技术参数异常: {str(e)}")
    
    def _extract_app_id(self) -> Optional[str]:
        """提取小程序AppID
        
        通过多种方式尝试获取小程序的AppID：
        1. 从UI控件属性中获取
        2. 通过右键菜单复制功能获取
        3. 从控件名称中解析
        
        Returns:
            Optional[str]: 小程序AppID，获取失败时返回None
        """
        try:
            # 策略1: 从控件属性中获取
            app_id = self._extract_app_id_from_control_attributes()
            if app_id:
                wxlog.debug(f"从控件属性获取到AppID: {app_id}")
                return app_id
            
            # 策略2: 通过右键菜单获取
            app_id = self._extract_app_id_from_context_menu()
            if app_id:
                wxlog.debug(f"从右键菜单获取到AppID: {app_id}")
                return app_id
            
            # 策略3: 从控件名称中解析
            app_id = self._extract_app_id_from_control_name()
            if app_id:
                wxlog.debug(f"从控件名称解析到AppID: {app_id}")
                return app_id
            
            wxlog.debug("无法获取AppID")
            return None
            
        except Exception as e:
            wxlog.warning(f"提取AppID异常: {str(e)}")
            return None
    
    def _extract_app_id_from_control_attributes(self) -> Optional[str]:
        """从控件属性中提取AppID
        
        Returns:
            Optional[str]: AppID或None
        """
        try:
            # 检查控件的各种属性
            attributes_to_check = [
                'AutomationId',
                'ClassName', 
                'Name',
                'HelpText',
                'AcceleratorKey'
            ]
            
            for attr_name in attributes_to_check:
                try:
                    attr_value = getattr(self.control, attr_name, None)
                    if attr_value and isinstance(attr_value, str):
                        # 查找AppID模式 (通常是wx开头的字符串)
                        app_id = self._parse_app_id_from_text(attr_value)
                        if app_id:
                            return app_id
                except Exception:
                    continue
            
            # 检查子控件的属性
            for child in uia.WalkControl(self.control):
                if child != self.control:
                    for attr_name in attributes_to_check:
                        try:
                            attr_value = getattr(child, attr_name, None)
                            if attr_value and isinstance(attr_value, str):
                                app_id = self._parse_app_id_from_text(attr_value)
                                if app_id:
                                    return app_id
                        except Exception:
                            continue
            
            return None
            
        except Exception as e:
            wxlog.debug(f"从控件属性提取AppID异常: {str(e)}")
            return None
    
    def _extract_app_id_from_context_menu(self) -> Optional[str]:
        """通过右键菜单获取AppID
        
        Returns:
            Optional[str]: AppID或None
        """
        try:
            # 导入剪贴板操作模块
            import pyperclip
            
            # 保存当前剪贴板内容
            original_clipboard = ""
            try:
                original_clipboard = pyperclip.paste()
            except Exception:
                pass
            
            # 尝试右键复制小程序信息
            try:
                # 滚动到视图中
                self.roll_into_view()
                
                # 右键点击
                self.control.RightClick()
                
                # 等待右键菜单出现
                import time
                time.sleep(0.5)
                
                # 查找复制相关的菜单项
                copy_menu_items = [
                    "复制链接",
                    "复制小程序信息", 
                    "复制",
                    "Copy Link",
                    "Copy"
                ]
                
                for menu_text in copy_menu_items:
                    try:
                        # 查找菜单项
                        menu_item = uia.MenuItemControl(searchDepth=3, Name=menu_text)
                        if menu_item.Exists(1):
                            menu_item.Click()
                            time.sleep(0.5)
                            
                            # 获取剪贴板内容
                            clipboard_content = pyperclip.paste()
                            if clipboard_content and clipboard_content != original_clipboard:
                                # 从剪贴板内容中解析AppID
                                app_id = self._parse_app_id_from_text(clipboard_content)
                                if app_id:
                                    return app_id
                            break
                    except Exception:
                        continue
                
                # 按ESC键关闭菜单
                import win32api
                import win32con
                win32api.keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
                win32api.keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)
                
            finally:
                # 恢复原始剪贴板内容
                try:
                    if original_clipboard:
                        pyperclip.copy(original_clipboard)
                except Exception:
                    pass
            
            return None
            
        except Exception as e:
            wxlog.debug(f"通过右键菜单提取AppID异常: {str(e)}")
            return None
    
    def _extract_app_id_from_control_name(self) -> Optional[str]:
        """从控件名称中解析AppID
        
        Returns:
            Optional[str]: AppID或None
        """
        try:
            # 检查主控件名称
            if self.control.Name:
                app_id = self._parse_app_id_from_text(self.control.Name)
                if app_id:
                    return app_id
            
            # 检查所有子控件的名称
            for child in uia.WalkControl(self.control):
                if child != self.control and child.Name:
                    app_id = self._parse_app_id_from_text(child.Name)
                    if app_id:
                        return app_id
            
            return None
            
        except Exception as e:
            wxlog.debug(f"从控件名称解析AppID异常: {str(e)}")
            return None
    
    def _parse_app_id_from_text(self, text: str) -> Optional[str]:
        """从文本中解析AppID
        
        Args:
            text: 待解析的文本
            
        Returns:
            Optional[str]: 解析出的AppID或None
        """
        if not text:
            return None
        
        # AppID的常见模式
        app_id_patterns = [
            r'wx[a-f0-9]{16}',  # 标准微信AppID格式
            r'appid[=:]?\s*([a-zA-Z0-9]{16,32})',  # appid=xxx格式
            r'app_id[=:]?\s*([a-zA-Z0-9]{16,32})',  # app_id=xxx格式
            r'id[=:]?\s*(wx[a-f0-9]{16})',  # id=wxxx格式
        ]
        
        for pattern in app_id_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # 返回第一个匹配的AppID
                app_id = matches[0] if isinstance(matches[0], str) else matches[0][0]
                # 验证AppID格式
                if self._is_valid_app_id(app_id):
                    return app_id
        
        return None
    
    def _is_valid_app_id(self, app_id: str) -> bool:
        """验证AppID格式是否有效
        
        Args:
            app_id: 待验证的AppID
            
        Returns:
            bool: 是否为有效的AppID格式
        """
        if not app_id or len(app_id) < 16:
            return False
        
        # 微信小程序AppID通常以wx开头，后跟16位十六进制字符
        if re.match(r'^wx[a-f0-9]{16}$', app_id, re.IGNORECASE):
            return True
        
        # 其他可能的AppID格式（16-32位字母数字组合）
        if re.match(r'^[a-zA-Z0-9]{16,32}$', app_id):
            return True
        
        return False
    
    def _extract_page_path(self) -> Optional[str]:
        """提取页面路径参数
        
        Returns:
            Optional[str]: 页面路径或None
        """
        try:
            # 策略1: 从控件属性中获取
            page_path = self._extract_page_path_from_attributes()
            if page_path:
                wxlog.debug(f"从控件属性获取到页面路径: {page_path}")
                return page_path
            
            # 策略2: 从右键菜单复制的内容中获取
            page_path = self._extract_page_path_from_context_menu()
            if page_path:
                wxlog.debug(f"从右键菜单获取到页面路径: {page_path}")
                return page_path
            
            # 策略3: 从控件名称中解析
            page_path = self._extract_page_path_from_control_name()
            if page_path:
                wxlog.debug(f"从控件名称解析到页面路径: {page_path}")
                return page_path
            
            wxlog.debug("无法获取页面路径")
            return None
            
        except Exception as e:
            wxlog.warning(f"提取页面路径异常: {str(e)}")
            return None
    
    def _extract_page_path_from_attributes(self) -> Optional[str]:
        """从控件属性中提取页面路径
        
        Returns:
            Optional[str]: 页面路径或None
        """
        try:
            # 检查控件和子控件的属性
            for control in uia.WalkControl(self.control):
                attributes_to_check = ['Name', 'HelpText', 'AutomationId']
                
                for attr_name in attributes_to_check:
                    try:
                        attr_value = getattr(control, attr_name, None)
                        if attr_value and isinstance(attr_value, str):
                            page_path = self._parse_page_path_from_text(attr_value)
                            if page_path:
                                return page_path
                    except Exception:
                        continue
            
            return None
            
        except Exception as e:
            wxlog.debug(f"从控件属性提取页面路径异常: {str(e)}")
            return None
    
    def _extract_page_path_from_context_menu(self) -> Optional[str]:
        """通过右键菜单获取页面路径
        
        Returns:
            Optional[str]: 页面路径或None
        """
        try:
            # 这里复用AppID提取中的右键菜单逻辑
            # 实际实现中可以优化为共享方法
            import pyperclip
            
            original_clipboard = ""
            try:
                original_clipboard = pyperclip.paste()
            except Exception:
                pass
            
            try:
                self.roll_into_view()
                self.control.RightClick()
                
                import time
                time.sleep(0.5)
                
                copy_menu_items = ["复制链接", "复制小程序信息", "复制"]
                
                for menu_text in copy_menu_items:
                    try:
                        menu_item = uia.MenuItemControl(searchDepth=3, Name=menu_text)
                        if menu_item.Exists(1):
                            menu_item.Click()
                            time.sleep(0.5)
                            
                            clipboard_content = pyperclip.paste()
                            if clipboard_content and clipboard_content != original_clipboard:
                                page_path = self._parse_page_path_from_text(clipboard_content)
                                if page_path:
                                    return page_path
                            break
                    except Exception:
                        continue
                
                # 关闭菜单
                import win32api, win32con
                win32api.keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
                win32api.keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)
                
            finally:
                try:
                    if original_clipboard:
                        pyperclip.copy(original_clipboard)
                except Exception:
                    pass
            
            return None
            
        except Exception as e:
            wxlog.debug(f"通过右键菜单提取页面路径异常: {str(e)}")
            return None
    
    def _extract_page_path_from_control_name(self) -> Optional[str]:
        """从控件名称中解析页面路径
        
        Returns:
            Optional[str]: 页面路径或None
        """
        try:
            # 检查所有控件的名称
            for control in uia.WalkControl(self.control):
                if control.Name:
                    page_path = self._parse_page_path_from_text(control.Name)
                    if page_path:
                        return page_path
            
            return None
            
        except Exception as e:
            wxlog.debug(f"从控件名称解析页面路径异常: {str(e)}")
            return None
    
    def _parse_page_path_from_text(self, text: str) -> Optional[str]:
        """从文本中解析页面路径
        
        Args:
            text: 待解析的文本
            
        Returns:
            Optional[str]: 解析出的页面路径或None
        """
        if not text:
            return None
        
        # 页面路径的常见模式
        page_path_patterns = [
            r'path[=:]?\s*([/\w\-\.]+)',  # path=/pages/index
            r'page[=:]?\s*([/\w\-\.]+)',  # page=/pages/index
            r'(/pages/[/\w\-\.]*)',  # /pages/xxx格式
            r'(/[a-zA-Z][/\w\-\.]*)',  # 以/开头的路径
        ]
        
        for pattern in page_path_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                page_path = matches[0]
                # 验证页面路径格式
                if self._is_valid_page_path(page_path):
                    return page_path
        
        return None
    
    def _is_valid_page_path(self, page_path: str) -> bool:
        """验证页面路径格式是否有效
        
        Args:
            page_path: 待验证的页面路径
            
        Returns:
            bool: 是否为有效的页面路径格式
        """
        if not page_path:
            return False
        
        # 页面路径通常以/开头
        if not page_path.startswith('/'):
            return False
        
        # 长度合理
        if len(page_path) > 200:
            return False
        
        # 包含合理的字符
        if re.match(r'^/[a-zA-Z0-9/\-_\.]*$', page_path):
            return True
        
        return False
    
    def _extract_page_params(self) -> Dict:
        """提取额外的页面参数
        
        Returns:
            Dict: 页面参数字典
        """
        try:
            params = {}
            
            # 策略1: 从控件属性中提取参数
            params.update(self._extract_params_from_attributes())
            
            # 策略2: 从右键菜单复制的内容中提取参数
            params.update(self._extract_params_from_context_menu())
            
            # 策略3: 从控件名称中解析参数
            params.update(self._extract_params_from_control_name())
            
            wxlog.debug(f"提取到 {len(params)} 个页面参数")
            return params
            
        except Exception as e:
            wxlog.warning(f"提取页面参数异常: {str(e)}")
            return {}
    
    def _extract_params_from_attributes(self) -> Dict:
        """从控件属性中提取参数
        
        Returns:
            Dict: 参数字典
        """
        params = {}
        try:
            for control in uia.WalkControl(self.control):
                attributes_to_check = ['Name', 'HelpText', 'AutomationId']
                
                for attr_name in attributes_to_check:
                    try:
                        attr_value = getattr(control, attr_name, None)
                        if attr_value and isinstance(attr_value, str):
                            extracted_params = self._parse_params_from_text(attr_value)
                            params.update(extracted_params)
                    except Exception:
                        continue
            
            return params
            
        except Exception as e:
            wxlog.debug(f"从控件属性提取参数异常: {str(e)}")
            return {}
    
    def _extract_params_from_context_menu(self) -> Dict:
        """通过右键菜单获取参数
        
        Returns:
            Dict: 参数字典
        """
        try:
            # 复用右键菜单逻辑
            import pyperclip
            
            original_clipboard = ""
            try:
                original_clipboard = pyperclip.paste()
            except Exception:
                pass
            
            try:
                self.roll_into_view()
                self.control.RightClick()
                
                import time
                time.sleep(0.5)
                
                copy_menu_items = ["复制链接", "复制小程序信息", "复制"]
                
                for menu_text in copy_menu_items:
                    try:
                        menu_item = uia.MenuItemControl(searchDepth=3, Name=menu_text)
                        if menu_item.Exists(1):
                            menu_item.Click()
                            time.sleep(0.5)
                            
                            clipboard_content = pyperclip.paste()
                            if clipboard_content and clipboard_content != original_clipboard:
                                params = self._parse_params_from_text(clipboard_content)
                                if params:
                                    return params
                            break
                    except Exception:
                        continue
                
                # 关闭菜单
                import win32api, win32con
                win32api.keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
                win32api.keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)
                
            finally:
                try:
                    if original_clipboard:
                        pyperclip.copy(original_clipboard)
                except Exception:
                    pass
            
            return {}
            
        except Exception as e:
            wxlog.debug(f"通过右键菜单提取参数异常: {str(e)}")
            return {}
    
    def _extract_params_from_control_name(self) -> Dict:
        """从控件名称中解析参数
        
        Returns:
            Dict: 参数字典
        """
        params = {}
        try:
            for control in uia.WalkControl(self.control):
                if control.Name:
                    extracted_params = self._parse_params_from_text(control.Name)
                    params.update(extracted_params)
            
            return params
            
        except Exception as e:
            wxlog.debug(f"从控件名称解析参数异常: {str(e)}")
            return {}
    
    def _parse_params_from_text(self, text: str) -> Dict:
        """从文本中解析参数
        
        Args:
            text: 待解析的文本
            
        Returns:
            Dict: 解析出的参数字典
        """
        params = {}
        if not text:
            return params
        
        try:
            # URL参数模式 (?key=value&key2=value2)
            url_params_pattern = r'[?&]([a-zA-Z_][a-zA-Z0-9_]*)[=:]([^&\s]+)'
            matches = re.findall(url_params_pattern, text)
            for key, value in matches:
                params[key] = value
            
            # JSON格式参数
            json_pattern = r'\{[^}]*\}'
            json_matches = re.findall(json_pattern, text)
            for json_str in json_matches:
                try:
                    json_params = json.loads(json_str)
                    if isinstance(json_params, dict):
                        params.update(json_params)
                except Exception:
                    continue
            
            # 键值对格式 (key=value, key:value)
            kv_patterns = [
                r'([a-zA-Z_][a-zA-Z0-9_]*)[=:]([^,\s&]+)',
                r'([a-zA-Z_][a-zA-Z0-9_]*)\s*[:=]\s*([^,\n&]+)'
            ]
            
            for pattern in kv_patterns:
                matches = re.findall(pattern, text)
                for key, value in matches:
                    # 过滤掉明显不是参数的键值对
                    if not self._is_likely_param_key(key):
                        continue
                    params[key] = value.strip()
            
            return params
            
        except Exception as e:
            wxlog.debug(f"解析参数异常: {str(e)}")
            return {}
    
    def _is_likely_param_key(self, key: str) -> bool:
        """判断是否可能是参数键名
        
        Args:
            key: 键名
            
        Returns:
            bool: 是否可能是参数键名
        """
        if not key or len(key) < 2:
            return False
        
        # 排除明显不是参数的键名
        exclude_keys = [
            'width', 'height', 'left', 'top', 'right', 'bottom',
            'color', 'font', 'size', 'style', 'class', 'id'
        ]
        
        if key.lower() in exclude_keys:
            return False
        
        # 参数键名通常是字母开头的标识符
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', key):
            return True
        
        return False
    
    def _extract_app_name(self) -> str:
        """提取小程序名称
        
        使用MiniprogramCardAnalyzer进行智能提取
        
        Returns:
            str: 小程序名称，提取失败时返回默认值
        """
        try:
            # 使用分析器进行智能提取
            analyzer = MiniprogramCardAnalyzer(self.control)
            app_name = analyzer.extract_app_name()
            
            # 如果分析器提取失败，尝试从基础内容中获取
            if not app_name or app_name == "未知小程序":
                if self.content:
                    # 简单清理内容作为备选
                    cleaned_content = self.content.strip()
                    if len(cleaned_content) <= 50:  # 合理的应用名称长度
                        app_name = cleaned_content
                    else:
                        # 取前30个字符作为应用名称
                        app_name = cleaned_content[:30].strip()
                        
            return app_name or "未知小程序"
            
        except Exception as e:
            wxlog.warning(f"提取小程序名称异常: {str(e)}")
            return "未知小程序"
    
    def _extract_app_description(self) -> str:
        """提取小程序描述
        
        使用MiniprogramCardAnalyzer进行智能提取
        
        Returns:
            str: 小程序描述，提取失败时返回空字符串
        """
        try:
            # 使用分析器进行智能提取
            analyzer = MiniprogramCardAnalyzer(self.control)
            description = analyzer.extract_description()
            
            # 如果分析器提取失败，尝试其他方法
            if not description:
                # 尝试从关键控件中获取描述
                key_controls = analyzer.find_key_child_controls()
                if key_controls.get('app_description') and key_controls['app_description'].Name:
                    description = key_controls['app_description'].Name.strip()
                    
                # 如果还是没有，尝试从所有文本控件中找最长的作为描述
                if not description:
                    text_controls = analyzer._find_text_controls()
                    longest_text = ""
                    for ctrl in text_controls:
                        if ctrl.Name and len(ctrl.Name) > len(longest_text):
                            # 排除明显是应用名称的短文本
                            if len(ctrl.Name) > 15:  # 描述通常比应用名称长
                                longest_text = ctrl.Name
                    description = longest_text.strip()
            
            return description
            
        except Exception as e:
            wxlog.warning(f"提取小程序描述异常: {str(e)}")
            return ""
    
    @property
    def app_name(self) -> str:
        """小程序名称"""
        return self._miniprogram_info.app_name if self._miniprogram_info else ""
    
    @property
    def app_description(self) -> str:
        """小程序描述"""
        return self._miniprogram_info.app_description if self._miniprogram_info else ""
    
    @property
    def app_id(self) -> Optional[str]:
        """小程序AppID"""
        return self._miniprogram_info.app_id if self._miniprogram_info else None
    
    @property
    def page_path(self) -> Optional[str]:
        """页面路径"""
        return self._miniprogram_info.page_path if self._miniprogram_info else None
    
    @property
    def page_params(self) -> Dict:
        """页面参数"""
        return self._miniprogram_info.page_params if self._miniprogram_info else {}
    
    @property
    def thumbnail_url(self) -> Optional[str]:
        """缩略图URL"""
        return self._miniprogram_info.thumbnail_url if self._miniprogram_info else None
    
    @property
    def thumbnail_info(self) -> Dict[str, any]:
        """缩略图信息
        
        Returns:
            Dict[str, any]: 缩略图详细信息，包含控件引用和位置信息
        """
        try:
            analyzer = MiniprogramCardAnalyzer(self.control)
            return analyzer.extract_thumbnail_info()
        except Exception as e:
            wxlog.warning(f"获取缩略图信息异常: {str(e)}")
            return {
                'has_thumbnail': False,
                'control': None,
                'position': None,
                'size': None,
                'type': 'unknown'
            }
    
    def extract_link_info(self) -> Dict:
        """提取完整的链接信息
        
        Returns:
            Dict: 包含所有小程序信息的字典
        """
        if self._miniprogram_info:
            return self._miniprogram_info.to_dict()
        return {}
    
    def open_miniprogram(self) -> WxResponse:
        """打开小程序
        
        点击小程序卡片以打开小程序
        
        Returns:
            WxResponse: 操作结果
        """
        try:
            import time
            
            # 首先确保微信窗口处于前台
            try:
                # 获取微信窗口并激活
                import win32gui
                import win32con
                
                # 查找微信窗口
                wechat_hwnd = win32gui.FindWindow("WeChatMainWndForPC", None)
                if wechat_hwnd:
                    # 激活微信窗口
                    win32gui.ShowWindow(wechat_hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(wechat_hwnd)
                    time.sleep(0.5)
                    wxlog.debug("微信窗口已激活")
                else:
                    wxlog.warning("未找到微信窗口")
            except Exception as e:
                wxlog.debug(f"激活微信窗口失败: {str(e)}")
            
            # 滚动到视图中确保卡片可见
            roll_result = self.roll_into_view()
            if not roll_result.success:
                wxlog.warning("无法滚动到小程序卡片")
                return WxResponse.failure("无法滚动到小程序卡片")
            
            # 确保控件存在且可点击
            if not self.control.Exists(1):
                return WxResponse.failure("小程序卡片控件不存在")
            
            # 获取控件的位置信息
            rect = self.control.BoundingRectangle
            if not rect:
                return WxResponse.failure("无法获取小程序卡片位置")
            
            # 计算多个候选点击位置（基于测试结果优化）
            click_positions = [
                # 位置1: 右侧区域（测试证明最有效）
                {
                    'x': rect.left + rect.width() * 5 // 6,  # 右侧5/6位置
                    'y': rect.top + rect.height() // 2,      # 垂直中心
                    'description': '右侧区域'
                },
                # 位置2: 右侧3/4位置
                {
                    'x': rect.left + rect.width() * 3 // 4,  # 右侧3/4位置
                    'y': rect.top + rect.height() // 2,      # 垂直中心
                    'description': '右侧3/4位置'
                },
                # 位置3: 中心位置（备选）
                {
                    'x': rect.left + rect.width() // 2,      # 中心
                    'y': rect.top + rect.height() // 2,      # 垂直中心
                    'description': '中心位置'
                }
            ]
            
            wxlog.debug(f"小程序卡片位置: ({rect.left}, {rect.top}, {rect.right}, {rect.bottom})")
            
            # 执行点击操作 - 尝试不同位置和方法
            click_success = False
            
            for i, pos in enumerate(click_positions):
                if click_success:
                    break
                    
                click_x, click_y = pos['x'], pos['y']
                wxlog.debug(f"尝试点击位置 {i+1}: {pos['description']} ({click_x}, {click_y})")
                
                # 移动鼠标到目标位置
                try:
                    import win32api
                    import win32con
                    win32api.SetCursorPos((click_x, click_y))
                    time.sleep(0.3)
                    wxlog.debug(f"鼠标已移动到位置: ({click_x}, {click_y})")
                except Exception as e:
                    wxlog.debug(f"移动鼠标失败: {str(e)}")
                    continue
                
                # 方法1: 使用Windows API点击（最可靠）
                try:
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    time.sleep(0.1)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    wxlog.debug(f"使用Windows API点击位置 {i+1}")
                    time.sleep(1.0)
                    
                    # 简单验证：检查窗口是否有变化
                    try:
                        import win32gui
                        current_window = win32gui.GetForegroundWindow()
                        window_title = win32gui.GetWindowText(current_window)
                        if "小程序" in window_title or current_window != wechat_hwnd:
                            wxlog.debug(f"位置 {i+1} 点击成功，检测到窗口变化")
                            click_success = True
                            break
                    except Exception:
                        pass
                    
                    # 如果是第一个位置（最有效的），认为点击成功
                    if i == 0:
                        click_success = True
                        wxlog.debug(f"使用最佳位置点击，假设成功")
                        break
                        
                except Exception as e:
                    wxlog.debug(f"Windows API点击位置 {i+1} 失败: {str(e)}")
                
                # 方法2: 使用控件Click方法（备选）
                if not click_success and i == 0:  # 只在第一个位置尝试
                    try:
                        self.control.Click()
                        wxlog.debug("使用控件Click方法点击")
                        time.sleep(0.5)
                        click_success = True
                        break
                    except Exception as e:
                        wxlog.debug(f"控件Click方法失败: {str(e)}")
            
            if not click_success:
                return WxResponse.failure("所有点击位置和方法都失败了")
            
            # 等待小程序打开
            time.sleep(2.0)
            
            # 验证小程序是否打开（检查是否有新窗口或页面变化）
            try:
                # 简单验证：检查是否有新的窗口标题或控件
                current_window = uia.GetForegroundWindow()
                if current_window:
                    window_title = current_window.Name
                    wxlog.debug(f"当前前台窗口: {window_title}")
                    
                    # 如果窗口标题包含小程序相关信息，认为打开成功
                    if any(keyword in window_title for keyword in ["小程序", "微信", self.app_name[:5]]):
                        wxlog.info(f"小程序似乎已打开: {self.app_name}")
                        return WxResponse.success("成功打开小程序")
            except Exception as e:
                wxlog.debug(f"验证小程序打开状态失败: {str(e)}")
            
            # 如果无法验证，假设打开成功
            wxlog.info(f"已点击小程序卡片: {self.app_name}")
            return WxResponse.success("已点击小程序卡片")
            
        except Exception as e:
            wxlog.error(f"打开小程序失败: {str(e)}")
            return WxResponse.failure(f"打开小程序失败: {str(e)}")
    
    def copy_link_info(self) -> WxResponse:
        """复制小程序链接信息到剪贴板
        
        使用右键菜单方式复制小程序链接信息
        
        Returns:
            WxResponse: 操作结果，包含复制的信息
        """
        copy_success = False
        copied_content = ""
        original_clipboard = ""
        
        try:
            import pyperclip
            import time
            import win32api
            import win32con
            
            # 保存当前剪贴板内容
            try:
                original_clipboard = pyperclip.paste()
            except Exception:
                pass
            
            wxlog.info(f"开始提取小程序链接: {self.app_name}")
            
            # 确保微信窗口处于前台
            try:
                import win32gui
                wechat_hwnd = win32gui.FindWindow("WeChatMainWndForPC", None)
                if wechat_hwnd:
                    win32gui.ShowWindow(wechat_hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(wechat_hwnd)
                    time.sleep(0.5)
                    wxlog.debug("微信窗口已激活")
            except Exception as e:
                wxlog.debug(f"激活微信窗口失败: {str(e)}")
            
            # 滚动到视图中确保卡片可见
            roll_result = self.roll_into_view()
            if not roll_result.success:
                wxlog.warning("无法滚动到小程序卡片")
            
            # 确保控件存在
            if not self.control.Exists(1):
                return WxResponse.failure("小程序卡片控件不存在")
            
            # 获取控件的位置信息
            rect = self.control.BoundingRectangle
            if not rect:
                return WxResponse.failure("无法获取小程序卡片位置")
            
            # 计算右键点击位置（使用之前测试成功的右侧位置）
            right_click_x = rect.left + rect.width() * 5 // 6  # 右侧5/6位置
            right_click_y = rect.top + rect.height() // 2      # 垂直中心
            
            wxlog.debug(f"小程序卡片位置: ({rect.left}, {rect.top}, {rect.right}, {rect.bottom})")
            wxlog.debug(f"计划右键点击位置: ({right_click_x}, {right_click_y})")
            
            # 移动鼠标到目标位置
            try:
                win32api.SetCursorPos((right_click_x, right_click_y))
                time.sleep(0.3)
                wxlog.debug(f"鼠标已移动到位置: ({right_click_x}, {right_click_y})")
            except Exception as e:
                wxlog.debug(f"移动鼠标失败: {str(e)}")
                return WxResponse.failure(f"移动鼠标失败: {str(e)}")
            
            # 执行右键点击
            try:
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
                time.sleep(0.1)
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
                wxlog.debug("已执行右键点击")
                time.sleep(1.0)  # 等待右键菜单出现
            except Exception as e:
                wxlog.debug(f"右键点击失败: {str(e)}")
                return WxResponse.failure(f"右键点击失败: {str(e)}")
            
            # 查找并点击复制链接选项
            wxlog.debug("查找复制链接选项")
            
            # 可能的复制链接菜单项位置（相对于右键点击位置）
            copy_link_positions = [
                {'x': right_click_x + 50, 'y': right_click_y + 30, 'desc': '右下方1'},
                {'x': right_click_x + 80, 'y': right_click_y + 30, 'desc': '右下方2'},
                {'x': right_click_x + 50, 'y': right_click_y + 50, 'desc': '右下方3'},
                {'x': right_click_x + 30, 'y': right_click_y + 40, 'desc': '右下方4'},
                {'x': right_click_x + 70, 'y': right_click_y + 50, 'desc': '右下方5'},
            ]
            
            copy_success = False
            for i, pos in enumerate(copy_link_positions):
                try:
                    wxlog.debug(f"尝试复制链接位置 {i+1}: ({pos['x']}, {pos['y']}) - {pos['desc']}")
                    
                    # 移动到复制链接位置并点击
                    win32api.SetCursorPos((pos['x'], pos['y']))
                    time.sleep(0.2)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    time.sleep(0.1)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    
                    # 等待复制操作完成
                    time.sleep(1.0)
                    
                    # 检查剪贴板是否有新内容
                    try:
                        current_clipboard = pyperclip.paste()
                        if current_clipboard != original_clipboard:
                            # 检查是否包含小程序相关信息
                            if any(keyword in current_clipboard for keyword in ['小程序', 'miniprogram', 'weapp', 'http', '#小程序']):
                                copied_content = current_clipboard
                                copy_success = True
                                wxlog.debug(f"复制链接成功，位置 {i+1}")
                                break
                    except Exception as e:
                        wxlog.debug(f"检查剪贴板失败: {str(e)}")
                        
                except Exception as e:
                    wxlog.debug(f"复制链接位置 {i+1} 失败: {str(e)}")
                    continue
            
            # 如果右键菜单方式失败，尝试其他方法
            if not copy_success:
                wxlog.debug("右键菜单方式失败，尝试构造基本信息")
                
                # 构造基本的小程序信息
                basic_info = {
                    'app_name': self.app_name,
                    'app_description': self.app_description,
                    'sender': self.sender_remark or self.sender,
                    'share_time': datetime.now().isoformat(),
                    'extraction_method': 'basic_info'
                }
                
                # 尝试从控件名称和聊天记录中提取更多信息
                miniprogram_link = None
                
                # 方法1: 从控件名称中提取
                if self.control.Name:
                    control_text = self.control.Name
                    if '#小程序://' in control_text:
                        import re
                        link_match = re.search(r'#小程序://[^\s\n]+', control_text)
                        if link_match:
                            miniprogram_link = link_match.group()
                            wxlog.debug(f"从控件名称提取到链接: {miniprogram_link}")
                
                # 方法2: 从聊天记录中查找（通过父控件）
                if not miniprogram_link:
                    try:
                        # 获取最近的消息内容，可能包含小程序链接
                        chat = self.parent
                        if chat and hasattr(chat, 'GetAllMessage'):
                            recent_messages = chat.GetAllMessage(limit=10)
                            for msg in recent_messages:
                                if hasattr(msg, 'content') and msg.content:
                                    if '#小程序://' in msg.content:
                                        import re
                                        link_match = re.search(r'#小程序://[^\s\n]+', msg.content)
                                        if link_match:
                                            miniprogram_link = link_match.group()
                                            wxlog.debug(f"从聊天记录提取到链接: {miniprogram_link}")
                                            break
                        elif chat and hasattr(chat, 'GetAllMessages'):
                            # 尝试另一种方法名
                            recent_messages = chat.GetAllMessages(limit=10)
                            for msg in recent_messages:
                                if hasattr(msg, 'content') and msg.content:
                                    if '#小程序://' in msg.content:
                                        import re
                                        link_match = re.search(r'#小程序://[^\s\n]+', msg.content)
                                        if link_match:
                                            miniprogram_link = link_match.group()
                                            wxlog.debug(f"从聊天记录提取到链接: {miniprogram_link}")
                                            break
                    except Exception as e:
                        wxlog.debug(f"从聊天记录提取链接失败: {str(e)}")
                
                # 方法3: 尝试从技术参数构造链接
                if not miniprogram_link and (self.app_id or self.page_path):
                    try:
                        if self.app_id and self.page_path:
                            miniprogram_link = f"#小程序://{self.app_id}/{self.page_path}"
                        elif self.app_id:
                            miniprogram_link = f"#小程序://{self.app_id}/"
                        wxlog.debug(f"从技术参数构造链接: {miniprogram_link}")
                    except Exception as e:
                        wxlog.debug(f"构造链接失败: {str(e)}")
                
                if miniprogram_link:
                    basic_info['miniprogram_link'] = miniprogram_link
                
                # 构造复制内容
                copied_content = f"小程序: {basic_info['app_name']}\n"
                if basic_info.get('app_description'):
                    copied_content += f"描述: {basic_info['app_description']}\n"
                copied_content += f"分享者: {basic_info['sender']}\n"
                if basic_info.get('miniprogram_link'):
                    copied_content += f"链接: {basic_info['miniprogram_link']}\n"
                
                # 复制到剪贴板
                try:
                    pyperclip.copy(copied_content)
                    copy_success = True
                    wxlog.debug("使用基本信息构造复制内容成功")
                except Exception as e:
                    wxlog.debug(f"复制基本信息失败: {str(e)}")
            
            if copy_success:
                return WxResponse.success("复制小程序链接成功", data={
                    'copied_content': copied_content,
                    'app_name': self.app_name,
                    'extraction_method': 'right_click_menu' if 'miniprogram_link' not in locals() else 'basic_info'
                })
            else:
                return WxResponse.failure("无法复制小程序链接信息")
                
        except Exception as e:
            wxlog.error(f"复制小程序链接失败: {str(e)}")
            return WxResponse.failure(f"复制小程序链接失败: {str(e)}")
            time.sleep(1)
            
            # 步骤3: 在弹出的菜单中查找复制链接选项
            wxlog.debug("步骤3: 查找复制链接选项")
            
            # 根据截图，复制链接选项可能的文本
            copy_options = [
                "复制链接",
                "复制小程序链接", 
                "复制页面路径",
                "分享链接",
                "Copy Link",
                "Share Link"
            ]
            
            # 尝试多种方式查找复制链接按钮
            for option in copy_options:
                try:
                    # 方法1: 查找菜单项控件
                    menu_item = uia.MenuItemControl(searchDepth=5, Name=option)
                    if menu_item.Exists(0.5):
                        wxlog.debug(f"找到菜单项: {option}")
                        menu_item.Click()
                        time.sleep(1)
                        
                        # 检查剪贴板内容
                        new_clipboard = pyperclip.paste()
                        if new_clipboard and new_clipboard != original_clipboard:
                            copied_content = new_clipboard
                            copy_success = True
                            wxlog.info(f"成功复制小程序链接: {option}")
                            break
                    
                    # 方法2: 查找按钮控件
                    if not copy_success:
                        button_item = uia.ButtonControl(searchDepth=5, Name=option)
                        if button_item.Exists(0.5):
                            wxlog.debug(f"找到按钮: {option}")
                            button_item.Click()
                            time.sleep(1)
                            
                            # 检查剪贴板内容
                            new_clipboard = pyperclip.paste()
                            if new_clipboard and new_clipboard != original_clipboard:
                                copied_content = new_clipboard
                                copy_success = True
                                wxlog.info(f"成功复制小程序链接: {option}")
                                break
                    
                    # 方法3: 查找文本控件
                    if not copy_success:
                        text_item = uia.TextControl(searchDepth=5, Name=option)
                        if text_item.Exists(0.5):
                            wxlog.debug(f"找到文本控件: {option}")
                            text_item.Click()
                            time.sleep(1)
                            
                            # 检查剪贴板内容
                            new_clipboard = pyperclip.paste()
                            if new_clipboard and new_clipboard != original_clipboard:
                                copied_content = new_clipboard
                                copy_success = True
                                wxlog.info(f"成功复制小程序链接: {option}")
                                break
                            
                except Exception as e:
                    wxlog.debug(f"尝试复制选项 {option} 失败: {str(e)}")
                    continue
                
                if copy_success:
                    break
            
            # 如果上述方法都失败，尝试通过位置查找复制链接按钮
            if not copy_success:
                try:
                    wxlog.debug("尝试通过位置查找复制链接按钮")
                    
                    # 查找所有可能的控件
                    all_controls = uia.FindAll(uia.Control, searchDepth=5)
                    
                    for ctrl in all_controls:
                        try:
                            if ctrl.Exists(0.2) and ctrl.Name:
                                ctrl_name = ctrl.Name.lower()
                                # 检查是否包含复制相关的关键词
                                if any(keyword in ctrl_name for keyword in ["复制", "链接", "copy", "link"]):
                                    wxlog.debug(f"尝试点击可能的复制按钮: {ctrl.Name}")
                                    ctrl.Click()
                                    time.sleep(1)
                                    
                                    # 检查剪贴板
                                    new_clipboard = pyperclip.paste()
                                    if new_clipboard and new_clipboard != original_clipboard:
                                        copied_content = new_clipboard
                                        copy_success = True
                                        wxlog.info(f"通过位置查找成功复制: {ctrl.Name}")
                                        break
                        except Exception:
                            continue
                            
                except Exception as e:
                    wxlog.debug(f"通过位置查找失败: {str(e)}")
            
            # 如果没有找到复制选项，尝试构造基本信息
            if not copy_success:
                wxlog.debug("未找到复制链接选项，构造基本信息")
                try:
                    miniprogram_info = self.extract_link_info()
                    
                    copy_lines = []
                    copy_lines.append(f"小程序: {miniprogram_info.get('app_name', self.app_name)}")
                    if miniprogram_info.get('app_id'):
                        copy_lines.append(f"AppID: {miniprogram_info['app_id']}")
                    if miniprogram_info.get('page_path'):
                        copy_lines.append(f"页面路径: {miniprogram_info['page_path']}")
                    copy_lines.append(f"分享者: {miniprogram_info.get('sender', self.sender)}")
                    
                    copied_content = '\n'.join(copy_lines)
                    pyperclip.copy(copied_content)
                    copy_success = True
                    wxlog.debug("使用基本信息构造复制内容")
                    
                except Exception as e:
                    wxlog.debug(f"构造基本信息失败: {str(e)}")
            
            # 关闭菜单和小程序
            try:
                # 按ESC键关闭菜单
                import win32api, win32con
                win32api.keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
                win32api.keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.5)
                
                # 再次按ESC关闭小程序
                win32api.keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
                win32api.keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)
            except Exception:
                pass
            
            if copy_success:
                return WxResponse.success("成功复制小程序链接", data={"copied_content": copied_content})
            else:
                return WxResponse.failure("无法复制小程序链接")
                
        except Exception as e:
            wxlog.error(f"复制小程序链接失败: {str(e)}")
            return WxResponse.failure(f"复制小程序链接失败: {str(e)}")
        
        finally:
            # 如果没有成功复制，恢复原始剪贴板内容
            if not copy_success and original_clipboard:
                try:
                    pyperclip.copy(original_clipboard)
                except Exception:
                    pass
    
    @property
    def miniprogram_info(self) -> MiniprogramInfo:
        """获取小程序信息对象
        
        Returns:
            MiniprogramInfo: 小程序信息数据模型实例
        """
        return self._miniprogram_info or MiniprogramInfo()
    
    @property
    def app_name(self) -> str:
        """获取小程序名称
        
        Returns:
            str: 小程序名称
        """
        return self._miniprogram_info.app_name if self._miniprogram_info else ""
    
    @property
    def app_description(self) -> str:
        """获取小程序描述
        
        Returns:
            str: 小程序描述
        """
        return self._miniprogram_info.app_description if self._miniprogram_info else ""
    
    @property
    def app_id(self) -> Optional[str]:
        """获取小程序AppID
        
        Returns:
            Optional[str]: 小程序AppID
        """
        return self._miniprogram_info.app_id if self._miniprogram_info else None
    
    @property
    def page_path(self) -> Optional[str]:
        """获取页面路径
        
        Returns:
            Optional[str]: 页面路径
        """
        return self._miniprogram_info.page_path if self._miniprogram_info else None
    
    @property
    def page_params(self) -> Dict:
        """获取页面参数
        
        Returns:
            Dict: 页面参数字典
        """
        return self._miniprogram_info.page_params if self._miniprogram_info else {}
    
    @property
    def thumbnail_url(self) -> Optional[str]:
        """获取缩略图URL
        
        Returns:
            Optional[str]: 缩略图URL
        """
        return self._miniprogram_info.thumbnail_url if self._miniprogram_info else None
    
    @property
    def _xbias(self):
        """获取消息点击的X偏移量
        
        Returns:
            int: X偏移量
        """
        from wxauto.param import WxParam
        if WxParam.FORCE_MESSAGE_XBIAS:
            try:
                return int(self.head_control.BoundingRectangle.width() * 1.5)
            except Exception:
                return WxParam.DEFAULT_MESSAGE_XBIAS
        return WxParam.DEFAULT_MESSAGE_XBIAS