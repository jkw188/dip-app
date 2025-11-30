import customtkinter as ctk
from datetime import datetime
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from core.database import Database
from .product_dashboard import ProductDashboardFrame
# IMPORT CÁC VIEW MỚI


COLOR_BG_MAIN = "#F5F6FA"
COLOR_BG_SIDEBAR = "#FFFFFF"
COLOR_TEXT_MAIN = "#2D3436"
COLOR_TEXT_SUB = "#636E72"
COLOR_ACCENT = "#2D3436"
COLOR_HOVER = "#F1F2F6"

class BaseApp(ctk.CTk):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        
        self.db = Database() # Khởi tạo DB dùng chung cho cả app

        self.initialize_components()
        self.initialize_style()

    def initialize_components(self):
        self.title(f"LINDA - Seller Management | {self.current_user.full_name}")
        self.geometry("1280x800")
        ctk.set_appearance_mode("Light")
        
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_shadow = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color='#E0E0E0')
        self.sidebar_frame = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=COLOR_BG_SIDEBAR)
        
        self.lbl_logo = ctk.CTkLabel(self.sidebar_frame, text="🤖 LINDA", font=("Arial", 22, "bold"), text_color=COLOR_TEXT_MAIN)
        self.lbl_time = ctk.CTkLabel(self.sidebar_frame, text=datetime.now().strftime("%d %b %Y"), font=("Arial", 14), text_color=COLOR_TEXT_SUB)

        self.menu_buttons = []
        # Cập nhật danh sách menu theo đúng yêu cầu
        self.menu_items_config = [
            ("📦 Products", "load_product_dashboard_frame"), 
            ("👤 Employees", "load_employee_dashboard_frame"), 
            ("🛒 Cashier", "load_cashier_frame"), 
            ("📝 History", "load_history_frame"), 
            ("📥 Import", "load_import_product_frame"),
            ("🚪 Offboarding", "load_off_board_frame")
        ]
        
        for text, method_name in self.menu_items_config:
            btn = self.create_menu_button(text, method_name)
            self.menu_buttons.append(btn)

        self.profile_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.lbl_avatar = ctk.CTkLabel(self.profile_frame, text="👤", font=("Arial", 24))
        self.info_frame = ctk.CTkFrame(self.profile_frame, fg_color="transparent")
        self.lbl_user_name = ctk.CTkLabel(self.info_frame, text=self.current_user.full_name, font=("Arial", 13, "bold"), text_color=COLOR_TEXT_MAIN)
        self.btn_logout = ctk.CTkButton(self.info_frame, text="Logout", font=("Arial", 12), fg_color="transparent", text_color="#E17055", height=20, width=50, hover=False, anchor="w", command=self.handle_logout)

        self.main_area_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=COLOR_BG_MAIN)
        self.main_area_frame.grid_columnconfigure(0, weight=1)
        self.main_area_frame.grid_rowconfigure(0, weight=1)

        self.view_container = ctk.CTkFrame(self.main_area_frame, fg_color="transparent")
        self.view_container.grid_columnconfigure(0, weight=1)
        self.view_container.grid_rowconfigure(0, weight=1)
        
        # Khởi tạo và Cache các Views thật
        self.views = {}
        
        self.views['product_dashboard_frame'] = ProductDashboardFrame(self, self.view_container)

    def initialize_style(self):
        self.sidebar_shadow.place(x=2, y=0, relheight=1)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        self.lbl_logo.pack(pady=(40, 10), padx=30, anchor="w")
        self.lbl_time.pack(pady=(0, 30), padx=30, anchor="w")

        for btn in self.menu_buttons:
            btn.pack(pady=5, padx=20)

        self.profile_frame.pack(side="bottom", fill="x", padx=20, pady=30)
        self.lbl_avatar.pack(side="left")
        self.info_frame.pack(side="left", padx=10)
        self.lbl_user_name.pack(anchor="w")
        self.btn_logout.pack(anchor="w")

        self.main_area_frame.grid(row=0, column=1, sticky="nsew")
        self.view_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Mặc định mở Product View
        self.load_product_dashboard_frame()

    def create_menu_button(self, text, method_name):
        btn = ctk.CTkButton(
            self.sidebar_frame, 
            text=text, height=45, 
            corner_radius=12, 
            font=("Arial", 15, "bold"), 
            fg_color="transparent", 
            text_color=COLOR_TEXT_SUB, 
            hover_color=COLOR_HOVER, 
            anchor="w", width=200
        )
        btn.configure(command=method_name)
        return btn

    def reset_switch_view(self):
        for btn in self.menu_buttons:
            btn.configure(fg_color="transparent", text_color=COLOR_TEXT_SUB)

        for v in self.views.values():
            v.pack_forget() # Dùng pack_forget vì các View class dùng pack()
        
    def open_view(self, view_name):
        self.views[view_name].pack(fill="both", expand=True)

    def highlight_button(self, btn):
        btn.configure(fg_color=COLOR_ACCENT, text_color="white")

    def load_product_dashboard_frame(self):
        self.reset_switch_view()
        self.highlight_button(self.menu_buttons[0])
        self.open_view('product_dashboard_frame')

    def load_employee_dashboard_frame(self):
        pass 

    def load_cashier_frame(self):
        pass 

    def load_history_frame(self):
        pass 

    def load_add_employee_frame(self):
        pass 

    def load_add_product_frame(self):
        pass 

    def load_confirm_import_product_frame(self):
        pass 

    def load_confirm_off_board_frame(self):
        pass 

    def load_edit_employee_frame(self):
        pass 

    def load_edit_product_frame(self):
        pass 

    def load_import_product_frame(self):
        pass 

    def load_off_board_frame(self):
        pass 

    def handle_logout(self):
        self.destroy()
        import subprocess
        subprocess.Popen([sys.executable, os.path.join(parent_dir, "seller_app", "login.py")])
