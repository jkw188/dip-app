import customtkinter as ctk

class PaymentFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="white")
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        # Header
        ctk.CTkButton(self, text="← Quay lại", fg_color="transparent", text_color="black", width=100, anchor="w", hover=False,
                      command=self.controller.show_cart).pack(anchor="w", padx=40, pady=30)
        
        container = ctk.CTkFrame(self, fg_color="#FAFAFA", width=600, corner_radius=0, border_width=1, border_color="#E0E0E0")
        container.pack(pady=0, fill="y", padx=40, ipadx=20, ipady=20)
        
        ctk.CTkLabel(container, text="XÁC NHẬN THANH TOÁN", font=("Arial", 22, "bold"), text_color="black").pack(pady=(20, 30))

        # Thông tin khách hàng
        user = self.controller.current_user
        
        info_frame = ctk.CTkFrame(container, fg_color="white", border_width=1, border_color="#EEE")
        info_frame.pack(fill="x", padx=20, pady=10, ipady=10)
        
        self.create_info_row(info_frame, "Khách hàng:", user.full_name)
        self.create_info_row(info_frame, "Số điện thoại:", user.phone)
        self.create_info_row(info_frame, "Địa chỉ nhận:", user.address)

        # Tổng tiền
        total = sum([item['obj'].sale_price * item['qty'] for item in self.controller.cart.values()])
        
        total_frame = ctk.CTkFrame(container, fg_color="transparent")
        total_frame.pack(fill="x", padx=20, pady=30)
        
        ctk.CTkLabel(total_frame, text="TỔNG THANH TOÁN", font=("Arial", 14), text_color="gray").pack(side="left")
        ctk.CTkLabel(total_frame, text=f"{total:,.0f} VNĐ", font=("Arial", 24, "bold"), text_color="black").pack(side="right")

        # Nút xác nhận
        ctk.CTkButton(container, text="XÁC NHẬN ĐẶT HÀNG", width=300, height=50, 
                      fg_color="black", text_color="white", font=("Arial", 14, "bold"), hover_color="#333",
                      command=self.controller.show_confirm_payment).pack(pady=20)

    def create_info_row(self, parent, label, value):
        row = ctk.CTkFrame(parent, fg_color="transparent", height=30)
        row.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(row, text=label, text_color="gray", width=100, anchor="w").pack(side="left")
        ctk.CTkLabel(row, text=value, text_color="black", font=("Arial", 13, "bold"), anchor="w").pack(side="left")