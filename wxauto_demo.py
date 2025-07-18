from wxauto import WeChat
import time
import os

# 检查微信是否已登录
def check_login():
    """检查微信是否已经登录"""
    # 这里我们通过检查微信主窗口是否存在来简单判断
    # 更可靠的方法可能需要结合其他UI自动化库或图像识别
    # 但对于wxauto，它在初始化时会尝试获取窗口，如果失败会抛出异常
    print("请确保微信PC版已经登录并显示主界面...")
    time.sleep(3) # 等待用户确认

def main():
    """主函数"""
    print("--- 微信自动化演示开始 ---")
    
    # 步骤 1: 初始化 WeChat 对象
    # 这会自动寻找当前登录的微信客户端并 attach
    print("正在初始化微信...")
    try:
        wx = WeChat()
        print("微信初始化成功！")
    except Exception as e:
        print(f"初始化失败，请确保微信已登录。错误: {e}")
        return

    # 步骤 2: 获取当前登录用户信息
    my_nickname = wx.nickname
    print(f"\n成功获取到你的信息：")
    print(f"  - 昵称: {my_nickname}")

    # 步骤 3: 向"文件传输助手"发送消息
    who = '文件传输助手'
    message = f"你好，{my_nickname}！你好！({time.strftime('%Y-%m-%d %H:%M:%S')})"
    
    print(f"\n准备向'{who}'发送消息...")
    wx.SendMsg(message, who)
    print(f"消息已发送: {message}")
    
    # 等待一秒，确保消息发送和接收完成
    time.sleep(1)

    # 步骤 4: 获取与"文件传输助手"的聊天记录
    print(f"\n正在获取与'{who}'的聊天记录...")
    
    # 首先确保聊天窗口是最新的
    wx.ChatWith(who) # 打开与'文件传输助手'的聊天窗口
    
    # 获取消息
    messages = wx.GetAllMessage() # 获取当前窗口的所有消息
    
    if messages:
        print(f"成功获取 {len(messages)} 条消息记录：")
        for i, msg in enumerate(messages[-10:]): # 只显示最近10条
            print(f"  {i+1}. [{msg.type}] 来自 {msg.sender}: {msg.content}")
    else:
        print("未能获取到任何消息。")
        
    print("\n--- 微信自动化演示结束 ---")

if __name__ == "__main__":
    check_login()
    main() 