import customtkinter as ctk
import random
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import os
import threading
import numpy as np

# Import Core Modules
from core.dao.product_dao import ProductDAO
from core.dao.product_image_dao import ProductImageDAO
from core.camera import Camera
from core.ai_model import FeatureExtractor, VectorSearch

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#FFFFFF")
        self.controller = controller
        self.db_conn = controller.db.get_connection()
        
        # DAO Init
        self.product_dao = ProductDAO(self.db_conn)
        self.image_dao = ProductImageDAO(self.db_conn)
        
        # AI Init (Lazy loading để tránh lag khi mở app)
        self.feature_extractor = None 
        self.db_vectors = None
        
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

        # Search Bar Area
        search_frame = ctk.CTkFrame(navbar, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True, padx=20)
        
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Nhập tên sản phẩm...", 
                                         height=36, width=250, border_color="#333", border_width=1,
                                         fg_color="white", text_color="black")
        self.entry_search.pack(side="left", expand=True, fill="x")
        
        ctk.CTkButton(search_frame, text="🔍 Tìm", width=60, height=36, 
                      fg_color="black", text_color="white", hover_color="#333",
                      command=self.search_product_text).pack(side="left", padx=(5, 0))
        
        # --- NÚT TÌM KIẾM BẰNG ẢNH (AI) ---
        ctk.CTkButton(search_frame, text="📷 Tìm bằng ảnh", width=120, height=36, 
                      fg_color="#0984e3", text_color="white", hover_color="#0069d9",
                      command=self.open_camera_search).pack(side="left", padx=(10, 0))
        
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

    # --- LOGIC TÌM KIẾM BÌNH THƯỜNG ---
    def load_products(self):
        for w in self.content_area.winfo_children(): w.destroy()
        all_products = self.product_dao.select_all()
        # Random để giả lập trang chủ phong phú
        display_products = random.sample(all_products, min(len(all_products), 20))
        self.render_grid(display_products)

    def search_product_text(self):
        keyword = self.entry_search.get()
        if not keyword: 
            self.load_products()
            return
        results = self.product_dao.search_by_name(keyword)
        for w in self.content_area.winfo_children(): w.destroy()
        self.render_grid(results)

    # --- LOGIC AI CAMERA & UPLOAD ---
    def init_ai_model(self):
        """Khởi tạo model AI nếu chưa có (chạy ngầm)"""
        if not self.feature_extractor:
            print("Loading AI Model...")
            self.feature_extractor = FeatureExtractor()
            self.db_vectors = self.image_dao.select_all_vectors()
            print(f"AI Loaded. Vectors in DB: {len(self.db_vectors)}")

    def open_camera_search(self):
        # Tạo popup window
        self.top = ctk.CTkToplevel(self)
        self.top.title("Tìm kiếm bằng hình ảnh")
        self.top.geometry("600x550")
        self.top.grab_set() # Focus vào cửa sổ này

        # Label hiển thị Camera
        self.cam_label = ctk.CTkLabel(self.top, text="Đang khởi động camera...", width=560, height=350, fg_color="black")
        self.cam_label.pack(pady=20)

        # Frame chứa nút bấm
        btn_frame = ctk.CTkFrame(self.top, fg_color="transparent")
        btn_frame.pack(pady=10)

        # Nút Chụp
        self.btn_capture = ctk.CTkButton(btn_frame, text="📸 CHỤP TỪ CAMERA", height=50, width=200, 
                                         fg_color="#d63031", font=("Arial", 14, "bold"),
                                         command=self.capture_and_search)
        self.btn_capture.pack(side="left", padx=10)

        # Nút Upload
        self.btn_upload = ctk.CTkButton(btn_frame, text="📂 TẢI ẢNH LÊN", height=50, width=200, 
                                        fg_color="#0984e3", font=("Arial", 14, "bold"),
                                        command=self.upload_and_search)
        self.btn_upload.pack(side="left", padx=10)

        # Khởi động Camera
        self.camera = Camera()
        try:
            self.camera.start()
            self.update_camera_feed()
        except Exception as e:
            self.cam_label.configure(text=f"Không tìm thấy camera.\nVui lòng sử dụng tính năng Tải ảnh lên.\nLỗi: {e}")
            # Vẫn cho mở popup để dùng tính năng upload
            
        # Khởi tạo AI trong luồng riêng để không đơ UI
        threading.Thread(target=self.init_ai_model, daemon=True).start()

    def update_camera_feed(self):
        if not hasattr(self, 'top') or not self.top.winfo_exists():
            self.camera.stop()
            return

        img_pil, self.current_frame_arr = self.camera.get_frame()
        if img_pil:
            # Resize để fit vào label
            img_pil = img_pil.resize((560, 350))
            img_tk = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(560, 350))
            self.cam_label.configure(image=img_tk, text="")
        
        self.top.after(10, self.update_camera_feed)

    def capture_and_search(self):
        if self.current_frame_arr is None:
            messagebox.showwarning("Lỗi", "Không nhận được hình ảnh từ camera")
            return
        
        # Dừng camera để lấy ảnh tĩnh
        self.camera.stop()
        
        # Convert mảng numpy sang PIL để xử lý thống nhất với upload
        image_pil = Image.fromarray(self.current_frame_arr)
        self.process_search(image_pil)

    def upload_and_search(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
        if not file_path:
            return

        try:
            image_pil = Image.open(file_path)
            # Hiển thị ảnh vừa chọn lên khung camera
            img_preview = image_pil.copy()
            img_preview.thumbnail((560, 350))
            img_tk = ctk.CTkImage(light_image=img_preview, dark_image=img_preview, size=(560, 350))
            self.cam_label.configure(image=img_tk, text="")
            
            # Dừng camera thực nếu đang chạy
            self.camera.stop()
            
            # Thực hiện tìm kiếm
            self.process_search(image_pil)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc file ảnh: {e}")

    def process_search(self, image_pil):
        if not self.feature_extractor:
            messagebox.showinfo("Đang tải", "Hệ thống AI đang khởi động, vui lòng thử lại sau vài giây...")
            return

        try:
            # 1. Trích xuất đặc trưng ảnh
            print("Extracting features...")
            # FeatureExtractor của bạn nhận cả PIL Image
            query_vector = self.feature_extractor.extract(image_pil)
            
            # 2. Cập nhật lại vector DB (phòng trường hợp có sp mới)
            if not self.db_vectors:
                 self.db_vectors = self.image_dao.select_all_vectors()

            # 3. Tìm kiếm Vector
            print("Searching...")
            matched_ids = VectorSearch.search(query_vector, self.db_vectors, top_k=20)
            
            # 4. Hiển thị kết quả
            if matched_ids:
                results = []
                for pid in matched_ids:
                    prod = self.product_dao.select_by_id(pid)
                    if prod: results.append(prod)
                
                self.top.destroy() # Đóng popup
                
                # Render kết quả ra màn hình chính
                for w in self.content_area.winfo_children(): w.destroy()
                ctk.CTkLabel(self.content_area, text=f"🎉 Tìm thấy {len(results)} sản phẩm tương tự:", 
                             font=("Arial", 18, "bold"), text_color="#0984e3").pack(pady=10, anchor="w")
                self.render_grid(results)
            else:
                messagebox.showinfo("Kết quả", "Không tìm thấy sản phẩm nào giống với ảnh chụp!")
        except Exception as e:
            messagebox.showerror("Lỗi AI", str(e))

    # --- RENDER GRID ---
    def render_grid(self, products):
        if not products:
            ctk.CTkLabel(self.content_area, text="Không tìm thấy sản phẩm nào.", 
                         text_color="#555", font=("Arial", 16)).pack(pady=50)
            return

        # Grid logic như cũ
        frame_grid = ctk.CTkFrame(self.content_area, fg_color="transparent")
        frame_grid.pack(fill="both", expand=True)
        for i in range(self.cols):
            frame_grid.grid_columnconfigure(i, weight=1)

        for i, p in enumerate(products):
            row = i // self.cols
            col = i % self.cols
            self.create_card(p, row, col, frame_grid)

    def create_card(self, product, r, c, parent):
        card = ctk.CTkFrame(parent, fg_color="white", border_width=1, border_color="#E5E5E5", corner_radius=8)
        card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew") 
        
        card.grid_columnconfigure(0, weight=1)
        
        # Logic hiển thị ảnh (giữ nguyên như cũ)
        img_path = self.product_dao.get_product_thumbnail(product.id)
        display_image = None
        if img_path:
            full_path = os.path.abspath(img_path) 
            if os.path.exists(full_path):
                try:
                    pil_img = Image.open(full_path)
                    display_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(150, 150))
                except: pass

        if display_image:
            ctk.CTkLabel(card, text="", image=display_image).grid(row=0, column=0, pady=(20, 10))
        else:
            ctk.CTkLabel(card, text="📦", font=("Arial", 48)).grid(row=0, column=0, pady=(20, 10))
        
        ctk.CTkLabel(card, text=product.name, font=("Arial", 14, "bold"), text_color="#222", 
                     wraplength=180).grid(row=1, column=0, padx=15, sticky="ew")
        
        meta_frame = ctk.CTkFrame(card, fg_color="transparent")
        meta_frame.grid(row=2, column=0, pady=(5, 0))
        ctk.CTkLabel(meta_frame, text=f"{product.sale_price:,.0f} đ", font=("Arial", 16, "bold"), text_color="black").pack()
        
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
            cart[product.id]['qty'] += 1
        else:
            cart[product.id] = {'obj': product, 'qty': 1}
        self.btn_cart.configure(text=f"Giỏ ({len(cart)})")