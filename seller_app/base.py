import customtkinter as ctk
from datetime import datetime
import os
import sys
from PIL import Image

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from core.database import Database

# Import tất cả Views
from .product_dashboard import ProductDashboardFrame
from .employee_dashboard import EmployeeDashboardFrame
from .cashier import CashierFrame
from .history import HistoryFrame
from .import_product import ImportProductFrame
from .off_board import OffBoardFrame

# Import Edit Frames
from .add_product import AddProductFrame
from .add_employee import AddEmployeeFrame
from .edit_product import EditProductFrame
from .edit_employee import EditEmployeeFrame

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
        self.db = Database()

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
        
        logo_path = os.path.join(parent_dir, 'logo.jpg')
        if os.path.exists(logo_path):
            self.logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(80, 80)
            )
        else:
            self.logo_image = None 

        self.lbl_logo = ctk.CTkLabel(
            self.sidebar_frame,
            text='LINDA',
            image=self.logo_image,
            compound='left',
            font=('Arial', 40, 'bold'),
            text_color='black',
            padx=10
        )
        self.lbl_time = ctk.CTkLabel(self.sidebar_frame, text=datetime.now().strftime("%d %b %Y"), font=("Arial", 14), text_color=COLOR_TEXT_SUB)

        self.menu_buttons = []
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
        
        self.views = {}
        self.views['product_dashboard_frame'] = ProductDashboardFrame(self.view_container, self)

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

        self.load_product_dashboard_frame()

    def create_menu_button(self, text, method_name):
        method = getattr(self, method_name)
        btn = ctk.CTkButton(self.sidebar_frame, text=text, height=45, corner_radius=12, font=("Arial", 15, "bold"), fg_color="transparent", text_color=COLOR_TEXT_SUB, hover_color=COLOR_HOVER, anchor="w", width=200, command=method)
        return btn

    def reset_switch_view(self):
        for btn in self.menu_buttons:
            btn.configure(fg_color="transparent", text_color=COLOR_TEXT_SUB)
        for v in self.views.values():
            v.grid_forget()
        
    def highlight_button(self, btn):
        btn.configure(fg_color=COLOR_ACCENT, text_color="white")

    def _load_frame(self, view_key, FrameClass, btn_index=None):
        self.reset_switch_view()
        if btn_index is not None:
            self.highlight_button(self.menu_buttons[btn_index])
        
        if view_key not in self.views:
            self.views[view_key] = FrameClass(self.view_container, self)
        
        # CHỈ GỌI load_data() là đủ, vì các view class đã implement hàm này
        if hasattr(self.views[view_key], 'load_data'):
            self.views[view_key].load_data()

        self.views[view_key].grid(row=0, column=0, sticky="nsew")

    def load_product_dashboard_frame(self):
        self._load_frame('product_dashboard_frame', ProductDashboardFrame, 0)

    def load_employee_dashboard_frame(self):
        self._load_frame('employee_dashboard_frame', EmployeeDashboardFrame, 1)

    def load_cashier_frame(self):
        self._load_frame('cashier_frame', CashierFrame, 2)

    def load_history_frame(self):
        self._load_frame('history_frame', HistoryFrame, 3)

    def load_import_product_frame(self):
        self._load_frame('import_product_frame', ImportProductFrame, 4)

    def load_off_board_frame(self):
        self._load_frame('off_board_frame', OffBoardFrame, 5)

    # --- HÀM LOAD CÁC TRANG ADD/EDIT (Dùng lại highlight của trang cha) ---
    def load_add_product_frame(self):
        self.reset_switch_view()
        self.highlight_button(self.menu_buttons[0])
        if 'add_product' not in self.views:
            self.views['add_product'] = AddProductFrame(self.view_container, self)
        self.views['add_product'].grid(row=0, column=0, sticky="nsew")

    def load_add_employee_frame(self):
        self.reset_switch_view()
        self.highlight_button(self.menu_buttons[1])
        if 'add_employee' not in self.views:
            self.views['add_employee'] = AddEmployeeFrame(self.view_container, self)
        self.views['add_employee'].grid(row=0, column=0, sticky="nsew")

    def load_edit_product_frame(self, product):
        self.reset_switch_view()
        self.highlight_button(self.menu_buttons[0])
        # Luôn tạo mới frame edit để refresh data
        if 'edit_product' in self.views: self.views['edit_product'].destroy()
        self.views['edit_product'] = EditProductFrame(self.view_container, self, product)
        self.views['edit_product'].grid(row=0, column=0, sticky="nsew")

    def load_edit_employee_frame(self, emp):
        self.reset_switch_view()
        self.highlight_button(self.menu_buttons[1])
        if 'edit_employee' in self.views: self.views['edit_employee'].destroy()
        self.views['edit_employee'] = EditEmployeeFrame(self.view_container, self, emp)
        self.views['edit_employee'].grid(row=0, column=0, sticky="nsew")

    def handle_logout(self):
        self.destroy()
        import subprocess
        subprocess.Popen([sys.executable, os.path.join(parent_dir, "seller_app", "login.py")])

if __name__ == "__main__":
    from dataclasses import dataclass
    @dataclass
    class MockUser:
        full_name: str = "Test Admin"
        is_manager: bool = True
    app = BaseApp(MockUser())
    app.mainloop()