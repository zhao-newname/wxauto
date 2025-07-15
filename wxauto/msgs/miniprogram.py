"""
小程序消息类型定义和数据模型

本模块提供小程序消息的基础架构，包括：
- MiniprogramMessage: 小程序消息基类
- MiniprogramInfo: 小程序信息数据模型
"""

from .base import HumanMessage
from wxauto.param import WxResponse
from wxauto import uiautomation as uia
from typing import Dict, Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime
import json

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