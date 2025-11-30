import customtkinter as ctk
from tkinter import messagebox
import hashlib
from core.dao.customer_dao import CustomerDAO

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F0F0F0") # Nền tổng thể xám nhẹ
        self.controller = controller
        self.customer_dao = CustomerDAO(controller.db.get_connection())
        
        self.setup_ui()

    def setup_ui(self):
        # Card Login
        frame = ctk.CTkFrame(self, fg_color="white", width=400, height=500, corner_radius=0, border_width=1, border_color="#DDD")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        frame.pack_propagate(False)

        ctk.CTkLabel(frame, text="WELCOME BACK", font=("Arial", 26, "bold"), text_color="black").pack(pady=(60, 10))
        ctk.CTkLabel(frame, text="Đăng nhập vào tài khoản của bạn", font=("Arial", 12), text_color="gray").pack(pady=(0, 30))

        # Inputs
        self.entry_user = ctk.CTkEntry(frame, placeholder_text="Tên đăng nhập", width=300, height=45, 
                                       fg_color="#FAFAFA", border_color="#E0E0E0", text_color="black")
        self.entry_user.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(frame, placeholder_text="Mật khẩu", width=300, height=45, show="*",
                                       fg_color="#FAFAFA", border_color="#E0E0E0", text_color="black")
        self.entry_pass.pack(pady=10)

        # Button Login (Black)
        ctk.CTkButton(frame, text="ĐĂNG NHẬP", width=300, height=45, 
                      fg_color="black", text_color="white", font=("Arial", 13, "bold"), hover_color="#333",
                      command=self.handle_login).pack(pady=30)

        # Register Link
        link_frame = ctk.CTkFrame(frame, fg_color="transparent")
        link_frame.pack()
        ctk.CTkLabel(link_frame, text="Chưa có tài khoản?", text_color="gray", font=("Arial", 12)).pack(side="left")
        ctk.CTkButton(link_frame, text="Đăng ký ngay", fg_color="transparent", text_color="black", 
                      font=("Arial", 12, "bold", "underline"), hover=False, width=80,
                      command=self.controller.show_register).pack(side="left")

    def handle_login(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()

        if not username or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ!")
            return

        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        customer = self.customer_dao.select_by_username(username)

        if customer and customer.password_hash == pwd_hash:
            self.controller.current_user = customer
            self.controller.show_dashboard()
        else:
            messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu")