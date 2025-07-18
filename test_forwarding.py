from wxauto import WeChat
import time

def main():
    """主函数：尝试转发小程序，以解析其链接"""
    print("--- 开始尝试转发小程序 ---")

    try:
        wx = WeChat()
        print("微信初始化成功！")
    except Exception as e:
        print(f"初始化失败: {e}")
        return

    # 1. 切换到 "文件传输助手" 并找到目标消息
    who = '文件传输助手'
    print(f"\n正在切换到 '{who}'...")
    wx.ChatWith(who)
    time.sleep(1)

    print("正在获取聊天记录以定位目标消息...")
    messages = wx.GetAllMessage()
    if not messages:
        print("未找到任何消息。")
        return

    target_msg = None
    for msg in reversed(messages):
        if msg.type == 'other' and msg.content.strip():
            target_msg = msg
            print(f"成功定位到目标消息，内容为: '{msg.content.splitlines()[0]}...'")
            break

    if not target_msg:
        print("在可见消息中未找到目标小程序卡片。")
        return

    # 2. 模拟右键点击并转发
    print("\n--- 关键步骤 ---")
    try:
        # 2a. 模拟右键点击
        # msg.control 是底层的UI控件，我们直接操作它
        print("步骤 2a: 正在对消息进行右键点击...")
        target_msg.control.RightClick()
        time.sleep(1) # 等待右键菜单弹出

        # 2b. 点击菜单中的"转发"
        # 通常右键菜单是 CMenuWnd 的一个实例，可通过核心对象访问
        print("步骤 2b: 正在点击'转发'菜单项...")
        wx.core.CMenu.MenuItem(Name='转发').Click()
        time.sleep(1) # 等待"选择联系人"窗口弹出

        # 2c. 在新窗口中选择"文件传输助手"并发送
        # "选择联系人"是一个新窗口，我们假设它的类名为 'SelectContactWnd'
        # 这是对wxauto能力的推测，但符合逻辑
        print("步骤 2c: 正在转发给'文件传输助手'...")
        forward_window = wx.core.Session.Control(ClassName='SelectContactWnd')
        forward_window.Edit(Name='搜索').SendKeys(who)
        time.sleep(0.5)
        forward_window.ListItem(Name=who).Click()
        time.sleep(0.5)
        forward_window.Button(Name='发送').Click()
        
        print("\n--- 转发成功！---")
        print("请检查'文件传输助手'，应该已经收到一条新转发的消息。")
        print("\n下一步：请再次运行 get_miniprogram_link.py 脚本来分析这条新消息的类型和内容。")

    except Exception as e:
        print(f"\n--- 自动转发过程中出错 ---")
        print(f"错误详情: {e}")
        print("\n这很可能意味着 wxauto 对右键菜单或转发窗口的支持与我们推测的不同。")
        print("不过别担心，你仍然可以手动完成这个过程：")
        print("1. 手动右键点击那个小程序。")
        print("2. 在菜单中点击"转发"。")
        print("3. 选择"文件传输助手"并发送。")
        print("4. 然后运行 get_miniprogram_link.py 脚本进行分析。")


if __name__ == "__main__":
    print("请确保微信PC版已经登录。")
    print("程序将在3秒后开始...")
    time.sleep(3)
    main() 