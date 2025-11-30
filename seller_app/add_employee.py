import customtkinter as ctk
from tkinter import messagebox
import hashlib
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from core.dao.employee_dao import EmployeeDAO
from core.models.employee import Employee

class AddEmployeeFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.db_conn = controller.db.get_connection()
        self.employee_dao = EmployeeDAO(self.db_conn)

        # Cấu hình grid cho frame chính để nó chiếm hết không gian cha
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Header cố định
        self.grid_rowconfigure(1, weight=1) # Phần thân co giãn

        self.setup_ui()

    def setup_ui(self):
        # 1. HEADER (Cố định ở trên cùng)
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkButton(header, text="< Back", width=80, fg_color="gray", 
                      command=self.go_back).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(header, text="ADD NEW EMPLOYEE", font=("Arial", 24, "bold"), 
                     text_color="#2D3436").pack(side="left")

        # 2. FORM CONTAINER (Chiếm toàn bộ phần còn lại)
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Để căn giữa form trong container rộng lớn này, ta dùng place cho form_frame
        # Hoặc dùng grid với weight để căn giữa. Ở đây dùng place cho giống style Login.
        
        # Shadow Frame (Hiệu ứng bóng đổ nhẹ)
        self.shadow_frame = ctk.CTkFrame(container, width=500, height=550, fg_color="#E0E0E0", corner_radius=15)
        self.shadow_frame.place(relx=0.503, rely=0.505, anchor="center")

        # Form Frame Chính (Màu trắng)
        self.form_frame = ctk.CTkFrame(container, width=500, height=550, fg_color="white", corner_radius=15)
        self.form_frame.place(relx=0.5, rely=0.5, anchor="center")
        # Cho phép form_frame không bị co lại theo nội dung (để giữ kích thước cố định đẹp)
        self.form_frame.pack_propagate(False) 

        # --- NỘI DUNG FORM ---
        ctk.CTkLabel(self.form_frame, text="Employee Information", font=("Arial", 20, "bold"), text_color="#2D3436").pack(pady=(40, 30))

        # Username
        self.entry_username = self.create_input_field(self.form_frame, "Username")
        
        # Full Name
        self.entry_fullname = self.create_input_field(self.form_frame, "Full Name")

        # Password
        self.entry_password = self.create_input_field(self.form_frame, "Password", is_password=True)

        # Confirm Password
        self.entry_confirm_pass = self.create_input_field(self.form_frame, "Confirm Password", is_password=True)

        # Footer Button
        btn_save = ctk.CTkButton(self.form_frame, text="CREATE ACCOUNT", height=45, fg_color="#00b894", 
                                 font=("Arial", 14, "bold"), command=self.save_employee)
        btn_save.pack(fill="x", padx=60, pady=20)

    def create_input_field(self, parent, label_text, is_password=False):
        # Helper tạo label + entry gọn gàng
        ctk.CTkLabel(parent, text=label_text, text_color="gray", font=("Arial", 12, "bold")).pack(anchor="w", padx=60, pady=(5, 0))
        entry = ctk.CTkEntry(parent, height=40, border_color="#dfe6e9", border_width=2, 
                             fg_color="white", text_color="black", 
                             show="*" if is_password else "")
        entry.pack(fill="x", padx=60, pady=(0, 15))
        return entry

    def save_employee(self):
        username = self.entry_username.get().strip()
        fullname = self.entry_fullname.get().strip()
        password = self.entry_password.get().strip()
        confirm = self.entry_confirm_pass.get().strip()

        if not username or not fullname or not password:
            messagebox.showerror("Error", "Please fill in all fields!")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        if self.employee_dao.select_by_username(username):
            messagebox.showerror("Error", "Username already exists!")
            return

        try:
            pwd_hash = hashlib.sha256(password.encode()).hexdigest()
            new_emp = Employee(
                id=0,
                username=username,
                password_hash=pwd_hash,
                full_name=fullname,
                status='active'
            )
            self.employee_dao.insert(new_emp)
            messagebox.showinfo("Success", f"Employee '{username}' created successfully!")
            self.go_back()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def go_back(self):
        self.controller.load_employee_dashboard_frame()