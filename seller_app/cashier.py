import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
import threading
from PIL import Image
import numpy as np
import os

# Core Modules
from core.dao.product_dao import ProductDAO
from core.dao.order_dao import OrderDAO
from core.dao.order_detail_dao import OrderDetailDAO
from core.dao.product_image_dao import ProductImageDAO
from core.models.order import Order
from core.models.order_detail import OrderDetail

# AI Modules
from core.camera import Camera
from core.ai_model import FeatureExtractor, VectorSearch

class CashierFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.db_conn = controller.db.get_connection()
        
        # Init DAOs
        self.product_dao = ProductDAO(self.db_conn)
        self.order_dao = OrderDAO(self.db_conn)
        self.detail_dao = OrderDetailDAO(self.db_conn)
        self.image_dao = ProductImageDAO(self.db_conn)
        
        # Init AI
        self.camera = Camera()
        self.feature_extractor = None
        self.db_vectors = None
        self.current_frame_arr = None
        
        self.cart = {} 

        self.grid_columnconfigure(0, weight=2) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)

        self.setup_left_panel()
        self.setup_right_panel()

        # Khởi động AI ngầm
        threading.Thread(target=self.init_ai, daemon=True).start()

    def init_ai(self):
        if not self.feature_extractor:
            self.feature_extractor = FeatureExtractor()
            self.db_vectors = self.image_dao.select_all_vectors()
            print("Seller AI Ready.")

    def setup_left_panel(self):
        left_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(0, weight=0) # Camera area
        left_frame.grid_rowconfigure(2, weight=1) # Product list

        # 1. Header Search
        search_frame = ctk.CTkFrame(left_frame, fg_color="transparent", height=50)
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(search_frame, text="CASHIER", font=("Arial", 20, "bold"), text_color="black").pack(side="left", padx=10)
        
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="ID hoặc Tên SP...", width=200)
        self.entry_search.pack(side="right", padx=5)
        self.entry_search.bind("<Return>", lambda e: self.search_product_text())
        ctk.CTkButton(search_frame, text="Tìm", width=60, fg_color="#2D3436", command=self.search_product_text).pack(side="right")

        # 2. CAMERA & AI SECTION
        cam_container = ctk.CTkFrame(left_frame, fg_color="#F0F0F0", corner_radius=10)
        cam_container.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        # Preview Label
        self.cam_preview = ctk.CTkLabel(cam_container, text="Camera Off", width=400, height=250, fg_color="black", text_color="white")
        self.cam_preview.pack(pady=10)
        
        btn_row = ctk.CTkFrame(cam_container, fg_color="transparent")
        btn_row.pack(pady=(0, 10))
        
        self.btn_toggle_cam = ctk.CTkButton(btn_row, text="Bật Camera", width=100, command=self.toggle_camera)
        self.btn_toggle_cam.pack(side="left", padx=5)
        
        self.btn_scan = ctk.CTkButton(btn_row, text="📸 QUÉT NGAY", width=120, fg_color="#d63031", state="disabled", command=self.scan_and_add)
        self.btn_scan.pack(side="left", padx=5)

        # Nút Upload Mới
        self.btn_upload = ctk.CTkButton(btn_row, text="📂 UPLOAD", width=100, fg_color="#0984e3", command=self.upload_and_scan)
        self.btn_upload.pack(side="left", padx=5)

        # 3. Product Grid
        self.product_grid = ctk.CTkScrollableFrame(left_frame, fg_color="#F5F6FA")
        self.product_grid.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        
        self.load_products_to_grid()

    # --- CAMERA LOGIC ---
    def toggle_camera(self):
        if not self.camera.is_running:
            try:
                self.camera.start()
                self.btn_toggle_cam.configure(text="Tắt Camera", fg_color="gray")
                self.btn_scan.configure(state="normal")
                self.update_camera_feed()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
        else:
            self.camera.stop()
            self.btn_toggle_cam.configure(text="Bật Camera", fg_color="#3B8ED0")
            self.btn_scan.configure(state="disabled")
            self.cam_preview.configure(image=None, text="Camera Off")

    def update_camera_feed(self):
        if not self.camera.is_running: return
        
        if not self.winfo_exists():
            self.camera.stop()
            return

        img_pil, frame_arr = self.camera.get_frame()
        if img_pil:
            self.current_frame_arr = frame_arr
            img_pil = img_pil.resize((400, 250))
            img_tk = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(400, 250))
            self.cam_preview.configure(image=img_tk, text="")
        
        self.after(20, self.update_camera_feed)

    def scan_and_add(self):
        if self.current_frame_arr is None: return
        
        # Convert to PIL for consistency
        image_pil = Image.fromarray(self.current_frame_arr)
        self.process_image_search(image_pil)

    def upload_and_scan(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
        if not file_path:
            return

        try:
            image_pil = Image.open(file_path)
            
            # Hiển thị preview ảnh upload
            img_preview = image_pil.copy()
            img_preview.thumbnail((400, 250))
            img_tk = ctk.CTkImage(light_image=img_preview, dark_image=img_preview, size=(400, 250))
            self.cam_preview.configure(image=img_tk, text="")
            
            # Nếu đang mở camera thì tắt đi
            if self.camera.is_running:
                self.toggle_camera()

            self.process_image_search(image_pil)
        except Exception as e:
            messagebox.showerror("Lỗi file", str(e))

    def process_image_search(self, image_pil):
        if not self.feature_extractor:
            messagebox.showinfo("Chờ chút", "AI đang khởi động...")
            return

        # 1. AI Processing
        query_vec = self.feature_extractor.extract(image_pil)
        
        if not self.db_vectors:
             self.db_vectors = self.image_dao.select_all_vectors()

        # 2. Search Top 5 (Thay vì Top 1)
        matched_ids = VectorSearch.search(query_vec, self.db_vectors, top_k=5)
        
        if matched_ids:
            # Lấy danh sách sản phẩm từ IDs
            products = []
            for pid in matched_ids:
                p = self.product_dao.select_by_id(pid)
                if p: products.append(p)
            
            if products:
                # Hiển thị Popup chọn lựa
                self.show_selection_popup(products)
            else:
                messagebox.showwarning("Lỗi", "Không tìm thấy dữ liệu sản phẩm tương ứng.")
        else:
            messagebox.showwarning("Không tìm thấy", "Không nhận diện được sản phẩm nào giống ảnh.")

    def show_selection_popup(self, products):
        """Hiển thị cửa sổ con để chọn sản phẩm"""
        top = ctk.CTkToplevel(self)
        top.title("Kết quả tìm kiếm AI")
        top.geometry("600x500")
        top.grab_set() # Focus vào cửa sổ này, chặn thao tác cửa sổ chính

        ctk.CTkLabel(top, text=f"Tìm thấy {len(products)} sản phẩm tương tự:", 
                     font=("Arial", 16, "bold"), text_color="#0984e3").pack(pady=10)

        scroll_frame = ctk.CTkScrollableFrame(top, fg_color="white")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        for p in products:
            row = ctk.CTkFrame(scroll_frame, fg_color="#F9F9F9", border_width=1, border_color="#E0E0E0")
            row.pack(fill="x", pady=5)

            # Icon/Image
            # Logic load ảnh thumbnail nhỏ
            img_path = self.product_dao.get_product_thumbnail(p.id)
            display_image = None
            if img_path:
                # Đường dẫn tương đối từ thư mục chạy
                # Cần xử lý đường dẫn tuyệt đối cẩn thận
                try:
                    full_path = os.path.abspath(img_path)
                    if os.path.exists(full_path):
                        pil = Image.open(full_path)
                        display_image = ctk.CTkImage(pil, size=(50, 50))
                except: pass
            
            if display_image:
                ctk.CTkLabel(row, text="", image=display_image, width=60).pack(side="left", padx=5)
            else:
                ctk.CTkLabel(row, text="📦", font=("Arial", 24), width=60).pack(side="left", padx=5)

            # Info
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", padx=10, fill="x", expand=True)
            ctk.CTkLabel(info, text=p.name, font=("Arial", 14, "bold"), text_color="black").pack(anchor="w")
            ctk.CTkLabel(info, text=f"Kho: {p.stock_quantity} | Giá: {p.sale_price:,.0f} đ", text_color="gray").pack(anchor="w")

            # Button Select
            ctk.CTkButton(row, text="CHỌN", width=80, fg_color="#00b894",
                          command=lambda prod=p: [self.add_to_cart(prod), top.destroy()]).pack(side="right", padx=10)

        ctk.CTkButton(top, text="Đóng", fg_color="gray", command=top.destroy).pack(pady=10)

    # --- EXISTING LOGIC ---
    def load_products_to_grid(self, keyword=None):
        for widget in self.product_grid.winfo_children(): widget.destroy()
        
        if keyword:
            try:
                p_id = int(keyword)
                product = self.product_dao.select_by_id(p_id)
                products = [product] if product else []
            except ValueError:
                products = self.product_dao.search_by_name(keyword)
        else:
            products = self.product_dao.select_all()

        for p in products: self.create_product_card(p)

    def search_product_text(self):
        kw = self.entry_search.get().strip()
        self.load_products_to_grid(kw)

    def create_product_card(self, product):
        card = ctk.CTkFrame(self.product_grid, fg_color="white", corner_radius=8, height=60)
        card.pack(fill="x", pady=5)
        
        ctk.CTkLabel(card, text="📦", font=("Arial", 24)).pack(side="left", padx=10)
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", padx=10)
        ctk.CTkLabel(info, text=product.name, text_color="black", font=("Arial", 14, "bold")).pack(anchor="w")
        ctk.CTkLabel(info, text=f"Stock: {product.stock_quantity}", text_color="gray", font=("Arial", 11)).pack(anchor="w")
        
        btn_add = ctk.CTkButton(card, text="ADD +", width=60, height=30, fg_color="#00b894",
                                command=lambda p=product: self.add_to_cart(p))
        btn_add.pack(side="right", padx=10)
        ctk.CTkLabel(card, text=f"{product.sale_price:,.0f} đ", text_color="#00b894", font=("Arial", 14, "bold")).pack(side="right", padx=10)

    def setup_right_panel(self):
        right_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(right_frame, text="CURRENT ORDER", font=("Arial", 18, "bold"), text_color="black").grid(row=0, column=0, pady=15)
        self.bill_list = ctk.CTkScrollableFrame(right_frame, fg_color="#F5F6FA")
        self.bill_list.grid(row=1, column=0, sticky="nsew", padx=10)

        total_frame = ctk.CTkFrame(right_frame, fg_color="#2D3436", height=120, corner_radius=10)
        total_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        ctk.CTkLabel(total_frame, text="TOTAL:", text_color="white", font=("Arial", 16)).pack(anchor="w", padx=20, pady=(15, 5))
        self.lbl_total_money = ctk.CTkLabel(total_frame, text="0", text_color="#00b894", font=("Arial", 28, "bold"))
        self.lbl_total_money.pack(anchor="e", padx=20)

        ctk.CTkButton(right_frame, text="PAY (THANH TOÁN)", height=50, fg_color="#00b894", 
                      font=("Arial", 16, "bold"), hover_color="#00a884",
                      command=self.process_payment).grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 20))

    def add_to_cart(self, product):
        if product.stock_quantity <= 0:
            messagebox.showwarning("Warning", "Out of stock!")
            return
        if product.id in self.cart:
            if self.cart[product.id]['qty'] < product.stock_quantity:
                self.cart[product.id]['qty'] += 1
            else:
                messagebox.showwarning("Limit", "Not enough stock!")
        else:
            self.cart[product.id] = {'obj': product, 'qty': 1}
        self.render_cart()

    def render_cart(self):
        for widget in self.bill_list.winfo_children(): widget.destroy()
        total_money = 0
        for pid, item in list(self.cart.items()):
            product = item['obj']
            qty = item['qty']
            subtotal = product.sale_price * qty
            total_money += subtotal
            
            row = ctk.CTkFrame(self.bill_list, fg_color="white", height=50)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=product.name, text_color="black", width=100, anchor="w").pack(side="left", padx=5)
            ctk.CTkButton(row, text="-", width=30, fg_color="gray", command=lambda p=pid: self.change_qty(p, -1)).pack(side="left")
            ctk.CTkLabel(row, text=str(qty), text_color="black", width=30).pack(side="left")
            ctk.CTkButton(row, text="+", width=30, fg_color="gray", command=lambda p=pid: self.change_qty(p, 1)).pack(side="left")
            ctk.CTkLabel(row, text=f"{subtotal:,.0f}", text_color="black", font=("Arial", 12, "bold")).pack(side="right", padx=10)
        self.lbl_total_money.configure(text=f"{total_money:,.0f} VNĐ")

    def change_qty(self, pid, delta):
        if pid in self.cart:
            self.cart[pid]['qty'] += delta
            if self.cart[pid]['qty'] <= 0: del self.cart[pid]
            elif delta > 0:
                prod = self.cart[pid]['obj']
                if self.cart[pid]['qty'] > prod.stock_quantity:
                    self.cart[pid]['qty'] -= 1
                    messagebox.showwarning("Limit", "Not enough stock!")
            self.render_cart()

    def process_payment(self):
        if not self.cart:
            messagebox.showinfo("Empty", "Cart is empty!")
            return
        total = sum([item['obj'].sale_price * item['qty'] for item in self.cart.values()])
        if messagebox.askyesno("Confirm Payment", f"Pay {total:,.0f} VNĐ via Cash?"):
            try:
                new_order = Order(
                    id=0, total_amount=total,
                    employee_id=self.controller.current_user.id,
                    order_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    status="completed"
                )
                order_id = self.order_dao.insert(new_order)
                for pid, item in self.cart.items():
                    prod = item['obj']
                    qty = item['qty']
                    detail = OrderDetail(id=0, order_id=order_id, product_id=pid, quantity=qty, unit_price=prod.sale_price)
                    self.detail_dao.insert(detail)
                    prod.stock_quantity -= qty
                    self.product_dao.update(prod)
                
                messagebox.showinfo("Success", f"Payment successful! Order #{order_id}")
                self.cart = {}
                self.render_cart()
                self.load_products_to_grid()
                
            except Exception as e:
                messagebox.showerror("Error", str(e))