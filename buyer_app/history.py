import customtkinter as ctk
from core.dao.order_dao import OrderDAO

class HistoryFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F9F9F9")
        self.controller = controller
        self.order_dao = OrderDAO(controller.db.get_connection())
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.setup_ui()
        self.load_history()

    def setup_ui(self):
        header = ctk.CTkFrame(self, height=60, fg_color="white")
        header.grid(row=0, column=0, sticky="ew")
        
        ctk.CTkButton(header, text="← TRANG CHỦ", fg_color="transparent", text_color="black", width=100, anchor="w", hover=False, font=("Arial", 12, "bold"),
                      command=self.controller.show_dashboard).pack(side="left", padx=20, pady=10)
        
        ctk.CTkLabel(header, text="LỊCH SỬ ĐƠN HÀNG", font=("Arial", 20, "bold"), text_color="black").pack(side="right", padx=30)

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def load_history(self):
        for w in self.scroll_frame.winfo_children(): w.destroy()
        
        all_orders = self.order_dao.select_all()
        # Lọc đơn (Demo logic: Lấy đơn pending hoặc employee_id=0)
        my_orders = [o for o in all_orders if o.status == "pending" or getattr(o, 'employee_id', None) == 0]
        
        if not my_orders:
            ctk.CTkLabel(self.scroll_frame, text="Bạn chưa có đơn hàng nào.", text_color="gray").pack(pady=20)
            return

        for order in my_orders:
            card = ctk.CTkFrame(self.scroll_frame, fg_color="white", height=60, border_width=1, border_color="#E0E0E0")
            card.pack(fill="x", pady=5)
            
            ctk.CTkLabel(card, text=f"#{order.id}", font=("Arial", 14, "bold"), text_color="black", width=80).pack(side="left", padx=20)
            ctk.CTkLabel(card, text=f"{order.order_date}", text_color="gray", width=150).pack(side="left")
            
            # Status Chip
            status_color = "#444" if order.status == "pending" else "black"
            ctk.CTkLabel(card, text=order.status.upper(), text_color="white", fg_color=status_color, corner_radius=5, width=80).pack(side="right", padx=20)
            
            ctk.CTkLabel(card, text=f"{order.total_amount:,.0f} đ", text_color="black", font=("Arial", 14, "bold")).pack(side="right", padx=20)