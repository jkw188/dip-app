import customtkinter as ctk
from tkinter import messagebox
import hashlib
from core.dao.customer_dao import CustomerDAO
from core.models.customer import Customer

class RegisterFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F5F5F5") # Nền xám nhạt
        self.controller = controller
        self.customer_dao = CustomerDAO(controller.db.get_connection())
        self.setup_ui()

    def setup_ui(self):
        # Card
        card = ctk.CTkFrame(self, fg_color="white", width=450, height=600, corner_radius=0, border_width=1, border_color="#DDD")
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        # Title
        ctk.CTkLabel(card, text="TẠO TÀI KHOẢN", font=("Arial", 24, "bold"), text_color="black").pack(pady=(40, 30))

        # Inputs
        self.entry_user = self.create_input(card, "Tên đăng nhập")
        self.entry_pass = self.create_input(card, "Mật khẩu", show="*")
        self.entry_name = self.create_input(card, "Họ và tên")
        self.entry_phone = self.create_input(card, "Số điện thoại")
        self.entry_addr = self.create_input(card, "Địa chỉ")

        # Submit Button
        ctk.CTkButton(card, text="ĐĂNG KÝ", width=300, height=45, 
                      fg_color="black", text_color="white", font=("Arial", 13, "bold"), hover_color="#333",
                      command=self.handle_register).pack(pady=30)
        
        # Back Link
        ctk.CTkButton(card, text="← Quay lại đăng nhập", fg_color="transparent", text_color="gray", 
                      hover=False, font=("Arial", 12),
                      command=self.controller.show_login).pack()

    def create_input(self, parent, placeholder, show=None):
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, width=300, height=40, show=show,
                             fg_color="#FAFAFA", border_color="#E0E0E0", text_color="black")
        entry.pack(pady=8)
        return entry

    def handle_register(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        name = self.entry_name.get()
        phone = self.entry_phone.get()
        addr = self.entry_addr.get()

        if not all([user, pwd, name, phone, addr]):
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tất cả thông tin")
            return

        if self.customer_dao.select_by_username(user):
            messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại")
            return

        try:
            pwd_hash = hashlib.sha256(pwd.encode()).hexdigest()
            new_cus = Customer(id=0, username=user, password_hash=pwd_hash, full_name=name, phone=phone, address=addr)
            self.customer_dao.insert(new_cus)
            messagebox.showinfo("Thành công", "Đăng ký thành công! Vui lòng đăng nhập.")
            self.controller.show_login()
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", str(e))