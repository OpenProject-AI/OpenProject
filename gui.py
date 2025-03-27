import maliang
import logging
from main import ChatManager

logger = logging.getLogger(__name__)

class ChatUI:
    def __init__(self):
        self.root = maliang.Tk(title="Chat Room", size=(800, 600))
        self.root.center()
        
        # 初始化ChatManager
        self.chat_manager = ChatManager()
        
        # 创建主容器
        self.main_frame = maliang.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        
        # 消息显示区域（带滚动条）
        self.chat_frame = maliang.ScrolledFrame(self.main_frame)
        self.chat_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 底部输入区域
        self.input_frame = maliang.Frame(self.main_frame)
        self.input_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # 输入框
        self.input_box = maliang.InputBox(self.input_frame, placeholder="Type message...")
        self.input_box.pack(side="left", fill="x", expand=True)
        
        # 发送按钮
        self.send_btn = maliang.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_btn.pack(side="right", padx=(10, 0))
        
        # 存储消息记录
        self.messages = []

    def create_progress_bar(self):
        """创建进度条组件"""
        self.progress_frame = maliang.Frame(self.main_frame)
        self.progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.progress_bar = maliang.ProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", expand=True)

    def update_progress(self, progress):
        """更新进度条"""
        if 0 <= progress <= 1:
            self.progress_bar.set(progress)

    def send_message(self):
        """处理消息发送"""
        text = self.input_box.get()
        if text.strip():
            try:
                self._add_message(f"You: {text}")
                self.input_box.set("")  # 清空输入框
                
                # 处理消息并获取响应
                result = self.chat_manager.process_chat_round(text)
                
                # 处理动作执行
                while result["use_action"]:
                    action_response = str(result["action_cback"])
                    self._add_message(f"Assistant (Action): {action_response}")
                    result = self.chat_manager.process_chat_round(result["action_cback"])
                
                # 显示最终响应
                response = result["chat_history"][-1]["content"]
                self._add_message(f"Assistant: {response}")
                
            except Exception as e:
                logger.error(f"发送消息失败: {str(e)}")
                self._add_message(f"Error: {str(e)}")
            
    def _add_message(self, message):
        """添加消息到显示区域"""
        msg_frame = maliang.Frame(self.chat_frame)
        msg_frame.pack(fill="x", padx=10, pady=5)
        
        msg = maliang.Text(msg_frame, text=message)
        msg.pack(anchor="w")
        self.messages.append(msg)
        
        # 自动滚动到底部
        self.chat_frame.see("end")

if __name__ == "__main__":
    ChatUI()
