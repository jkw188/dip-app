import customtkinter as ctk
from core.dao.product_dao import ProductDAO
from math import ceil

class ProductDashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self.product_dao = ProductDAO(self.controller.db.get_connection())

        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.all_products = [] 

        # Cấu hình Grid: 3 Hàng (Header, Table, Footer)
        self.grid_columnconfigure(0, weight=1)
        # Hàng 1 (Table) chiếm toàn bộ không gian thừa
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=1) # Table
        self.grid_rowconfigure(2, weight=0) # Footer

        self.setup_ui()
        # self.load_data() # BaseApp sẽ gọi

    def setup_ui(self):
        # 1. HEADER
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(header, text="PRODUCT DASHBOARD", font=("Arial", 24, "bold"), text_color="#2D3436").pack(side="left")
        
        right_group = ctk.CTkFrame(header, fg_color="transparent")
        right_group.pack(side="right")
        
        self.entry_search = ctk.CTkEntry(right_group, placeholder_text="Search ID or Name...", width=250)
        self.entry_search.pack(side="left", padx=10)
        self.entry_search.bind("<Return>", lambda e: self.search_product())

        ctk.CTkButton(right_group, text="Search", width=80, fg_color="#2D3436", command=self.search_product).pack(side="left", padx=5)
        ctk.CTkButton(right_group, text="+ NEW PRODUCT", width=120, fg_color="#2D3436").pack(side="left")

        # 2. TABLE AREA (Chứa Header Row + List Rows)
        self.table_container = ctk.CTkFrame(self, fg_color="transparent")
        self.table_container.grid(row=1, column=0, sticky="nsew", padx=20)
        
        # Chia layout cho table_container: Header (cố định), List (co giãn)
        self.table_container.grid_columnconfigure(0, weight=1)
        self.table_container.grid_rowconfigure(0, weight=0) # Header row
        self.table_container.grid_rowconfigure(1, weight=1) # List rows

        # --- Table Header Row ---
        header_row = ctk.CTkFrame(self.table_container, height=40, fg_color="#DFE6E9", corner_radius=5)
        header_row.grid(row=0, column=0, sticky="ew")
        
        columns = [
            ("ID", 50), ("Name", 200), ("Stock", 80), 
            ("Import", 100), ("Sale", 100), ("Supplier", 150),
            ("Expiry", 80), ("Action", 100)
        ]
        
        for name, width in columns:
            lbl = ctk.CTkLabel(header_row, text=name, font=("Arial", 12, "bold"), text_color="black", width=width)
            lbl.pack(side="left", padx=5, fill="x", expand=True)

        # --- List Frame (Thay thế ScrollableFrame) ---
        # Dùng CTkFrame thường để hỗ trợ pack(expand=True)
        self.list_frame = ctk.CTkFrame(self.table_container, fg_color="transparent", corner_radius=0)
        self.list_frame.grid(row=1, column=0, sticky="nsew", pady=(2, 0))

        # 3. FOOTER
        footer = ctk.CTkFrame(self, fg_color="transparent", height=40)
        footer.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
        self.btn_prev = ctk.CTkButton(footer, text="< Prev", width=80, fg_color="#636E72", command=self.prev_page)
        self.btn_prev.pack(side="left")
        
        self.lbl_page = ctk.CTkLabel(footer, text="Page 1 / 1", text_color="black", font=("Arial", 12, "bold"))
        self.lbl_page.pack(side="left", padx=20)
        
        self.btn_next = ctk.CTkButton(footer, text="Next >", width=80, fg_color="#636E72", command=self.next_page)
        self.btn_next.pack(side="left")

    def load_data(self):
        self.all_products = self.product_dao.select_all()
        self.total_pages = ceil(len(self.all_products) / self.items_per_page)
        if self.total_pages == 0: self.total_pages = 1
        self.current_page = 1
        self.render_table()

    def search_product(self):
        keyword = self.entry_search.get().strip()
        if not keyword:
            self.load_data()
            return
        results = self.product_dao.search_by_name(keyword)
        self.all_products = results
        self.total_pages = ceil(len(self.all_products) / self.items_per_page)
        if self.total_pages == 0: self.total_pages = 1
        self.current_page = 1
        self.render_table()

    def render_table(self):
        # Xóa cũ
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        self.lbl_page.configure(text=f"Page {self.current_page} / {self.total_pages}")
        self.btn_prev.configure(state="normal" if self.current_page > 1 else "disabled")
        self.btn_next.configure(state="normal" if self.current_page < self.total_pages else "disabled")

        start = (self.current_page - 1) * self.items_per_page
        end = start + self.items_per_page
        page_data = self.all_products[start:end]

        # 1. Vẽ các dòng dữ liệu thật
        current_rows_count = 0
        if page_data:
            for i, p in enumerate(page_data):
                bg_color = "white" if i % 2 == 0 else "#F0F0F0"
                self.create_row(p, bg_color)
                current_rows_count += 1
        else:
            # Nếu không có dữ liệu, hiện thông báo ở 1 dòng, còn lại là dòng trống
            lbl = ctk.CTkLabel(self.list_frame, text="No products found.", text_color="gray")
            lbl.pack(fill="both", expand=True) # Chiếm 1 slot
            current_rows_count += 1

        # 2. Vẽ các dòng trống (Blank Rows) để lấp đầy trang (Đủ 10 dòng)
        # Điều này ĐẢM BẢO bảng luôn có 10 dòng chia đều chiều cao
        rows_to_fill = self.items_per_page - current_rows_count
        for j in range(rows_to_fill):
            idx = current_rows_count + j
            bg_color = "white" if idx % 2 == 0 else "#F0F0F0"
            self.create_blank_row(bg_color)

    def create_row(self, product, bg_color):
        # QUAN TRỌNG: Không set height cố định, để expand tự chia
        row = ctk.CTkFrame(self.list_frame, fg_color=bg_color, corner_radius=0)
        
        # fill="both", expand=True: Bắt buộc dòng phải giãn ra chiếm không gian
        row.pack(fill="both", expand=True, pady=1)
        
        data = [
            (str(product.id), 50), 
            (product.name, 200), 
            (str(product.stock_quantity), 80), 
            (f"{product.import_price:,.0f}" if product.import_price else "0", 100),
            (f"{product.sale_price:,.0f}", 100),
            (product.supplier_info or "N/A", 150),
            (str(product.shelf_life_days), 80)
        ]
        
        for text, width in data:
            lbl = ctk.CTkLabel(row, text=text, text_color="black", width=width, anchor="center")
            # expand=True cho label để cột cũng giãn đều
            lbl.pack(side="left", padx=5, fill="x", expand=True)
        
        btn_frame = ctk.CTkFrame(row, fg_color="transparent", width=100)
        btn_frame.pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(btn_frame, text="✏️", width=30, height=25, fg_color="#0984e3",
                      command=lambda p=product: self.edit_product(p)).pack(side="left", padx=2)
        
        ctk.CTkButton(btn_frame, text="🗑️", width=30, height=25, fg_color="#d63031",
                      command=lambda p=product: self.delete_product(p)).pack(side="left", padx=2)

    def create_blank_row(self, bg_color):
        # Dòng rỗng cũng phải expand=True để chia đều chiều cao với dòng thật
        row = ctk.CTkFrame(self.list_frame, fg_color=bg_color, corner_radius=0)
        row.pack(fill="both", expand=True, pady=1)

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.render_table()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.render_table()

    def edit_product(self, product):
        print(f"Edit: {product.name}")

    def delete_product(self, product):
        self.product_dao.delete(product.id)
        self.load_data()