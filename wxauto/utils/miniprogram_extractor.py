"""
小程序消息批量提取器

提供小程序消息的批量处理和过滤功能，包括：
- 批量提取小程序消息
- 按条件过滤小程序消息
- 数据导出和序列化
- 统计和分析功能
"""

from typing import List, Dict, Optional, Union, Callable
from wxauto.msgs.miniprogram import MiniprogramMessage, MiniprogramInfo
from wxauto.msgs.friend import FriendMiniprogramMessage
from wxauto.msgs.self import SelfMiniprogramMessage
from wxauto.param import WxResponse
from wxauto.logger import wxlog
import json
import os
from datetime import datetime, timedelta
from collections import Counter


class MiniprogramExtractor:
    """小程序消息批量提取器
    
    用于从聊天记录中批量提取和处理小程序消息，提供：
    - 批量提取功能
    - 条件过滤功能
    - 统计分析功能
    - 数据导出功能
    """
    
    def __init__(self, chat_instance):
        """初始化提取器
        
        Args:
            chat_instance: Chat或WeChat实例
        """
        self.chat = chat_instance
        self._cached_messages = None
        self._cache_timestamp = None
        self._cache_duration = 300  # 缓存5分钟
    
    def extract_all_miniprogram_messages(self, use_cache: bool = True) -> List[MiniprogramMessage]:
        """提取所有小程序消息
        
        Args:
            use_cache: 是否使用缓存，默认True
            
        Returns:
            List[MiniprogramMessage]: 小程序消息列表
        """
        try:
            # 检查缓存
            if use_cache and self._is_cache_valid():
                wxlog.debug("使用缓存的小程序消息")
                return self._cached_messages
            
            wxlog.debug("开始提取所有小程序消息")
            
            # 获取所有消息
            all_messages = self.chat.GetAllMessage()
            miniprogram_messages = []
            
            # 过滤小程序消息
            for msg in all_messages:
                if isinstance(msg, (MiniprogramMessage, FriendMiniprogramMessage, SelfMiniprogramMessage)):
                    miniprogram_messages.append(msg)
            
            # 更新缓存
            self._cached_messages = miniprogram_messages
            self._cache_timestamp = datetime.now()
            
            wxlog.debug(f"提取到 {len(miniprogram_messages)} 条小程序消息")
            return miniprogram_messages
            
        except Exception as e:
            wxlog.warning(f"提取小程序消息异常: {str(e)}")
            return []
    
    def filter_by_app_name(self, app_name: str, exact_match: bool = False) -> List[MiniprogramMessage]:
        """按小程序名称过滤
        
        Args:
            app_name: 小程序名称
            exact_match: 是否精确匹配，默认False（模糊匹配）
            
        Returns:
            List[MiniprogramMessage]: 过滤后的小程序消息列表
        """
        try:
            all_miniprogram_msgs = self.extract_all_miniprogram_messages()
            filtered_messages = []
            
            for msg in all_miniprogram_msgs:
                msg_app_name = msg.app_name
                if exact_match:
                    if msg_app_name == app_name:
                        filtered_messages.append(msg)
                else:
                    if app_name.lower() in msg_app_name.lower():
                        filtered_messages.append(msg)
            
            wxlog.debug(f"按应用名称 '{app_name}' 过滤，找到 {len(filtered_messages)} 条消息")
            return filtered_messages
            
        except Exception as e:
            wxlog.warning(f"按应用名称过滤异常: {str(e)}")
            return []
    
    def filter_by_sender(self, sender: str, exact_match: bool = False) -> List[MiniprogramMessage]:
        """按发送者过滤
        
        Args:
            sender: 发送者名称
            exact_match: 是否精确匹配，默认False（模糊匹配）
            
        Returns:
            List[MiniprogramMessage]: 过滤后的小程序消息列表
        """
        try:
            all_miniprogram_msgs = self.extract_all_miniprogram_messages()
            filtered_messages = []
            
            for msg in all_miniprogram_msgs:
                msg_sender = msg.sender or ""
                if exact_match:
                    if msg_sender == sender:
                        filtered_messages.append(msg)
                else:
                    if sender.lower() in msg_sender.lower():
                        filtered_messages.append(msg)
            
            wxlog.debug(f"按发送者 '{sender}' 过滤，找到 {len(filtered_messages)} 条消息")
            return filtered_messages
            
        except Exception as e:
            wxlog.warning(f"按发送者过滤异常: {str(e)}")
            return []
    
    def filter_by_time_range(self, start_time: datetime = None, end_time: datetime = None) -> List[MiniprogramMessage]:
        """按时间范围过滤
        
        Args:
            start_time: 开始时间，默认None（不限制）
            end_time: 结束时间，默认None（不限制）
            
        Returns:
            List[MiniprogramMessage]: 过滤后的小程序消息列表
        """
        try:
            all_miniprogram_msgs = self.extract_all_miniprogram_messages()
            filtered_messages = []
            
            for msg in all_miniprogram_msgs:
                # 获取消息时间（如果有的话）
                msg_time = getattr(msg, 'share_time', None) or getattr(msg, 'time', None)
                
                if msg_time:
                    # 检查时间范围
                    if start_time and msg_time < start_time:
                        continue
                    if end_time and msg_time > end_time:
                        continue
                    filtered_messages.append(msg)
                elif not start_time and not end_time:
                    # 如果没有时间限制且消息没有时间信息，也包含进来
                    filtered_messages.append(msg)
            
            wxlog.debug(f"按时间范围过滤，找到 {len(filtered_messages)} 条消息")
            return filtered_messages
            
        except Exception as e:
            wxlog.warning(f"按时间范围过滤异常: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict[str, any]:
        """获取小程序消息统计信息
        
        Returns:
            Dict[str, any]: 统计信息字典
        """
        try:
            all_miniprogram_msgs = self.extract_all_miniprogram_messages()
            
            # 基础统计
            total_count = len(all_miniprogram_msgs)
            
            # 按应用名称统计
            app_names = [msg.app_name for msg in all_miniprogram_msgs if msg.app_name]
            app_counter = Counter(app_names)
            
            # 按发送者统计
            senders = [msg.sender for msg in all_miniprogram_msgs if msg.sender]
            sender_counter = Counter(senders)
            
            # 按消息类型统计
            friend_count = sum(1 for msg in all_miniprogram_msgs if isinstance(msg, FriendMiniprogramMessage))
            self_count = sum(1 for msg in all_miniprogram_msgs if isinstance(msg, SelfMiniprogramMessage))
            
            statistics = {
                'total_count': total_count,
                'friend_messages': friend_count,
                'self_messages': self_count,
                'top_apps': dict(app_counter.most_common(10)),
                'top_senders': dict(sender_counter.most_common(10)),
                'unique_apps': len(app_counter),
                'unique_senders': len(sender_counter),
                'extraction_time': datetime.now().isoformat()
            }
            
            wxlog.debug(f"生成统计信息: 总计 {total_count} 条小程序消息")
            return statistics
            
        except Exception as e:
            wxlog.warning(f"生成统计信息异常: {str(e)}")
            return {
                'total_count': 0,
                'friend_messages': 0,
                'self_messages': 0,
                'top_apps': {},
                'top_senders': {},
                'unique_apps': 0,
                'unique_senders': 0,
                'error': str(e),
                'extraction_time': datetime.now().isoformat()
            }
    
    def export_to_json(self, filepath: str, include_statistics: bool = True) -> WxResponse:
        """导出为JSON格式
        
        Args:
            filepath: 导出文件路径
            include_statistics: 是否包含统计信息，默认True
            
        Returns:
            WxResponse: 导出结果
        """
        try:
            all_miniprogram_msgs = self.extract_all_miniprogram_messages()
            
            # 准备导出数据
            export_data = {
                'export_info': {
                    'export_time': datetime.now().isoformat(),
                    'total_messages': len(all_miniprogram_msgs),
                    'chat_name': getattr(self.chat, 'who', 'Unknown')
                },
                'messages': []
            }
            
            # 转换消息数据
            for msg in all_miniprogram_msgs:
                try:
                    # 安全获取属性值，处理Mock对象和实际对象
                    def safe_get_attr(obj, attr, default=None):
                        try:
                            value = getattr(obj, attr, default)
                            # 如果是Mock对象，尝试获取其返回值
                            if hasattr(value, '_mock_name'):
                                return str(value) if value is not None else default
                            return value
                        except:
                            return default
                    
                    msg_data = {
                        'app_name': safe_get_attr(msg, 'app_name', ''),
                        'app_description': safe_get_attr(msg, 'app_description', ''),
                        'app_id': safe_get_attr(msg, 'app_id', None),
                        'page_path': safe_get_attr(msg, 'page_path', None),
                        'sender': safe_get_attr(msg, 'sender', ''),
                        'sender_remark': safe_get_attr(msg, 'sender_remark', ''),
                        'message_type': type(msg).__name__,
                        'share_time': None  # 简化时间处理
                    }
                    
                    # 处理时间字段
                    try:
                        share_time = safe_get_attr(msg, 'share_time', None)
                        if share_time and hasattr(share_time, 'isoformat'):
                            msg_data['share_time'] = share_time.isoformat()
                        elif share_time:
                            msg_data['share_time'] = str(share_time)
                    except:
                        msg_data['share_time'] = None
                    
                    export_data['messages'].append(msg_data)
                except Exception as e:
                    wxlog.warning(f"转换消息数据异常: {str(e)}")
                    # 添加一个基本的错误记录
                    export_data['messages'].append({
                        'app_name': 'Error',
                        'app_description': f'数据转换失败: {str(e)}',
                        'app_id': None,
                        'page_path': None,
                        'sender': 'Unknown',
                        'sender_remark': '',
                        'message_type': type(msg).__name__,
                        'share_time': None
                    })
                    continue
            
            # 添加统计信息
            if include_statistics:
                export_data['statistics'] = self.get_statistics()
            
            # 确保目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            wxlog.debug(f"成功导出 {len(all_miniprogram_msgs)} 条小程序消息到 {filepath}")
            return WxResponse.success(f"成功导出到 {filepath}")
            
        except Exception as e:
            error_msg = f"导出JSON文件异常: {str(e)}"
            wxlog.warning(error_msg)
            return WxResponse.failure(error_msg)
    
    def get_recent_miniprogram_messages(self, days: int = 7) -> List[MiniprogramMessage]:
        """获取最近几天的小程序消息
        
        Args:
            days: 天数，默认7天
            
        Returns:
            List[MiniprogramMessage]: 最近的小程序消息列表
        """
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            return self.filter_by_time_range(start_time, end_time)
            
        except Exception as e:
            wxlog.warning(f"获取最近小程序消息异常: {str(e)}")
            return []
    
    def find_duplicate_apps(self) -> Dict[str, List[MiniprogramMessage]]:
        """查找重复的小程序应用
        
        Returns:
            Dict[str, List[MiniprogramMessage]]: 重复应用的消息字典
        """
        try:
            all_miniprogram_msgs = self.extract_all_miniprogram_messages()
            app_groups = {}
            
            # 按应用名称分组
            for msg in all_miniprogram_msgs:
                app_name = msg.app_name
                if app_name not in app_groups:
                    app_groups[app_name] = []
                app_groups[app_name].append(msg)
            
            # 只返回有多条消息的应用
            duplicates = {app: msgs for app, msgs in app_groups.items() if len(msgs) > 1}
            
            wxlog.debug(f"找到 {len(duplicates)} 个重复的小程序应用")
            return duplicates
            
        except Exception as e:
            wxlog.warning(f"查找重复应用异常: {str(e)}")
            return {}
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效
        
        Returns:
            bool: 缓存是否有效
        """
        if not self._cached_messages or not self._cache_timestamp:
            return False
        
        # 检查缓存时间
        cache_age = (datetime.now() - self._cache_timestamp).total_seconds()
        return cache_age < self._cache_duration
    
    def clear_cache(self):
        """清除缓存"""
        self._cached_messages = None
        self._cache_timestamp = None
        wxlog.debug("已清除小程序消息缓存")