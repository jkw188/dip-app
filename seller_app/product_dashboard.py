import customtkinter as ctk

class ProductDashboardFrame(ctk.CTkFrame):
    def __init__(self, base, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self.base = base
        self.setup_header()
        self.setup_table_header()
        self.setup_product_list()
        self.setup_pagination()

    def setup_header(self):
        header_frame = ctk.CTkFrame(
            self, 
            fg_color="transparent", 
            height=50)
        header_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            header_frame, 
            text="PRODUCT DASHBOARD", 
            font=("Arial", 24, "bold"), 
            text_color="#2D3436").pack(side="left")

        right_group = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_group.pack(side="right")

        self.entry_search = ctk.CTkEntry(right_group, placeholder_text="Search ID or Name...", width=250)
        self.entry_search.pack(side="left", padx=10)

        ctk.CTkButton(right_group, text="+ NEW PRODUCT", width=120, 
                      fg_color="#2D3436", command=self.open_add_product).pack(side="left")

    def setup_table_header(self):
        self.columns = [
            ("ID", 40), ("Name", 150), ("Stock", 60), 
            ("Import", 90), ("Sale", 90), ("Supplier", 100), 
            ("Expiry", 80), ("Action", 100)
        ]
        header = ctk.CTkFrame(self, height=40, fg_color="#DFE6E9", corner_radius=5)
        header.pack(fill="x", padx=20, pady=(10, 0))
        
        for name, width in self.columns:
            ctk.CTkLabel(header, text=name, font=("Arial", 12, "bold"), 
                         text_color="black", width=width).pack(side="left", padx=5)

    def setup_product_list(self):
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=0)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Mock data
        for i in range(1, 15):
            self.create_row(i, f"Product {i}", 100, 50000, 80000, "Vinamilk", 365)

    def create_row(self, p_id, name, stock, imp, sale, supp, exp):
        row = ctk.CTkFrame(self.scroll_frame, height=40, fg_color="transparent")
        row.pack(fill="x", pady=2)
        
        data = [
            (str(p_id), 40), (name, 150), (str(stock), 60), 
            (f"{imp:,.0f}", 90), (f"{sale:,.0f}", 90), (supp, 100), (str(exp), 80)
        ]
        
        for text, width in data:
            ctk.CTkLabel(row, text=text, text_color="black", width=width).pack(side="left", padx=5)
        
        action_frame = ctk.CTkFrame(row, fg_color="transparent", width=100)
        action_frame.pack(side="left", padx=5)
        
        ctk.CTkButton(action_frame, text="Edit", width=40, height=25, fg_color="#0984e3").pack(side="left", padx=2)
        ctk.CTkButton(action_frame, text="Del", width=40, height=25, fg_color="#d63031").pack(side="left", padx=2)

    def setup_pagination(self):
        footer = ctk.CTkFrame(self, fg_color="transparent", height=40)
        footer.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(footer, text="< Prev", width=80, fg_color="gray").pack(side="left")
        ctk.CTkLabel(footer, text="Page 1 / 5", text_color="black").pack(side="left", padx=20)
        ctk.CTkButton(footer, text="Next >", width=80, fg_color="gray").pack(side="left")

    def open_add_product(self):
        print("Add Product Clicked")