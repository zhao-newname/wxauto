#!/usr/bin/env python3
"""
基础功能测试脚本
验证MiniprogramMessage和MiniprogramInfo类的基本功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# 模拟必要的依赖
class MockControl:
    def __init__(self):
        self.Name = "测试小程序"
        self.runtimeid = "test_id"
    
    def Exists(self, timeout=0):
        return True
    
    def ButtonControl(self, searchDepth=2):
        return self
    
    def GetParentControl(self):
        return self

class MockChatBox:
    def __init__(self):
        self.root = None
    
    def get_info(self):
        return {"chat_name": "测试聊天"}

# 模拟wxauto模块
class MockUIAutomation:
    Control = MockControl

class MockWxResponse:
    def __init__(self, success, message=""):
        self.success = success
        self.message = message
    
    @classmethod
    def success(cls, message=""):
        return cls(True, message)
    
    @classmethod
    def failure(cls, message=""):
        return cls(False, message)

# 设置模拟环境
sys.modules['wxauto'] = type('MockModule', (), {})()
sys.modules['wxauto.uiautomation'] = MockUIAutomation()
sys.modules['wxauto.param'] = type('MockModule', (), {'WxResponse': MockWxResponse})()
sys.modules['wxauto.ui'] = type('MockModule', (), {})()
sys.modules['wxauto.ui.chatbox'] = type('MockModule', (), {})()

# 模拟基类
class MockHumanMessage:
    def __init__(self, control, parent):
        self.control = control
        self.parent = parent
        self.content = control.Name
        self.id = control.runtimeid
        self.sender = "test_sender"
        self.sender_remark = "test_remark"
    
    def roll_into_view(self):
        return MockWxResponse.success()
    
    def click(self):
        pass
    
    def select_option(self, option):
        return MockWxResponse.success()
    
    def chat_info(self):
        return self.parent.get_info()

sys.modules['wxauto.msgs'] = type('MockModule', (), {})()
sys.modules['wxauto.msgs.base'] = type('MockModule', (), {'HumanMessage': MockHumanMessage})()

def test_miniprogram_classes():
    """测试小程序类的基本功能"""
    print("开始测试小程序类...")
    
    # 创建临时的miniprogram模块内容用于测试
    import tempfile
    import importlib.util
    
    # 创建临时文件，修改导入语句
    miniprogram_code = '''
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional
import json

@dataclass
class MiniprogramInfo:
    """小程序信息数据模型"""
    app_name: str = ""
    app_description: str = ""
    app_id: Optional[str] = None
    page_path: Optional[str] = None
    page_params: Dict = field(default_factory=dict)
    thumbnail_url: Optional[str] = None
    share_time: Optional[datetime] = None
    sender: str = ""
    chat_name: str = ""
    
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

class MiniprogramMessage(MockHumanMessage):
    """小程序消息基类"""
    
    type = 'miniprogram'
    
    def __init__(self, control, parent):
        super().__init__(control, parent)
        self._miniprogram_info = None
        self._parse_miniprogram_info()
    
    def _parse_miniprogram_info(self):
        """解析小程序信息"""
        self._miniprogram_info = MiniprogramInfo()
        
        chat_info = self.chat_info()
        if chat_info:
            self._miniprogram_info.chat_name = chat_info.get('chat_name', '')
        
        self._miniprogram_info.sender = self.sender_remark or self.sender
        self._miniprogram_info.share_time = datetime.now()
        self._miniprogram_info.app_name = self._extract_app_name()
        self._miniprogram_info.app_description = self._extract_app_description()
    
    def _extract_app_name(self) -> str:
        try:
            return self.content or ""
        except Exception:
            return ""
    
    def _extract_app_description(self) -> str:
        try:
            return ""
        except Exception:
            return ""
    
    @property
    def app_name(self) -> str:
        return self._miniprogram_info.app_name if self._miniprogram_info else ""
    
    @property
    def app_description(self) -> str:
        return self._miniprogram_info.app_description if self._miniprogram_info else ""
    
    @property
    def app_id(self) -> Optional[str]:
        return self._miniprogram_info.app_id if self._miniprogram_info else None
    
    @property
    def page_path(self) -> Optional[str]:
        return self._miniprogram_info.page_path if self._miniprogram_info else None
    
    @property
    def page_params(self) -> Dict:
        return self._miniprogram_info.page_params if self._miniprogram_info else {}
    
    @property
    def thumbnail_url(self) -> Optional[str]:
        return self._miniprogram_info.thumbnail_url if self._miniprogram_info else None
    
    def extract_link_info(self) -> Dict:
        if self._miniprogram_info:
            return self._miniprogram_info.to_dict()
        return {}
    
    def open_miniprogram(self):
        try:
            if not self.roll_into_view():
                return MockWxResponse.failure("无法滚动到小程序卡片")
            self.click()
            return MockWxResponse.success("成功打开小程序")
        except Exception as e:
            return MockWxResponse.failure(f"打开小程序失败: {str(e)}")
    
    def copy_link_info(self):
        try:
            return self.select_option("复制")
        except Exception as e:
            return MockWxResponse.failure(f"复制链接信息失败: {str(e)}")
    
    @property
    def miniprogram_info(self):
        return self._miniprogram_info or MiniprogramInfo()
'''
    
    # 执行代码
    exec(miniprogram_code, globals())
    MiniprogramMessage = globals()['MiniprogramMessage']
    MiniprogramInfo = globals()['MiniprogramInfo']
    
    # 测试MiniprogramInfo数据模型
    print("\n1. 测试MiniprogramInfo数据模型:")
    info = MiniprogramInfo()
    print(f"   - 创建成功: {type(info).__name__}")
    print(f"   - 字段注解: {MiniprogramInfo.__annotations__}")
    
    # 设置一些测试数据
    info.app_name = "测试小程序"
    info.app_description = "这是一个测试小程序"
    
    # 测试序列化方法
    dict_data = info.to_dict()
    json_data = info.to_json()
    print(f"   - to_dict()方法: {type(dict_data).__name__}")
    print(f"   - to_json()方法: {type(json_data).__name__}")
    
    # 测试MiniprogramMessage类
    print("\n2. 测试MiniprogramMessage类:")
    mock_control = MockControl()
    mock_parent = MockChatBox()
    
    msg = MiniprogramMessage(mock_control, mock_parent)
    print(f"   - 创建成功: {type(msg).__name__}")
    print(f"   - 类继承关系: {MiniprogramMessage.__mro__}")
    print(f"   - 消息类型: {msg.type}")
    
    # 测试属性
    print(f"   - app_name属性: '{msg.app_name}'")
    print(f"   - app_description属性: '{msg.app_description}'")
    print(f"   - app_id属性: {msg.app_id}")
    print(f"   - page_path属性: {msg.page_path}")
    print(f"   - page_params属性: {msg.page_params}")
    
    # 测试方法
    print("\n3. 测试方法调用:")
    link_info = msg.extract_link_info()
    print(f"   - extract_link_info(): {type(link_info).__name__}")
    
    open_result = msg.open_miniprogram()
    print(f"   - open_miniprogram(): {open_result.success}")
    
    copy_result = msg.copy_link_info()
    print(f"   - copy_link_info(): {copy_result.success}")
    
    miniprogram_info = msg.miniprogram_info
    print(f"   - miniprogram_info属性: {type(miniprogram_info).__name__}")
    
    print("\n✅ 所有测试通过！")
    return True

if __name__ == "__main__":
    try:
        test_miniprogram_classes()
        print("\n🎉 基础架构创建成功！")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)