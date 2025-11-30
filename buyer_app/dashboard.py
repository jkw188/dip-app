import customtkinter as ctk
import random
from tkinter import messagebox
from PIL import Image
import os
from core.dao.product_dao import ProductDAO

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#FFFFFF")
        self.controller = controller
        self.product_dao = ProductDAO(controller.db.get_connection())
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.setup_ui()
        self.load_products()

    def setup_ui(self):
        # --- 1. NAVBAR (HEADER) ---
        navbar = ctk.CTkFrame(self, height=60, fg_color="white", corner_radius=0)
        navbar.grid(row=0, column=0, sticky="ew")
        
        separator = ctk.CTkFrame(self, height=1, fg_color="#E0E0E0")
        separator.grid(row=0, column=0, sticky="ews", pady=(59, 0))

        # Logo
        brand_frame = ctk.CTkFrame(navbar, fg_color="transparent")
        brand_frame.pack(side="left", padx=20, pady=10)
        ctk.CTkLabel(brand_frame, text="STORE", font=("Arial", 22, "bold"), text_color="black").pack(side="left")
        ctk.CTkLabel(brand_frame, text=f"  |  {self.controller.current_user.full_name}", 
                     font=("Arial", 14), text_color="#555").pack(side="left")

        # Search Bar
        search_frame = ctk.CTkFrame(navbar, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True, padx=20)
        
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Tìm sản phẩm...", 
                                         height=36, width=300, border_color="#333", border_width=1,
                                         fg_color="white", text_color="black")
        self.entry_search.pack(side="left", expand=True, fill="x")
        
        ctk.CTkButton(search_frame, text="Tìm", width=60, height=36, 
                      fg_color="black", text_color="white", hover_color="#333",
                      command=self.search_product).pack(side="left", padx=(5, 0))
        
        ctk.CTkButton(search_frame, text="↻", width=40, height=36, 
                      fg_color="white", text_color="black", border_width=1, border_color="#DDD", hover_color="#F5F5F5",
                      command=self.load_products).pack(side="left", padx=(5, 0))

        # Actions
        action_frame = ctk.CTkFrame(navbar, fg_color="transparent")
        action_frame.pack(side="right", padx=20)

        self.btn_cart = ctk.CTkButton(action_frame, text=f"Giỏ ({len(self.controller.cart)})", width=90, height=36,
                                      fg_color="black", hover_color="#333",
                                      command=self.controller.show_cart)
        self.btn_cart.pack(side="left", padx=5)

        ctk.CTkButton(action_frame, text="Lịch sử", width=80, height=36,
                      fg_color="white", text_color="black", border_width=1, border_color="black", hover_color="#F5F5F5",
                      command=self.controller.show_history).pack(side="left", padx=5)

        ctk.CTkButton(action_frame, text="Thoát", width=60, height=36,
                      fg_color="transparent", text_color="gray", hover_color="#F0F0F0",
                      command=self.controller.logout).pack(side="left", padx=5)

        # --- 2. PRODUCT CONTENT ---
        self.content_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_area.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        self.cols = 4
        for i in range(self.cols):
            self.content_area.grid_columnconfigure(i, weight=1)

    def load_products(self):
        for w in self.content_area.winfo_children(): w.destroy()
        
        all_products = self.product_dao.select_all()
        # Hiển thị tối đa 20 sản phẩm
        display_products = random.sample(all_products, min(len(all_products), 20))
        self.render_grid(display_products)

    def search_product(self):
        keyword = self.entry_search.get()
        if not keyword: 
            self.load_products()
            return
        results = self.product_dao.search_by_name(keyword)
        for w in self.content_area.winfo_children(): w.destroy()
        self.render_grid(results)

    def render_grid(self, products):
        if not products:
            ctk.CTkLabel(self.content_area, text="Không tìm thấy sản phẩm nào.", 
                         text_color="#555", font=("Arial", 16)).pack(pady=50)
            return

        for i, p in enumerate(products):
            row = i // self.cols
            col = i % self.cols
            self.create_card(p, row, col)

    def create_card(self, product, r, c):
        card = ctk.CTkFrame(self.content_area, fg_color="white", border_width=1, border_color="#E5E5E5", corner_radius=8)
        card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew") 
        
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(3, weight=1)

        # --- LOGIC HIỂN THỊ ẢNH ---
        img_path = self.product_dao.get_product_thumbnail(product.id)
        
        # Mặc định là icon nếu không có ảnh hoặc lỗi
        display_image = None
        
        if img_path:
            # Xử lý đường dẫn tương đối
            # Giả định file chạy từ thư mục gốc dự án (ví dụ C:\src\project\dip-app)
            # img_path trong DB dạng: 'data/images/prod_1.jpg'
            full_path = os.path.abspath(img_path) 
            
            if os.path.exists(full_path):
                try:
                    # Load ảnh thật
                    pil_img = Image.open(full_path)
                    display_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(150, 150))
                except Exception as e:
                    print(f"Lỗi load ảnh {full_path}: {e}")
            else:
                print(f"Không tìm thấy file ảnh: {full_path}")

        # Hiển thị ảnh (nếu có) hoặc icon hộp (nếu không)
        if display_image:
            ctk.CTkLabel(card, text="", image=display_image).grid(row=0, column=0, pady=(20, 10))
        else:
            ctk.CTkLabel(card, text="📦", font=("Arial", 48)).grid(row=0, column=0, pady=(20, 10))
        
        # Tên
        ctk.CTkLabel(card, text=product.name, font=("Arial", 14, "bold"), text_color="#222", 
                     wraplength=180).grid(row=1, column=0, padx=15, sticky="ew")
        
        # Giá & Kho
        meta_frame = ctk.CTkFrame(card, fg_color="transparent")
        meta_frame.grid(row=2, column=0, pady=(5, 0))
        ctk.CTkLabel(meta_frame, text=f"{product.sale_price:,.0f} đ", 
                     font=("Arial", 16, "bold"), text_color="black").pack()
        ctk.CTkLabel(meta_frame, text=f"Kho: {product.stock_quantity}", 
                     font=("Arial", 11), text_color="gray").pack()

        # Nút Mua
        btn = ctk.CTkButton(card, text="THÊM VÀO GIỎ", height=35,
                            fg_color="black", hover_color="#444", 
                            font=("Arial", 11, "bold"),
                            command=lambda p=product: self.add_to_cart(p))
        btn.grid(row=4, column=0, sticky="ew", padx=15, pady=20)

    def add_to_cart(self, product):
        if product.stock_quantity <= 0:
            messagebox.showwarning("Hết hàng", "Sản phẩm này tạm thời hết hàng!")
            return
            
        cart = self.controller.cart
        if product.id in cart:
            if cart[product.id]['qty'] < product.stock_quantity:
                cart[product.id]['qty'] += 1
            else:
                messagebox.showwarning("Cảnh báo", "Không đủ số lượng trong kho")
                return
        else:
            cart[product.id] = {'obj': product, 'qty': 1}
        
        self.btn_cart.configure(text=f"Giỏ ({len(cart)})")