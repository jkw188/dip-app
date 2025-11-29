import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import cv2
import os
import shutil
import hashlib
from datetime import datetime

# Import module core
from core.database import Database
# from core.ai_model import FeatureExtractor # Bỏ comment khi bạn đã code xong AI

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Đăng nhập - Hệ thống quản lý")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Kết nối DB
        self.db = Database()

        # UI Components
        self.label_title = ctk.CTkLabel(self, text="SELLER APP", font=("Arial", 24, "bold"))
        self.label_title.pack(pady=40)

        self.entry_user = ctk.CTkEntry(self, placeholder_text="Tên đăng nhập", width=250)
        self.entry_user.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(self, placeholder_text="Mật khẩu", show="*", width=250)
        self.entry_pass.pack(pady=10)

        self.btn_login = ctk.CTkButton(self, text="Đăng nhập", width=250, command=self.handle_login)
        self.btn_login.pack(pady=20)

    def handle_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        # Hash password để so sánh với DB
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()

        # Query kiểm tra (Dùng bảng employees)
        try:
            cursor = self.db.conn.cursor()
            user = cursor.execute(
                "SELECT * FROM employees WHERE username=? AND password_hash=?", 
                (username, pwd_hash)
            ).fetchone()

            if user:
                self.destroy() # Đóng cửa sổ login
                app = SellerApp(user) # Mở app chính
                app.mainloop()
            else:
                messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu!")
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", str(e))

