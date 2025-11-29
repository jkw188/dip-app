import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import hashlib
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from core.database import Database
from core.dao.employee_dao import EmployeeDAO
from seller_app.base import BaseApp

class LoginForm(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.initialize_components()
        self.initialize_style()

    def initialize_components(self):
        self.title('LINDA - Login')
        self.geometry('900x600')
        ctk.set_appearance_mode('Light')
        self.configure(fg_color='#F8F9FB')

        self.db = Database()
        self.employee_dao = EmployeeDAO(self.db.get_connection())

        self.card_frame = ctk.CTkFrame(
            self,
            width=400,
            height=500,
            fg_color='white',
            corner_radius=20,
            border_width=0
        )

        self.sub_card_frame = ctk.CTkFrame(
            self.card_frame,
            fg_color='white'
        )

        logo_path = os.path.join(parent_dir, 'logo.jpg')
        if os.path.exists(logo_path):
            self.logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(60, 60)
            )
        else:
            self.logo_image = None 

        self.lbl_title = ctk.CTkLabel(
            self.sub_card_frame,
            text='LINDA',
            image=self.logo_image,
            compound='left',
            font=('Arial', 28, 'bold'),
            text_color='black',
            padx=10
        )

        self.lbl_username = ctk.CTkLabel(
            self.sub_card_frame,
            text='USERNAME',
            font=('Arial', 12, 'bold'),
            text_color='black'
        )

        self.entry_username = ctk.CTkEntry(
            self.sub_card_frame,
            width=300,
            height=40,
            corner_radius=20,
            border_width=1,
            border_color='black',
            fg_color='white',
            text_color='black',
            placeholder_text=''
        )

        self.lbl_password = ctk.CTkLabel(
            self.sub_card_frame,
            text='PASSWORD',
            font=('Arial', 12, 'bold'),
            text_color='black'
        )

        self.entry_password = ctk.CTkEntry(
            self.sub_card_frame,
            width=300,
            height=40,
            corner_radius=20,
            border_color='black',
            border_width=1,
            fg_color='white',
            text_color='black',
            show='*',
            placeholder_text=''
        )
        
        self.entry_password.bind("<Return>", lambda event: self.handle_login())

        self.btn_login = ctk.CTkButton(
            self.sub_card_frame,
            text='LOGIN',
            width=300,
            height=45,
            corner_radius=22,
            fg_color='black',
            text_color='white',
            font=('Arial', 14, 'bold'),
            hover_color='#333333',
            command=self.handle_login
        )

    def initialize_style(self):
        self.card_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
        self.card_frame.pack_propagate(False) 

        self.sub_card_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        self.lbl_title.pack(pady=(0, 40))

        self.lbl_username.pack(anchor='w', padx=10, pady=(0, 5))
        self.entry_username.pack(pady=(0, 20))

        self.lbl_password.pack(anchor='w', padx=10, pady=(0, 5))
        self.entry_password.pack(pady=(0, 40))

        self.btn_login.pack(pady=(0, 10))

    def handle_login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not username or not password:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin!")
            return

        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            employee = self.employee_dao.select_by_username(username)
            
            if employee and employee.password_hash == pwd_hash:
                if employee.status != 'active':
                    messagebox.showerror("Lỗi", "Tài khoản này đã bị vô hiệu hóa!")
                    return

                self.destroy()
                
                app = BaseApp(current_user=employee)
                app.mainloop()
            else:
                messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu!")
        
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", str(e))