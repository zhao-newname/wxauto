# 小程序URL提取功能使用说明

## 功能概述

本功能可以从微信聊天记录中提取小程序消息，并尝试获取小程序的URL链接信息。

## 核心功能

### 1. 小程序消息识别和提取
- 自动识别聊天中的小程序卡片消息
- 提取小程序名称、描述、发送者等基本信息
- 支持批量处理多条小程序消息

### 2. 小程序URL提取
- 点击小程序卡片打开小程序
- 自动点击右上角"..."菜单按钮
- 查找并点击"复制链接"选项
- 获取复制到剪贴板的URL信息

### 3. 数据导出和统计
- 支持将提取结果导出为JSON格式
- 提供小程序消息统计信息
- 支持按应用名称、发送者等条件过滤

## 使用方法

### 快速测试
```python
from wxauto import WeChat

# 连接微信
wx = WeChat()

# 获取小程序消息
messages = wx.GetMiniprogramMessages()
print(f"找到 {len(messages)} 条小程序消息")

# 提取第一条消息的链接
if messages:
    msg = messages[0]
    result = msg.copy_link_info()
    if result.success:
        print("链接提取成功！")
        print(result.data['copied_content'])
```

### 使用提供的脚本

1. **核心功能验证**
   ```bash
   python verify_miniprogram.py
   ```

2. **点击功能测试**
   ```bash
   python test_click_miniprogram.py
   ```

3. **复制链接测试**
   ```bash
   python test_copy_link.py
   ```

4. **完整URL提取**
   ```bash
   python get_miniprogram_link.py
   ```

## API参考

### Chat类新增方法

#### GetMiniprogramMessages(use_cache=True)
获取当前聊天窗口的所有小程序消息
- `use_cache`: 是否使用缓存，默认True
- 返回: `List[MiniprogramMessage]`

#### FilterMiniprogramByApp(app_name, exact_match=False)
按小程序名称过滤消息
- `app_name`: 小程序名称
- `exact_match`: 是否精确匹配，默认False
- 返回: `List[MiniprogramMessage]`

#### GetMiniprogramStatistics()
获取小程序消息统计信息
- 返回: `Dict` 包含总数、热门应用、发送者等统计信息

#### ExportMiniprogramMessages(filepath, include_statistics=True)
导出小程序消息为JSON文件
- `filepath`: 导出文件路径
- `include_statistics`: 是否包含统计信息
- 返回: `WxResponse`

### WeChat类新增方法

WeChat类继承了Chat类的所有方法，并额外提供：

#### GetRecentMiniprogramMessages(days=7)
获取最近几天的小程序消息
- `days`: 天数，默认7天
- 返回: `List[MiniprogramMessage]`

#### FindDuplicateMiniprogram()
查找重复的小程序应用
- 返回: `Dict[str, List[MiniprogramMessage]]`

#### FilterMiniprogramBySender(sender, exact_match=False)
按发送者过滤小程序消息
- `sender`: 发送者名称
- `exact_match`: 是否精确匹配
- 返回: `List[MiniprogramMessage]`

### MiniprogramMessage类方法

#### extract_link_info()
提取小程序的完整信息
- 返回: `Dict` 包含应用名称、描述、AppID等信息

#### copy_link_info()
复制小程序链接信息到剪贴板
- 返回: `WxResponse` 包含操作结果和复制的内容

#### open_miniprogram()
打开小程序
- 返回: `WxResponse` 操作结果

## 当前状态

### ✅ 已实现功能
1. 小程序消息识别和提取
2. 基本信息提取（名称、描述、发送者）
3. 小程序卡片点击功能
4. 菜单按钮定位和点击
5. 数据导出和统计功能
6. 完整的API集成

### 🔧 需要优化的功能
1. "复制链接"按钮的精确定位
2. URL提取的准确性
3. 不同类型小程序的兼容性

### 📋 已验证的功能
- ✅ 微信连接正常
- ✅ 小程序消息识别正常
- ✅ 小程序卡片点击正常
- ✅ 菜单按钮点击正常
- ✅ 基本信息提取正常
- ✅ 数据导出功能正常

## 注意事项

1. **环境要求**
   - 微信客户端已打开并登录
   - 微信版本支持UI自动化
   - Python环境已安装wxauto

2. **使用限制**
   - 需要在包含小程序消息的聊天中使用
   - 自动化操作可能受微信版本影响
   - 建议在测试环境中使用

3. **最佳实践**
   - 使用前先运行验证脚本确认功能正常
   - 批量操作时注意添加适当延迟
   - 定期清理缓存以获取最新数据

## 示例输出

```json
{
  "export_info": {
    "export_time": "2025-07-18T17:37:23",
    "total_messages": 1,
    "chat_name": "测试聊天"
  },
  "messages": [
    {
      "app_name": "快团团",
      "app_description": "新鲜下树，咔嚓一口冰糖脆",
      "sender": "self",
      "message_type": "SelfMiniprogramMessage",
      "share_time": "2025-07-18T17:37:23"
    }
  ],
  "statistics": {
    "total_count": 1,
    "friend_messages": 0,
    "self_messages": 1,
    "unique_apps": 1
  }
}
```

## 技术实现

本功能基于wxauto框架实现，主要技术点包括：
- UI自动化控件识别
- 小程序卡片特征分析
- 鼠标点击和菜单操作
- 剪贴板内容获取
- 数据序列化和导出

## 更新日志

- 2025-07-18: 完成基础功能实现和API集成
- 2025-07-18: 修复点击定位问题
- 2025-07-18: 优化复制链接功能