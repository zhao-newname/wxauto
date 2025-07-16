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
    
    # 小程序卡片高度特征 (像素)
    CARD_HEIGHT_RANGE = (70, 220)
    
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
            
            # 判断阈值：70分以上认为是小程序卡片
            is_miniprogram = score >= 70
            
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
                return ""
                
            # 从控件名称中提取应用名称
            if self.control.Name:
                # 小程序名称通常在控件名称的开头
                name = self.control.Name.strip()
                # 移除常见的后缀
                name = re.sub(r'\s*(小程序|miniprogram|weapp).*$', '', name, flags=re.IGNORECASE)
                return name.strip()
                
            return ""
            
        except Exception as e:
            wxlog.debug(f"提取应用名称异常: {str(e)}")
            return ""
    
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
        
        # 从控件中提取小程序名称（基础实现）
        self._miniprogram_info.app_name = self._extract_app_name()
        
        # 从控件中提取小程序描述（基础实现）
        self._miniprogram_info.app_description = self._extract_app_description()
    
    def _extract_app_name(self) -> str:
        """提取小程序名称
        
        Returns:
            str: 小程序名称，提取失败时返回空字符串
        """
        try:
            # 基础实现：从控件名称中提取
            # 实际实现将在后续任务中完善
            return self.content or ""
        except Exception:
            return ""
    
    def _extract_app_description(self) -> str:
        """提取小程序描述
        
        Returns:
            str: 小程序描述，提取失败时返回空字符串
        """
        try:
            # 基础实现：返回空字符串
            # 实际实现将在后续任务中完善
            return ""
        except Exception:
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
            # 滚动到视图中
            if not self.roll_into_view():
                return WxResponse.failure("无法滚动到小程序卡片")
            
            # 点击小程序卡片
            self.click()
            return WxResponse.success("成功打开小程序")
            
        except Exception as e:
            return WxResponse.failure(f"打开小程序失败: {str(e)}")
    
    def copy_link_info(self) -> WxResponse:
        """复制链接信息到剪贴板
        
        通过右键菜单复制小程序信息
        
        Returns:
            WxResponse: 操作结果
        """
        try:
            # 基础实现：使用右键菜单
            # 实际实现将在后续任务中完善
            return self.select_option("复制")
            
        except Exception as e:
            return WxResponse.failure(f"复制链接信息失败: {str(e)}")
    
    @property
    def miniprogram_info(self) -> MiniprogramInfo:
        """获取小程序信息对象
        
        Returns:
            MiniprogramInfo: 小程序信息数据模型实例
        """
        return self._miniprogram_info or MiniprogramInfo()