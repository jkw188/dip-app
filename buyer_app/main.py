import customtkinter as ctk
import os
import sys

# Setup đường dẫn để import core
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from core.database import Database
from buyer_app.login import LoginFrame
from buyer_app.register import RegisterFrame
from buyer_app.dashboard import DashboardFrame
from buyer_app.cart import CartFrame
from buyer_app.payment import PaymentFrame
from buyer_app.confirm_payment import ConfirmPaymentFrame
from buyer_app.history import HistoryFrame

class BuyerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LINDA - Mua sắm trực tuyến")
        self.geometry("1200x800")
        ctk.set_appearance_mode("Light")
        
        self.db = Database()
        self.current_user = None
        self.cart = {} # Giỏ hàng: {product_id: {'obj': product, 'qty': int}}

        # Container chính chứa các frame
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.current_frame = None

        # Khởi tạo màn hình Login đầu tiên
        self.show_login()

    def switch_frame(self, frame_class, **kwargs):
        # Xóa frame cũ
        if self.current_frame:
            self.current_frame.destroy()
        
        # Tạo frame mới
        self.current_frame = frame_class(self.container, self, **kwargs)
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def show_login(self):
        self.switch_frame(LoginFrame)

    def show_register(self):
        self.switch_frame(RegisterFrame)

    def show_dashboard(self):
        self.switch_frame(DashboardFrame)

    def show_cart(self):
        self.switch_frame(CartFrame)

    def show_payment(self):
        self.switch_frame(PaymentFrame)

    def show_confirm_payment(self):
        self.switch_frame(ConfirmPaymentFrame)

    def show_history(self):
        self.switch_frame(HistoryFrame)
    
    def logout(self):
        self.current_user = None
        self.cart = {}
        self.show_login()

if __name__ == "__main__":
    app = BuyerApp()
    app.mainloop()