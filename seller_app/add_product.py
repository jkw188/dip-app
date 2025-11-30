import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import shutil
import sys

# Xử lý import đường dẫn
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from core.dao.product_dao import ProductDAO
from core.dao.product_image_dao import ProductImageDAO
from core.models.product import Product
from core.models.product_image import ProductImage
# --- IMPORT QUAN TRỌNG: AI Model ---
from core.ai_model import FeatureExtractor

class AddProductFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.db_conn = controller.db.get_connection()
        
        self.product_dao = ProductDAO(self.db_conn)
        self.image_dao = ProductImageDAO(self.db_conn)
        
        # --- KHỞI TẠO AI MODEL ---
        # Load model MobileNetV2 ngay khi mở màn hình này
        # (Có thể mất 1-2 giây lần đầu, nhưng giúp tìm kiếm sau này)
        try:
            self.feature_extractor = FeatureExtractor()
        except Exception as e:
            print(f"Warning: Không thể tải AI Model: {e}")
            self.feature_extractor = None

        self.selected_image_path = None
        
        # Grid Layout chính
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_ui()

    def setup_ui(self):
        # Header với nút Back
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkButton(header, text="< Back", width=80, fg_color="gray", 
                      command=self.go_back).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(header, text="ADD NEW PRODUCT", font=("Arial", 24, "bold"), 
                     text_color="#2D3436").pack(side="left")

        # Container Form (Màu trắng, bo góc)
        form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        form_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)

        # --- CỘT TRÁI ---
        ctk.CTkLabel(form_frame, text="Basic Information", font=("Arial", 16, "bold"), text_color="black").grid(row=0, column=0, sticky="w", padx=30, pady=(30, 20))

        self.entry_name = self.create_input(form_frame, "Product Name:", 1, 0)
        self.entry_import_price = self.create_input(form_frame, "Import Price (VNĐ):", 2, 0)
        self.entry_sale_price = self.create_input(form_frame, "Sale Price (VNĐ):", 3, 0)
        self.entry_supplier = self.create_input(form_frame, "Supplier:", 4, 0)
        self.entry_shelf_life = self.create_input(form_frame, "Shelf Life (Days):", 5, 0)
        self.entry_stock = self.create_input(form_frame, "Initial Stock:", 6, 0)

        # --- CỘT PHẢI ---
        ctk.CTkLabel(form_frame, text="Details & Image", font=("Arial", 16, "bold"), text_color="black").grid(row=0, column=1, sticky="w", padx=30, pady=(30, 20))

        ctk.CTkLabel(form_frame, text="Description:", text_color="gray", font=("Arial", 12)).grid(row=1, column=1, sticky="w", padx=30)
        self.txt_desc = ctk.CTkTextbox(form_frame, height=100, border_color="#dfe6e9", border_width=2, fg_color="white", text_color="black")
        self.txt_desc.grid(row=2, column=1, sticky="ew", padx=30, pady=(0, 15))

        # Image Preview
        self.image_preview = ctk.CTkLabel(form_frame, text="No Image", width=200, height=200, fg_color="#F5F6FA", corner_radius=10)
        self.image_preview.grid(row=3, column=1, rowspan=4, padx=30)
        
        btn_select = ctk.CTkButton(form_frame, text="Choose Image", command=self.choose_image, fg_color="#2D3436")
        btn_select.grid(row=7, column=1, padx=30, pady=10)

        # Footer Buttons
        btn_save = ctk.CTkButton(form_frame, text="SAVE PRODUCT", height=45, fg_color="#00b894", 
                                 font=("Arial", 14, "bold"), command=self.save_product)
        btn_save.grid(row=8, column=1, sticky="e", padx=30, pady=30)

    def create_input(self, parent, label, row, col):
        ctk.CTkLabel(parent, text=label, text_color="gray", font=("Arial", 12)).grid(row=row*2-1, column=col, sticky="w", padx=30)
        entry = ctk.CTkEntry(parent, height=35, border_color="#dfe6e9", fg_color="white", text_color="black")
        entry.grid(row=row*2, column=col, sticky="ew", padx=30, pady=(0, 15))
        return entry

    def choose_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.selected_image_path = file_path
            try:
                img = ctk.CTkImage(Image.open(file_path), size=(200, 200))
                self.image_preview.configure(image=img, text="")
            except: pass

    def save_product(self):
        name = self.entry_name.get()
        sale_price = self.entry_sale_price.get()
        
        if not name or not sale_price:
            messagebox.showerror("Error", "Name and Price are required!")
            return

        try:
            # 1. Lưu thông tin sản phẩm cơ bản
            new_prod = Product(
                id=0,
                name=name,
                import_price=float(self.entry_import_price.get() or 0),
                sale_price=float(sale_price),
                supplier_info=self.entry_supplier.get(),
                shelf_life_days=int(self.entry_shelf_life.get() or 0),
                stock_quantity=int(self.entry_stock.get() or 0),
                description=self.txt_desc.get("1.0", "end").strip()
            )
            
            prod_id = self.product_dao.insert(new_prod)
            
            # 2. Xử lý ảnh và Vector AI
            if self.selected_image_path:
                # Tạo đường dẫn lưu file
                dest_dir = os.path.join(parent_dir, "data", "images")
                os.makedirs(dest_dir, exist_ok=True)
                ext = os.path.splitext(self.selected_image_path)[1]
                new_filename = f"prod_{prod_id}{ext}"
                dest_path = os.path.join(dest_dir, new_filename)
                
                # Copy ảnh vào thư mục data
                shutil.copy(self.selected_image_path, dest_path)
                
                # --- TÍNH TOÁN VECTOR ĐẶC TRƯNG ---
                vector_blob = None
                if self.feature_extractor:
                    try:
                        print("Đang tính toán vector AI cho sản phẩm mới...")
                        pil_img = Image.open(dest_path)
                        vector = self.feature_extractor.extract(pil_img)
                        vector_blob = vector.tobytes() # Chuyển thành bytes để lưu vào DB
                        print("Đã tạo vector thành công!")
                    except Exception as e:
                        print(f"Lỗi tạo vector AI: {e}")

                # Lưu thông tin ảnh + Vector vào DB
                self.image_dao.insert(ProductImage(
                    id=0, product_id=prod_id, 
                    image_path=f"data/images/{new_filename}", 
                    feature_vector=vector_blob, # Cột này rất quan trọng cho việc tìm kiếm
                    is_thumbnail=True
                ))

            messagebox.showinfo("Success", "Product added successfully!")
            self.go_back() # Quay về Dashboard và reload

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def go_back(self):
        # Gọi hàm chuyển trang của BaseApp để quay lại ProductDashboard
        self.controller.load_product_dashboard_frame()