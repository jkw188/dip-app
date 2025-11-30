import customtkinter as ctk
from core.dao.order_dao import OrderDAO

class HistoryFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.order_dao = OrderDAO(controller.db.get_connection())
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.setup_filter()
        self.setup_content()

    def setup_filter(self):
        flt = ctk.CTkFrame(self, fg_color="white", height=60)
        flt.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        ctk.CTkLabel(flt, text="FROM:", text_color="black").pack(side="left", padx=(20, 5))
        self.entry_from = ctk.CTkEntry(flt, placeholder_text="YYYY-MM-DD", width=120)
        self.entry_from.pack(side="left")
        
        ctk.CTkLabel(flt, text="TO:", text_color="black").pack(side="left", padx=(20, 5))
        self.entry_to = ctk.CTkEntry(flt, placeholder_text="YYYY-MM-DD", width=120)
        self.entry_to.pack(side="left")
        
        ctk.CTkButton(flt, text="FILTER", width=100, fg_color="#2D3436", command=self.load_data).pack(side="left", padx=30)

    def setup_content(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)
        
        # Left: Invoice List
        left = ctk.CTkFrame(container, fg_color="white")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(left, text="INVOICE HISTORY", font=("Arial", 16, "bold"), text_color="black").pack(pady=10)
        
        self.invoice_list = ctk.CTkScrollableFrame(left, fg_color="white")
        self.invoice_list.pack(fill="both", expand=True, padx=5, pady=5)

        # Right: Revenue
        right = ctk.CTkFrame(container, fg_color="white")
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(right, text="REVENUE SUMMARY", font=("Arial", 16, "bold"), text_color="black").pack(pady=10)
        
        self.lbl_revenue = ctk.CTkLabel(right, text="0 VNĐ", font=("Arial", 30, "bold"), text_color="#00b894")
        self.lbl_revenue.place(relx=0.5, rely=0.5, anchor="center")
        
        self.load_data()

    def load_data(self):
        # Đơn giản hóa: Load tất cả đơn hàng
        for w in self.invoice_list.winfo_children(): w.destroy()
        
        orders = self.order_dao.select_all()
        total_revenue = 0
        
        for order in orders:
            total_revenue += order.total_amount
            
            row = ctk.CTkFrame(self.invoice_list, height=40, fg_color="#F5F6FA")
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=f"#{order.id}", text_color="gray", width=50).pack(side="left")
            ctk.CTkLabel(row, text=order.order_date, text_color="black", width=150).pack(side="left")
            ctk.CTkLabel(row, text=f"{order.total_amount:,.0f}", text_color="#00b894", font=("Arial", 12, "bold")).pack(side="right", padx=10)

        self.lbl_revenue.configure(text=f"{total_revenue:,.0f} VNĐ")