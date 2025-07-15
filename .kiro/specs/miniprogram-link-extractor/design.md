# 设计文档

## 概述

本设计文档描述了为wxauto库添加小程序链接抓取功能的技术实现方案。该功能将扩展现有的消息处理系统，添加新的小程序消息类型，并提供完整的小程序卡片信息提取和交互能力。

基于对微信UI自动化的研究，小程序卡片在微信中通常表现为特殊的富文本控件，包含多个子控件来展示小程序的名称、描述、图标等信息。我们将通过UI控件分析来识别和解析这些信息。

## 架构

### 核心组件架构

```
wxauto.msgs
├── miniprogram.py          # 小程序消息类型定义
├── msg.py                  # 消息解析器（扩展）
├── friend.py               # 好友小程序消息（扩展）
├── self.py                 # 自己小程序消息（扩展）
└── type.py                 # 消息类型（扩展）
```

### 消息处理流程

1. **消息识别阶段**：在`parse_msg_type`函数中添加小程序消息识别逻辑
2. **消息解析阶段**：创建专门的小程序消息类来解析卡片内容
3. **信息提取阶段**：从UI控件中提取小程序的技术参数和元数据
4. **交互处理阶段**：提供点击、复制、转发等交互功能

## 组件和接口

### 1. 小程序消息基类 (MiniprogramMessage)

```python
class MiniprogramMessage(HumanMessage):
    type = 'miniprogram'
    
    def __init__(self, control: uia.Control, parent: "ChatBox"):
        super().__init__(control, parent)
        self._parse_miniprogram_info()
    
    @property
    def app_name(self) -> str:
        """小程序名称"""
        
    @property
    def app_description(self) -> str:
        """小程序描述"""
        
    @property
    def app_id(self) -> str:
        """小程序AppID"""
        
    @property
    def page_path(self) -> str:
        """页面路径"""
        
    @property
    def thumbnail_url(self) -> str:
        """缩略图URL"""
        
    def extract_link_info(self) -> Dict:
        """提取完整的链接信息"""
        
    def open_miniprogram(self) -> WxResponse:
        """打开小程序"""
        
    def copy_link_info(self) -> WxResponse:
        """复制链接信息到剪贴板"""
```

### 2. 消息识别器扩展

在`wxauto/msgs/msg.py`中扩展`parse_msg_type`函数：

```python
def parse_msg_type(control: uia.Control, parent, attr: Literal['Self', 'Friend']):
    # 现有逻辑...
    
    # 小程序消息识别
    if _is_miniprogram_message(control):
        return getattr(msgtype, f'{attr}MiniprogramMessage')(control, parent)
    
    # 其他消息类型...
```

### 3. UI控件分析器

```python
class MiniprogramCardAnalyzer:
    """小程序卡片UI分析器"""
    
    def __init__(self, control: uia.Control):
        self.control = control
        
    def is_miniprogram_card(self) -> bool:
        """判断是否为小程序卡片"""
        
    def extract_app_name(self) -> str:
        """提取小程序名称"""
        
    def extract_description(self) -> str:
        """提取描述信息"""
        
    def extract_technical_params(self) -> Dict:
        """提取技术参数（AppID、页面路径等）"""
        
    def get_thumbnail_control(self) -> uia.Control:
        """获取缩略图控件"""
```

### 4. 批量处理工具

```python
class MiniprogramExtractor:
    """小程序消息批量提取器"""
    
    def __init__(self, chat_instance):
        self.chat = chat_instance
        
    def extract_all_miniprogram_messages(self) -> List[MiniprogramMessage]:
        """提取所有小程序消息"""
        
    def filter_by_app_name(self, app_name: str) -> List[MiniprogramMessage]:
        """按小程序名称过滤"""
        
    def export_to_json(self, filepath: str) -> WxResponse:
        """导出为JSON格式"""
```

## 数据模型

### 小程序信息数据结构

```python
@dataclass
class MiniprogramInfo:
    """小程序信息数据模型"""
    app_name: str                    # 小程序名称
    app_description: str             # 小程序描述
    app_id: Optional[str] = None     # 小程序AppID
    page_path: Optional[str] = None  # 页面路径
    page_params: Dict = field(default_factory=dict)  # 页面参数
    thumbnail_url: Optional[str] = None  # 缩略图URL
    share_time: Optional[datetime] = None  # 分享时间
    sender: str = ""                 # 发送者
    chat_name: str = ""              # 聊天名称
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        
    def to_json(self) -> str:
        """转换为JSON字符串"""
```

## 错误处理

### 异常类型定义

```python
class MiniprogramExtractionError(Exception):
    """小程序信息提取异常"""
    pass

class MiniprogramInteractionError(Exception):
    """小程序交互异常"""
    pass
```

### 错误处理策略

1. **UI控件不存在**：返回默认值或None，记录警告日志
2. **信息提取失败**：提供部分信息，标记提取状态
3. **交互操作失败**：返回WxResponse失败状态，包含错误描述
4. **批量处理异常**：跳过问题消息，继续处理其他消息

## 测试策略

### 单元测试

1. **消息识别测试**：测试不同类型小程序卡片的识别准确性
2. **信息提取测试**：验证各种小程序信息的提取正确性
3. **交互功能测试**：测试点击、复制等操作的可靠性
4. **边界条件测试**：测试异常情况和边界条件的处理

### 集成测试

1. **消息流程测试**：测试从消息获取到信息提取的完整流程
2. **批量处理测试**：测试大量消息的处理性能和准确性
3. **多种小程序测试**：测试不同类型小程序的兼容性
4. **UI变化适应测试**：测试对微信UI变化的适应能力

### 测试数据准备

1. **模拟小程序卡片**：创建不同类型的小程序卡片测试数据
2. **边界情况数据**：准备异常和边界情况的测试用例
3. **性能测试数据**：准备大量消息数据进行性能测试

## 实现注意事项

### UI控件识别策略

1. **多层次识别**：结合控件类型、名称、层级结构进行识别
2. **容错机制**：考虑微信版本差异和UI变化的影响
3. **性能优化**：避免过度的UI控件遍历，提高识别效率

### 信息提取技术

1. **正则表达式**：用于从控件名称中提取结构化信息
2. **UI自动化API**：利用Windows UI自动化API获取控件属性
3. **剪贴板操作**：通过右键菜单复制获取更多信息

### 兼容性考虑

1. **微信版本兼容**：支持微信3.9.X版本系列
2. **系统兼容**：确保在Windows 10/11上正常运行
3. **语言兼容**：支持中文和其他语言版本的微信

### 性能优化

1. **懒加载**：按需提取小程序信息，避免不必要的计算
2. **缓存机制**：缓存已提取的信息，避免重复处理
3. **异步处理**：对于批量操作，考虑异步处理提高效率