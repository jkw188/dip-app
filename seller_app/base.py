import customtkinter as ctk
from datetime import datetime
from PIL import Image
import os

# --- CẤU HÌNH MÀU SẮC ---
COLOR_BG_MAIN = "#F5F6FA"
COLOR_BG_SIDEBAR = "#FFFFFF"
COLOR_CARD = "#FFFFFF"
COLOR_TEXT_MAIN = "#2D3436"
COLOR_TEXT_SUB = "#636E72"
COLOR_ACCENT = "#2D3436"
COLOR_HOVER = "#F1F2F6"

class BaseApp(ctk.CTk):
    def __init__(self, current_user):
        super().__init__()
        
        self.current_user = current_user # Lưu thông tin nhân viên đang đăng nhập

        # 1. Cấu hình cửa sổ
        self.title(f"LINDA - Seller Management | {current_user.full_name}")
        self.geometry("1200x800")
        ctk.set_appearance_mode("Light")
        
        # Grid Layout
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR (TRÁI) ---
        self.setup_sidebar()

        # --- MAIN CONTENT (PHẢI) ---
        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color=COLOR_BG_MAIN)
        self.main_area.grid(row=0, column=1, sticky="nsew")
        
        # Header Status (Thanh trạng thái trên cùng)
        self.create_status_bar()

        # Container chứa các Views
        self.view_container = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.view_container.pack(fill="both", expand=True, padx=30, pady=20)

        # Khởi tạo các Views (Placeholder)
        self.views = {}
        # Bạn import các View thật vào đây thay vì Placeholder này
        self.views["Dashboard"] = self.create_placeholder_view("📊 DASHBOARD")
        self.views["Products"] = self.create_placeholder_view("📦 PRODUCTS")
        self.views["Orders"] = self.create_placeholder_view("📝 ORDERS")
        self.views["Import"] = self.create_placeholder_view("📥 IMPORT")
        
        # Mặc định hiện Dashboard
        self.change_view("Dashboard", self.menu_buttons[0])

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=COLOR_BG_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo
        ctk.CTkLabel(self.sidebar, text="🤖 LINDA", 
                     font=("DM Sans", 22, "bold"), text_color=COLOR_TEXT_MAIN).pack(pady=(40, 10), padx=30, anchor="w")
        
        # Ngày giờ
        self.time_label = ctk.CTkLabel(self.sidebar, text=datetime.now().strftime("%d %b %Y"),
                                       font=("DM Sans", 14), text_color=COLOR_TEXT_SUB)
        self.time_label.pack(pady=(0, 30), padx=30, anchor="w")

        # Menu Buttons
        self.menu_buttons = []
        menus = [("Dashboard", "Dashboard"), 
                 ("Products", "Products"), 
                 ("Orders", "Orders"), 
                 ("Import", "Import")]
        
        for text, view_name in menus:
            btn = self.create_menu_button(text, view_name)
            self.menu_buttons.append(btn)

        # User Profile (Dưới đáy)
        self.create_user_profile()

    def create_menu_button(self, text, view_name):
        btn = ctk.CTkButton(self.sidebar, text=text, height=45, corner_radius=12,
                            font=("DM Sans", 15, "bold"), fg_color="transparent",
                            text_color=COLOR_TEXT_SUB, hover_color=COLOR_HOVER, anchor="w", width=200)
        btn.pack(pady=5, padx=20)
        btn.configure(command=lambda: self.change_view(view_name, btn))
        return btn

    def create_user_profile(self):
        profile_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        profile_frame.pack(side="bottom", fill="x", padx=20, pady=30)
        
        ctk.CTkLabel(profile_frame, text="👤", font=("Arial", 24)).pack(side="left")
        
        info = ctk.CTkFrame(profile_frame, fg_color="transparent")
        info.pack(side="left", padx=10)
        
        # Hiển thị tên người dùng đăng nhập
        ctk.CTkLabel(info, text=self.current_user.full_name, font=("DM Sans", 13, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w")
        
        # Nút Logout
        logout_btn = ctk.CTkButton(info, text="Logout", font=("DM Sans", 12), fg_color="transparent", 
                                   text_color="#E17055", height=15, width=0, anchor="w", hover=False,
                                   command=self.handle_logout)
        logout_btn.pack(anchor="w")

    def create_status_bar(self):
        # (Giữ nguyên code phần status bar từ bài trước nếu muốn)
        pass

    def change_view(self, view_name, btn_obj):
        for btn in self.menu_buttons:
            btn.configure(fg_color="transparent", text_color=COLOR_TEXT_SUB)
        btn_obj.configure(fg_color=COLOR_ACCENT, text_color="white")
        
        frame = self.views[view_name]
        frame.tkraise()

    def create_placeholder_view(self, text):
        frame = ctk.CTkFrame(self.view_container, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(frame, text=text, font=("Arial", 30)).pack(pady=50)
        return frame

    def handle_logout(self):
        self.destroy()
        # Để quay lại trang login, cách đơn giản nhất là chạy lại file login.py
        # Hoặc dùng cấu trúc Controller để quản lý việc switch cửa sổ
        print("User logged out")
        import subprocess
        subprocess.Popen(["python", "seller_app/login.py"])