class SellerApp(ctk.CTk):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info # Lưu thông tin người đang đăng nhập
        self.title(f"Hệ thống bán hàng - Xin chào: {user_info[3]}")
        self.geometry("1000x700")
        
        # Cấu hình layout (Chia 2 cột: Menu trái, Nội dung phải)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_area()
        
        # Mặc định hiện trang Quản lý sản phẩm
        self.show_product_frame()

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="MENU", font=("Arial", 20, "bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        self.btn_products = ctk.CTkButton(self.sidebar, text="Quản lý Sản phẩm", command=self.show_product_frame)
        self.btn_products.grid(row=1, column=0, padx=20, pady=10)

        self.btn_search = ctk.CTkButton(self.sidebar, text="Tìm kiếm bằng Camera", command=self.show_search_frame)
        self.btn_search.grid(row=2, column=0, padx=20, pady=10)
        
        self.btn_logout = ctk.CTkButton(self.sidebar, text="Đăng xuất", fg_color="red", command=self.logout)
        self.btn_logout.grid(row=9, column=0, padx=20, pady=20, sticky="s")

    def setup_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def logout(self):
        self.destroy()
        # Mở lại login (Code khởi chạy ở dưới cùng)

    # ---------------------------------------------------------
    # CHỨC NĂNG 1: QUẢN LÝ SẢN PHẨM (CRUD)
    # ---------------------------------------------------------
    def show_product_frame(self):
        self.clear_main_frame()
        
        # Tiêu đề
        lbl = ctk.CTkLabel(self.main_frame, text="THÊM SẢN PHẨM MỚI", font=("Arial", 20))
        lbl.pack(pady=10)

        # Form nhập liệu
        form_frame = ctk.CTkFrame(self.main_frame)
        form_frame.pack(pady=10, padx=20, fill="x")

        self.entry_name = ctk.CTkEntry(form_frame, placeholder_text="Tên sản phẩm")
        self.entry_name.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.entry_price = ctk.CTkEntry(form_frame, placeholder_text="Giá bán (VNĐ)")
        self.entry_price.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.entry_shelf_life = ctk.CTkEntry(form_frame, placeholder_text="Hạn sử dụng (số ngày)")
        self.entry_shelf_life.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.entry_desc = ctk.CTkEntry(form_frame, placeholder_text="Mô tả chi tiết")
        self.entry_desc.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Chọn ảnh
        self.btn_img = ctk.CTkButton(form_frame, text="Chọn ảnh sản phẩm", command=self.select_image)
        self.btn_img.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.lbl_img_path = ctk.CTkLabel(form_frame, text="Chưa chọn ảnh")
        self.lbl_img_path.grid(row=3, column=0, columnspan=2)
        self.selected_image_path = None

        # Nút Lưu
        btn_save = ctk.CTkButton(self.main_frame, text="Lưu sản phẩm", fg_color="green", command=self.save_product)
        btn_save.pack(pady=20)

    def select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if file_path:
            self.selected_image_path = file_path
            self.lbl_img_path.configure(text=os.path.basename(file_path))

    def save_product(self):
        # 1. Lấy dữ liệu từ Form
        name = self.entry_name.get()
        price = self.entry_price.get()
        shelf_life = self.entry_shelf_life.get()
        desc = self.entry_desc.get()

        if not name or not price:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tên và giá!")
            return

        try:
            db = Database()
            cursor = db.conn.cursor()

            # 2. Insert vào bảng PRODUCTS
            # (id, name, description, supplier_info, import_price, sale_price, stock, shelf_life_days)
            cursor.execute("""
                INSERT INTO products (name, sale_price, shelf_life_days, description)
                VALUES (?, ?, ?, ?)
            """, (name, float(price), int(shelf_life) if shelf_life else 0, desc))
            
            product_id = cursor.lastrowid # Lấy ID sản phẩm vừa tạo

            # 3. Xử lý ảnh & Insert vào bảng PRODUCT_IMAGES
            if self.selected_image_path:
                # Copy ảnh vào thư mục dự án
                dest_folder = "data/images"
                os.makedirs(dest_folder, exist_ok=True)
                ext = os.path.splitext(self.selected_image_path)[1]
                new_filename = f"prod_{product_id}{ext}"
                dest_path = os.path.join(dest_folder, new_filename)
                
                shutil.copy(self.selected_image_path, dest_path)

                # TODO: Tại đây sẽ gọi AI Model để trích xuất Vector
                # vector = ai_model.extract(dest_path) 
                # binary_vector = db.adapt_array(vector)
                binary_vector = None # Tạm thời để Null để test GUI trước

                cursor.execute("""
                    INSERT INTO product_images (product_id, image_path, feature_vector, is_thumbnail)
                    VALUES (?, ?, ?, 1)
                """, (product_id, dest_path, binary_vector))

            db.conn.commit()
            messagebox.showinfo("Thành công", "Đã thêm sản phẩm thành công!")
            self.show_product_frame() # Reset form

        except Exception as e:
            messagebox.showerror("Lỗi CSDL", str(e))

    # ---------------------------------------------------------
    # CHỨC NĂNG 2: TÌM KIẾM BẰNG CAMERA (OpenCV Integration)
    # ---------------------------------------------------------
    def show_search_frame(self):
        self.clear_main_frame()

        lbl = ctk.CTkLabel(self.main_frame, text="TÌM KIẾM BẰNG HÌNH ẢNH", font=("Arial", 20))
        lbl.pack(pady=10)

        # Khung chứa Camera
        self.camera_frame = ctk.CTkLabel(self.main_frame, text="")
        self.camera_frame.pack(pady=10)

        # Nút Chụp
        btn_capture = ctk.CTkButton(self.main_frame, text="Chụp & Tìm kiếm", command=self.capture_and_search)
        btn_capture.pack(pady=10)

        # Khởi động Camera
        self.cap = cv2.VideoCapture(0)
        self.update_camera()

    def update_camera(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Chuyển BGR (OpenCV) -> RGB (Pillow)
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                # Resize cho vừa khung
                img = img.resize((400, 300))
                imgtk = ImageTk.PhotoImage(image=img)
                
                self.camera_frame.configure(image=imgtk)
                self.camera_frame.image = imgtk # Giữ tham chiếu để không bị Garbage Collection
            
            # Gọi lại hàm này sau 10ms
            self.after(10, self.update_camera)

    def capture_and_search(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Lưu ảnh tạm
                filename = "temp_search.jpg"
                cv2.imwrite(filename, frame)
                
                # TODO: Gọi hàm tìm kiếm AI ở đây
                # results = ai_engine.search(filename)
                
                messagebox.showinfo("Thông báo", "Đã chụp ảnh! (Tính năng tìm kiếm đang phát triển)")

    # Dừng camera khi chuyển trang hoặc đóng app
    def clear_main_frame(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        super().clear_main_frame()

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    # Tạo thư mục dữ liệu nếu chưa có
    os.makedirs("data/db", exist_ok=True)
    os.makedirs("data/images", exist_ok=True)
    
    # Chạy màn hình đăng nhập trước
    login_window = LoginWindow()
    login_window.mainloop()