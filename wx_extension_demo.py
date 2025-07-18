from wxauto import uiautomation as uia
from wxauto import WeChat
import time
import traceback

def forward_and_get_new_msg(wx: WeChat, target_msg, forward_to_who: str):
    """
    一个基于uiautomation底层能力扩展的函数，用于：
    1. 右键点击一个消息
    2. 在菜单中选择"转发"
    3. 在新窗口中选择联系人并发送
    4. 获取转发后产生的新消息

    Args:
        wx (WeChat): 已初始化的WeChat实例.
        target_msg (Message): 要转发的目标消息对象.
        forward_to_who (str): 要转发给谁.

    Returns:
        Message or None: 转发成功后，在目标聊天中产生的新消息对象；如果失败则返回None.
    """
    print("--- 开始执行底层UI自动化转发流程 ---")

    # 步骤 1: 右键点击目标消息的底层UI控件
    try:
        print(f"[1/5] 正在右键点击消息: '{target_msg.content.splitlines()[0]}...'")
        target_msg.control.RightClick(simulateMove=False)
        time.sleep(1)
    except Exception:
        print(f"错误：右键点击失败。\n{traceback.format_exc()}")
        return None

    # 步骤 2: 从桌面找到右键菜单并点击"转发"
    try:
        print("[2/5] 正在从桌面寻找右键菜单...")
        # 右键菜单是顶级窗口，所以从Root开始找
        menu = uia.MenuControl(searchDepth=1) 
        print("[3/5] 成功找到菜单，正在点击'转发'...")
        menu.MenuItemControl(Name='转发').Click(simulateMove=False)
        time.sleep(1)
    except uia.errors.NotFoundError:
        print(f"错误：未能找到右键菜单或'转发'选项。\n{traceback.format_exc()}")
        return None

    # 步骤 3: 找到"合并转发"窗口，选择联系人并发送
    try:
        print("[4/5] 正在寻找'合并转发'窗口...")
        # "合并转发"窗口也是一个顶级窗口
        forward_win = uia.WindowControl(searchDepth=1, Name='合并转发')
        
        print("       - 正在搜索联系人...")
        forward_win.EditControl(searchDepth=3).SendKeys(forward_to_who)
        time.sleep(0.5)
        
        print("       - 正在点击联系人...")
        forward_win.ListItemControl(Name=forward_to_who).Click(simulateMove=False)
        time.sleep(0.5)
        
        print("       - 正在点击'发送'按钮...")
        forward_win.ButtonControl(Name='发送').Click(simulateMove=False)
        print("       - 转发操作已发送。")
        time.sleep(1) # 等待消息发送和接收
    except Exception:
        print(f"错误：在'合并转发'窗口中操作失败。\n{traceback.format_exc()}")
        return None

    # 步骤 4: 回到文件传输助手，获取最后一条消息
    try:
        print("[5/5] 正在获取转发后产生的新消息...")
        wx.ChatWith(forward_to_who)
        time.sleep(0.5)
        all_msgs = wx.GetAllMessage()
        if all_msgs:
            new_msg = all_msgs[-1]
            print("--- 扩展功能执行成功！---")
            return new_msg
        else:
            print("错误：获取新消息失败。")
            return None
    except Exception:
        print(f"错误：获取新消息时出错。\n{traceback.format_exc()}")
        return None

def main():
    wx = WeChat()
    who = '文件传输助手'
    wx.ChatWith(who)
    print(f"已切换到 '{who}'。正在定位原始小程序消息...")

    messages = wx.GetAllMessage()
    if not messages:
        print("未找到任何消息。")
        return

    target_msg = None
    for msg in reversed(messages):
        # 定位我们之前找到的那个特殊小程序
        if msg.type == 'other' and msg.content.strip() and '新鲜下树' in msg.content:
            target_msg = msg
            break
    
    if not target_msg:
        print("未在当前可见消息中找到目标'快团团'小程序。请确保它可见。")
        return
    
    # 使用我们扩展的函数进行转发和分析
    newly_forwarded_msg = forward_and_get_new_msg(wx, target_msg, who)

    if newly_forwarded_msg:
        print("\n\n--- 对转发后的新消息进行分析 ---")
        print(f"新消息类型: '{newly_forwarded_msg.type}'")
        print(f"新消息内容: '{newly_forwarded_msg.content}'")
        print(f"新消息对象所有属性: {newly_forwarded_msg.__dict__}")
        print("\n分析完成。请检查以上信息是否包含了小程序链接或所需信息。")

if __name__ == '__main__':
    print("即将执行扩展功能演示，请确保微信已登录且目标小程序在'文件传输助手'中可见。")
    time.sleep(3)
    main() 