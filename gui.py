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
        # 使用Canvas实现滚动条
        self.scrollbar = maliang.Canvas(auto_zoom=True)
        self.scrollbar.place(width=20, height=480, x=780, y=20)
        self.scrollbar.create_rectangle(0, 0, 20, 480, fill='#cccccc')
        self.scrollbar_thumb = maliang.Canvas(auto_zoom=True)
        self.scrollbar_thumb.place(width=20, height=100, x=780, y=20)
        self.scrollbar_thumb.create_rectangle(0, 0, 20, 100, fill='#4caf50')
        self.chat_frame.config(yscrollcommand=self._update_scrollbar)
        self.scrollbar.bind('<MouseWheel>', lambda event: self.chat_frame.yview_scroll(int(-1*(event.delta/120)), 'units'))

    def _update_scrollbar(self, first, last):
        """更新滚动条滑块位置"""
        if float(first) <= 0.0 and float(last) >= 1.0:
            return
        height = int(480 * (float(last) - float(first)))
        y = int(20 + 480 * float(first))
        self.scrollbar_thumb.place(width=20, height=height, x=780, y=y)
        self.chat_frame.bind('<MouseWheel>', lambda event: self.chat_frame.yview_scroll(int(-1*(event.delta/120)), 'units'))
        
        # 输入框
        self.input_box = maliang.InputBox(self.canvas, (20, 520), (640, 50), 
                                        placeholder="Type message...")
        # 发送按钮
        self.send_btn = maliang.Button(self.canvas, (680, 520), (100, 50), 
                                     text="Send", command=self.send_message)
        
        # 存储消息记录
        self.messages = []
        self.msg_height = 0  # 当前消息位置
        
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"程序异常终止: {e}")
            raise

    def create_progress_bar(self, x, y, width, height):
        """创建进度条组件"""
        self.progress_bar_bg = maliang.Canvas(auto_zoom=True)
        self.progress_bar_bg.place(width=width, height=height, x=x, y=y)
        self.progress_bar_bg.create_rectangle(0, 0, width, height, fill="#cccccc")

        self.progress_bar_fg = maliang.Canvas(auto_zoom=True)
        self.progress_bar_fg.place(width=0, height=height, x=x, y=y)
        self.progress_bar_fg.create_rectangle(0, 0, width, height, fill="#4caf50")

        self.progress_text = maliang.Text(self.progress_bar_bg, (width/2-10, height/2-10), text="0%", anchor="nw")

    def update_progress(self, progress):
        """更新进度条"""
        if 0 <= progress <= 1:
            width = int(self.progress_bar_bg['width'] * progress)
            self.progress_bar_fg.config(width=width)
            self.progress_text.config(text=f"{int(progress*100)}%")

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
        
        # 使用标准滚动条控制
        self.msg_height += msg.winfo_height() + 10
        self.chat_frame.yview_moveto(1.0)

if __name__ == "__main__":
    ChatUI()
