import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import shutil
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from core.dao.product_dao import ProductDAO
from core.dao.product_image_dao import ProductImageDAO
from core.models.product import Product
from core.models.product_image import ProductImage

class EditProductFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, product_data):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.product_data = product_data 
        self.db_conn = controller.db.get_connection()
        
        self.product_dao = ProductDAO(self.db_conn)
        self.image_dao = ProductImageDAO(self.db_conn)
        
        self.selected_image_path = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.setup_ui()
        self.load_current_data()

    def setup_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkButton(header, text="< Back", width=80, fg_color="gray", 
                      command=self.go_back).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(header, text=f"EDIT PRODUCT: {self.product_data.name}", font=("Arial", 24, "bold"), 
                     text_color="#2D3436").pack(side="left")

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        form_wrapper = ctk.CTkFrame(container, width=850, height=600, fg_color="transparent")
        form_wrapper.place(relx=0.5, rely=0.5, anchor="center")
        
        self.form_frame = ctk.CTkScrollableFrame(
            form_wrapper, 
            width=800, 
            height=550, 
            fg_color="white", 
            corner_radius=15
        )
        self.form_frame.pack(fill="both", expand=True)

        self.form_frame.grid_columnconfigure(0, weight=1)
        self.form_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.form_frame, text="Basic Information", font=("Arial", 16, "bold"), text_color="black").grid(row=0, column=0, sticky="w", padx=30, pady=(30, 20))

        self.entry_name = self.create_input(self.form_frame, "Product Name:", 1, 0)
        self.entry_import_price = self.create_input(self.form_frame, "Import Price (VNĐ):", 2, 0)
        self.entry_sale_price = self.create_input(self.form_frame, "Sale Price (VNĐ):", 3, 0)
        self.entry_supplier = self.create_input(self.form_frame, "Supplier:", 4, 0)
        self.entry_shelf_life = self.create_input(self.form_frame, "Shelf Life (Days):", 5, 0)
        self.entry_stock = self.create_input(self.form_frame, "Stock Quantity:", 6, 0)

        ctk.CTkLabel(self.form_frame, text="Details & Image", font=("Arial", 16, "bold"), text_color="black").grid(row=0, column=1, sticky="w", padx=30, pady=(30, 20))

        ctk.CTkLabel(self.form_frame, text="Description:", text_color="gray", font=("Arial", 12)).grid(row=1, column=1, sticky="w", padx=30)
        self.txt_desc = ctk.CTkTextbox(self.form_frame, height=100, border_color="#dfe6e9", border_width=2, fg_color="white", text_color="black")
        self.txt_desc.grid(row=2, column=1, sticky="ew", padx=30, pady=(0, 15))

        self.image_preview = ctk.CTkLabel(self.form_frame, text="No Image", width=200, height=200, fg_color="#F5F6FA", corner_radius=10)
        self.image_preview.grid(row=3, column=1, rowspan=4, padx=30)
        
        btn_select = ctk.CTkButton(self.form_frame, text="Change Image", command=self.choose_image, fg_color="#2D3436")
        btn_select.grid(row=7, column=1, padx=30, pady=10)

        btn_save = ctk.CTkButton(self.form_frame, text="UPDATE PRODUCT", height=45, fg_color="#00b894", 
                                 font=("Arial", 14, "bold"), command=self.update_product)
        btn_save.grid(row=15, column=0, columnspan=2, sticky="ew", padx=30, pady=(20, 20))

    def create_input(self, parent, label, input_order, col):
        base_row = input_order * 2 - 1
        
        ctk.CTkLabel(parent, text=label, text_color="gray", font=("Arial", 12)).grid(row=base_row, column=col, sticky="w", padx=30)
        entry = ctk.CTkEntry(parent, height=35, border_color="#dfe6e9", fg_color="white", text_color="black")
        entry.grid(row=base_row+1, column=col, sticky="ew", padx=30, pady=(0, 15))
        return entry

    def load_current_data(self):
        self.entry_name.insert(0, self.product_data.name)
        self.entry_import_price.insert(0, str(int(self.product_data.import_price)) if self.product_data.import_price else "0")
        self.entry_sale_price.insert(0, str(int(self.product_data.sale_price)))
        self.entry_supplier.insert(0, self.product_data.supplier_info or "")
        self.entry_shelf_life.insert(0, str(self.product_data.shelf_life_days))
        self.entry_stock.insert(0, str(self.product_data.stock_quantity))
        
        if self.product_data.description:
            self.txt_desc.insert("1.0", self.product_data.description)

        try:
            img_record = self.image_dao.select_thumbnail(self.product_data.id)
            if img_record and img_record.image_path:
                abs_path = os.path.join(parent_dir, img_record.image_path)
                if os.path.exists(abs_path):
                    img = ctk.CTkImage(Image.open(abs_path), size=(200, 200))
                    self.image_preview.configure(image=img, text="")
        except Exception as e:
            print(f"Error loading image: {e}")

    def choose_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.selected_image_path = file_path
            try:
                img = ctk.CTkImage(Image.open(file_path), size=(200, 200))
                self.image_preview.configure(image=img, text="")
            except: pass

    def update_product(self):
        name = self.entry_name.get()
        sale_price = self.entry_sale_price.get()
        
        if not name or not sale_price:
            messagebox.showerror("Error", "Name and Price are required!")
            return

        try:
            self.product_data.name = name
            self.product_data.import_price = float(self.entry_import_price.get() or 0)
            self.product_data.sale_price = float(sale_price)
            self.product_data.supplier_info = self.entry_supplier.get()
            self.product_data.shelf_life_days = int(self.entry_shelf_life.get() or 0)
            self.product_data.stock_quantity = int(self.entry_stock.get() or 0)
            self.product_data.description = self.txt_desc.get("1.0", "end").strip()
            
            self.product_dao.update(self.product_data)
            
            if self.selected_image_path:
                dest_dir = os.path.join(parent_dir, "data", "images")
                os.makedirs(dest_dir, exist_ok=True)
                ext = os.path.splitext(self.selected_image_path)[1]
                new_filename = f"prod_{self.product_data.id}{ext}"
                
                shutil.copy(self.selected_image_path, os.path.join(dest_dir, new_filename))
                
                current_img = self.image_dao.select_thumbnail(self.product_data.id)
                new_path = f"data/images/{new_filename}"
                
                if current_img:
                    self.image_dao.delete(current_img.id)
                
                self.image_dao.insert(ProductImage(
                    id=0, product_id=self.product_data.id, 
                    image_path=new_path, 
                    is_thumbnail=True
                ))

            messagebox.showinfo("Success", "Product updated!")
            self.go_back()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def go_back(self):
        self.controller.load_product_dashboard_frame()