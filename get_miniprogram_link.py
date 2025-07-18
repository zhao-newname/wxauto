from wxauto import WeChat
import time

def main():
    """主函数：获取文件传输助手中最新的小程序并打印标题"""
    print("--- 开始获取小程序链接 ---")

    # 初始化 WeChat 对象
    try:
        wx = WeChat()
        print("微信初始化成功！")
    except Exception as e:
        print(f"初始化失败，请确保微信已登录。错误: {e}")
        return

    # 切换到 "文件传输助手"
    who = '文件传输助手'
    print(f"\n正在切换到 '{who}'...")
    wx.ChatWith(who)
    time.sleep(1) # 等待窗口切换完成

    # 获取当前窗口的所有消息
    print("正在获取聊天记录...")
    messages = wx.GetAllMessage()

    if not messages:
        print("在 '文件传输助手' 中没有找到任何消息。")
        return

    print("\n开始遍历消息，寻找小程序...\n")
    found = False
    # 我们从后往前遍历，更容易找到最近的小程序
    for msg in reversed(messages):
        # 为了调试，仍然打印出所有消息的类型和内容
        print(f"检测到消息 -> 类型: '{msg.type}', 内容: '{msg.content}'")

        # 新的逻辑：因为 wxauto 把它识别为了'other'类型，我们在这里捕获它
        # 并且我们只关心有实质文本内容的 'other' 消息
        if msg.type == 'other' and msg.content.strip():
            found = True
            # 从多行内容中提取第一行作为标题
            title = msg.content.splitlines()[0]
            print(f"\n--- 找到了一个疑似小程序的卡片 (类型为'other')! ---")
            print(f"  - 提取到的标题是: {title}")
            
            # 深入调试：打印消息对象的所有属性，寻找链接
            print("\n  [深入调试信息] 消息对象的全部属性:")
            try:
                # __dict__ 包含了对象的所有实例属性
                print(f"  {msg.__dict__}")
            except AttributeError:
                print("  该消息对象没有 __dict__ 属性。")

            # 结论：根据调试信息判断是否有URL
            if 'url' in msg.__dict__ or 'link' in msg.__dict__:
                 print("\n  [结论] 找到了链接相关的属性！")
            else:
                 print("\n  [结论] 在消息对象的所有属性中，未直接找到URL或链接。这可能意味着wxauto无法从这类消息卡片中直接提取链接。")

            # 找到最近的一个就结束
            break
    
    if not found:
        print("\n在 '文件传输助手' 的可见消息中未找到小程序链接或 'other' 类型的卡片消息。")
        print("提示：请确保小程序链接在当前屏幕可见，或手动上滑加载更多历史消息。")

    print("\n--- 任务结束 ---")


if __name__ == "__main__":
    print("请确保微信PC版已经登录，并且'文件传输助手'中有小程序链接。")
    print("程序将在3秒后开始...")
    time.sleep(3)
    main() 