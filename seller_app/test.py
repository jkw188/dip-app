import customtkinter as ctk
from datetime import datetime

# --- CẤU HÌNH MÀU SẮC (THEO ẢNH MẪU) ---
COLOR_BG_MAIN = "#F5F6FA"       # Xám rất nhạt (Nền chính)
COLOR_BG_SIDEBAR = "#FFFFFF"    # Trắng (Nền Sidebar)
COLOR_CARD = "#FFFFFF"          # Trắng (Nền thẻ/Card)
COLOR_TEXT_MAIN = "#2D3436"     # Đen xám (Chữ chính)
COLOR_TEXT_SUB = "#636E72"      # Xám ghi (Chữ phụ)
COLOR_ACCENT = "#2D3436"        # Màu nhấn (Active Menu)
COLOR_HOVER = "#F1F2F6"         # Màu khi di chuột

# Màu pastel cho các Tag trạng thái
COLOR_TAG_GREEN = "#E6F7ED"     # Xanh nhạt
COLOR_TEXT_GREEN = "#00B894"    # Chữ xanh
COLOR_TAG_YELLOW = "#FFFAE6"    # Vàng nhạt
COLOR_TEXT_YELLOW = "#FDCB6E"   # Chữ vàng

class ModernSellerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Cấu hình cửa sổ
        self.title("LINDA - Modern Kitchen Style")
        self.geometry("1200x800")
        ctk.set_appearance_mode("Light")
        
        # Grid: Sidebar (cột 0) cố định, Main (cột 1) co giãn
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR (TRÁI) ---
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=COLOR_BG_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False) # Cố định chiều rộng không cho co lại

        # Logo
        ctk.CTkLabel(self.sidebar, text="☁️ Kitchen", 
                     font=("DM Sans", 22, "bold"), text_color=COLOR_TEXT_MAIN).pack(pady=(40, 10), padx=30, anchor="w")
        
        # Ngày giờ (Giả lập giống ảnh)
        self.time_label = ctk.CTkLabel(self.sidebar, text=datetime.now().strftime("%d Sep %Y\n%I:%M:%S %p"),
                                       font=("DM Sans", 14), text_color=COLOR_TEXT_SUB, justify="left")
        self.time_label.pack(pady=(0, 30), padx=30, anchor="w")

        # Menu Buttons
        self.menu_buttons = []
        # Danh sách menu khớp với dự án của bạn
        menus = [("📦 Products", "ProductsView"), 
                 ("👤 Employees", "EmployeesView"), 
                 ("📝 Orders", "OrdersView"), 
                 ("📥 Import", "ImportView"), 
                 ("🚪 Offboarding", "OffboardingView")]
        
        for text, view_name in menus:
            btn = self.create_menu_button(text, view_name)
            self.menu_buttons.append(btn)

        # User Profile ở dưới cùng
        self.create_user_profile()

        # --- MAIN CONTENT (PHẢI) ---
        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color=COLOR_BG_MAIN)
        self.main_area.grid(row=0, column=1, sticky="nsew")
        
        # Header Status Bar (Các viên thuốc trạng thái ở trên cùng)
        self.create_status_bar()

        # Container chứa các trang con
        self.view_container = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.view_container.pack(fill="both", expand=True, padx=30, pady=20)

        # Khởi tạo các Views
        self.views = {}
        for F in (ProductsView, EmployeesView, OrdersView, ImportView, OffboardingView):
            page_name = F.__name__
            frame = F(parent=self.view_container)
            self.views[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Mặc định chọn trang Orders (để demo giống ảnh nhất)
        self.change_view("OrdersView", self.menu_buttons[2])

    def create_menu_button(self, text, view_name):
        """Tạo nút menu dạng Pill (tròn 2 đầu)"""
        btn = ctk.CTkButton(self.sidebar, 
                            text=text,
                            height=45,
                            corner_radius=12, # Bo góc lớn để tạo hình viên thuốc
                            font=("DM Sans", 15, "bold"),
                            fg_color="transparent",
                            text_color=COLOR_TEXT_SUB,
                            hover_color=COLOR_HOVER,
                            anchor="w",
                            width=200)
        btn.pack(pady=5, padx=20)
        
        # Gán lệnh khi bấm
        btn.configure(command=lambda: self.change_view(view_name, btn))
        return btn

    def create_user_profile(self):
        """Phần hiển thị user ở góc dưới sidebar"""
        profile_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        profile_frame.pack(side="bottom", fill="x", padx=20, pady=30)
        
        # Avatar giả lập
        avatar = ctk.CTkLabel(profile_frame, text="👨‍🍳", font=("Arial", 30))
        avatar.pack(side="left")
        
        info_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        info_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(info_frame, text="Enrico", font=("DM Sans", 14, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w")
        ctk.CTkButton(info_frame, text="Logout", font=("DM Sans", 12), fg_color="transparent", 
                      text_color=COLOR_TEXT_SUB, height=15, width=0, anchor="w", hover=False).pack(anchor="w")

    def create_status_bar(self):
        """Tạo thanh trạng thái dạng chips ở trên cùng"""
        bar = ctk.CTkFrame(self.main_area, fg_color="transparent", height=60)
        bar.pack(fill="x", padx=30, pady=(30, 10))
        
        # Danh sách trạng thái giả lập
        statuses = [("5", "New"), ("5", "Assigned"), ("12", "Cooking"), ("10", "Delivery"), ("85", "Complete")]
        
        for count, label in statuses:
            # Frame con cho từng chip
            chip = ctk.CTkFrame(bar, fg_color=COLOR_CARD, corner_radius=15)
            chip.pack(side="left", padx=(0, 15), ipadx=15, ipady=5)
            
            # Số lượng (Circle)
            count_lbl = ctk.CTkLabel(chip, text=count, width=25, height=25, 
                                     fg_color=COLOR_HOVER, corner_radius=12, # Hình tròn
                                     font=("DM Sans", 12, "bold"))
            count_lbl.pack(side="left", padx=(5, 10))
            
            # Nhãn
            ctk.CTkLabel(chip, text=label, font=("DM Sans", 13), text_color=COLOR_TEXT_MAIN).pack(side="left")

    def change_view(self, view_name, btn_obj):
        # 1. Đổi màu active cho nút
        for btn in self.menu_buttons:
            btn.configure(fg_color="transparent", text_color=COLOR_TEXT_SUB)
        
        # Nút được chọn: Màu đen, chữ trắng (Giống ảnh mục "Orders")
        btn_obj.configure(fg_color=COLOR_ACCENT, text_color="white")

        # 2. Hiển thị trang
        frame = self.views[view_name]
        frame.tkraise()

# --- CÁC TRANG CON (MÔ PHỎNG CARD STYLE) ---

class OrdersView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Tiêu đề mục
        ctk.CTkLabel(self, text="New Orders", font=("DM Sans", 20, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 15))

        # Container cho các thẻ (Grid 2 cột)
        cards_grid = ctk.CTkFrame(self, fg_color="transparent")
        cards_grid.pack(fill="x")
        
        # Tạo 2 thẻ mẫu giống trong ảnh
        self.create_order_card(cards_grid, "Tomas Miller", "#93875", "$13.26", "Seiston Kitchen", "Hemphrey's").grid(row=0, column=0, padx=(0, 20), sticky="ew")
        self.create_order_card(cards_grid, "Stephanie May", "#93876", "$15.29", "Dengeos Glenview", "Dee's Place").grid(row=0, column=1, sticky="ew")

        # Tiêu đề mục 2
        ctk.CTkLabel(self, text="In Progress", font=("DM Sans", 20, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", pady=(30, 15))
        
        # List dọc
        progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        progress_frame.pack(fill="both", expand=True)
        self.create_list_item(progress_frame, "Lucas Pleinsborough", "Cooking", "$15.29").pack(fill="x", pady=5)
        self.create_list_item(progress_frame, "Tommy James", "Out for delivery", "$13.26").pack(fill="x", pady=5)

    def create_order_card(self, parent, name, order_id, total, loc1, loc2):
        """Hàm tạo một Card đơn hàng chi tiết"""
        card = ctk.CTkFrame(parent, fg_color=COLOR_CARD, corner_radius=20)
        
        # Header thẻ
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=15)
        
        # Timer circle (giả lập)
        timer = ctk.CTkLabel(header, text="0:18", width=40, height=40, corner_radius=20, 
                             fg_color="white", text_color="black", font=("Arial", 11, "bold"))
        # Vẽ viền tròn cho timer bằng 1 frame lót (hack trick nhỏ)
        timer_border = ctk.CTkFrame(header, width=44, height=44, corner_radius=22, fg_color="#E0E0E0")
        timer_border.pack(side="left")
        timer.place(in_=timer_border, relx=0.5, rely=0.5, anchor="center")

        info = ctk.CTkFrame(header, fg_color="transparent")
        info.pack(side="left", padx=10)
        ctk.CTkLabel(info, text=name, font=("DM Sans", 14, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(info, text="1006 Wadsworth Dr, Apt 24", font=("DM Sans", 11), text_color=COLOR_TEXT_SUB).pack(anchor="w")
        
        ctk.CTkLabel(header, text=order_id, font=("DM Sans", 11), text_color="#B2BEC3").pack(side="right", anchor="n")

        # Total
        row_total = ctk.CTkFrame(card, fg_color="transparent")
        row_total.pack(fill="x", padx=20)
        ctk.CTkLabel(row_total, text="Total", font=("DM Sans", 12, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="left")
        ctk.CTkLabel(row_total, text=total, font=("DM Sans", 14, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="right")

        # Locations (Màu xanh/vàng nhạt)
        loc_frame = ctk.CTkFrame(card, fg_color="transparent")
        loc_frame.pack(fill="x", padx=20, pady=20)
        
        self.create_tag(loc_frame, loc1, COLOR_TAG_GREEN, COLOR_TEXT_GREEN).pack(side="left", expand=True, fill="x", padx=(0,5))
        self.create_tag(loc_frame, loc2, COLOR_TAG_YELLOW, COLOR_TEXT_YELLOW).pack(side="left", expand=True, fill="x", padx=(5,0))

        return card

    def create_tag(self, parent, text, bg_color, text_color):
        tag = ctk.CTkFrame(parent, fg_color=bg_color, corner_radius=10)
        ctk.CTkLabel(tag, text=text, font=("DM Sans", 11, "bold"), text_color=text_color).pack(padx=10, pady=10)
        return tag
    
    def create_list_item(self, parent, name, status, price):
        """Hàm tạo item danh sách ngang"""
        item = ctk.CTkFrame(parent, fg_color=COLOR_CARD, corner_radius=15, height=60)
        
        ctk.CTkLabel(item, text="🕒", font=("Arial", 20)).pack(side="left", padx=15)
        
        info = ctk.CTkFrame(item, fg_color="transparent")
        info.pack(side="left", pady=10)
        ctk.CTkLabel(info, text=name, font=("DM Sans", 13, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(info, text="Chicken fingers, Large wrap...", font=("DM Sans", 11), text_color=COLOR_TEXT_SUB).pack(anchor="w")

        # Status text màu xanh hoặc đỏ
        color_status = COLOR_TEXT_GREEN if status == "Out for delivery" else "#E17055"
        ctk.CTkLabel(item, text=status, font=("DM Sans", 11), text_color=color_status).pack(side="right", padx=20, anchor="n", pady=10)
        ctk.CTkLabel(item, text=price, font=("DM Sans", 13, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="right", padx=20, anchor="s", pady=10)
        
        return item

# --- CÁC CLASS KHÁC GIỮ NGUYÊN KHUNG ---
class ProductsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        ctk.CTkLabel(self, text="📦 PRODUCTS MANAGEMENT", font=("DM Sans", 24, "bold"), text_color=COLOR_TEXT_MAIN).pack()

class EmployeesView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        ctk.CTkLabel(self, text="👤 EMPLOYEES", font=("DM Sans", 24, "bold"), text_color=COLOR_TEXT_MAIN).pack()

class ImportView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        ctk.CTkLabel(self, text="📥 IMPORT STOCK", font=("DM Sans", 24, "bold"), text_color=COLOR_TEXT_MAIN).pack()

class OffboardingView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        ctk.CTkLabel(self, text="🚪 OFFBOARDING", font=("DM Sans", 24, "bold"), text_color=COLOR_TEXT_MAIN).pack()

if __name__ == "__main__":
    app = ModernSellerApp()
    app.mainloop()