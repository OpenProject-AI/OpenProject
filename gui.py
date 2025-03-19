import maliang

class ChatUI:
    def __init__(self):
        self.root = maliang.Tk(title="Chat Room", size=(800, 600))
        self.root.center()
        
        # 创建画布容器
        self.canvas = maliang.Canvas(auto_zoom=True, keep_ratio="min")
        self.canvas.place(width=800, height=600)
        
        # 消息显示区域（模拟可滚动区域）
        self.chat_frame = maliang.Canvas(auto_zoom=True)
        self.chat_frame.place(width=760, height=480, x=20, y=20)
        
        # 输入框
        self.input_box = maliang.InputBox(self.canvas, (20, 520), (640, 50), 
                                        placeholder="Type message...")
        # 发送按钮
        self.send_btn = maliang.Button(self.canvas, (680, 520), (100, 50), 
                                     text="Send", command=self.send_message)
        
        # 存储消息记录
        self.messages = []
        self.msg_height = 0  # 当前消息位置
        
        self.root.mainloop()

    def send_message(self):
        """处理消息发送"""
        text = self.input_box.get()
        if text.strip():
            self._add_message(f"You: {text}")
            self.input_box.set("")  # 清空输入框

            # 此处可添加网络发送逻辑
            
    def _add_message(self, message):
        """添加消息到显示区域"""
        msg = maliang.Text(self.chat_frame, (10, self.msg_height+10), 
                          text=message, anchor="nw")
        self.messages.append(msg)
        
        # 简单滚动效果（每次发送后滚动到底部）
        self.msg_height += 30
        self.chat_frame.scroll_y = self.msg_height - 460 if self.msg_height > 460 else 0

if __name__ == "__main__":
    ChatUI()
