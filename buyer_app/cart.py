import customtkinter as ctk
from tkinter import messagebox

class CartFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#FFFFFF")
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.setup_ui()
        self.render_cart()

    def setup_ui(self):
        # HEADER
        header = ctk.CTkFrame(self, height=60, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkButton(header, text="← MUA SẮM", fg_color="transparent", text_color="black", 
                      font=("Arial", 12, "bold"), anchor="w", hover=False, width=100,
                      command=self.controller.show_dashboard).pack(side="left")
        
        ctk.CTkLabel(header, text="GIỎ HÀNG", font=("Arial", 24, "bold"), text_color="black").pack(side="right")

        # CART LIST CONTAINER
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#FAFAFA") # Nền xám rất nhạt
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # FOOTER
        self.footer = ctk.CTkFrame(self, height=100, fg_color="white", border_width=1, border_color="#E0E0E0")
        self.footer.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        self.lbl_total = ctk.CTkLabel(self.footer, text="TỔNG CỘNG: 0 VNĐ", font=("Arial", 20, "bold"), text_color="black")
        self.lbl_total.pack(side="left", padx=30)
        
        ctk.CTkButton(self.footer, text="THANH TOÁN", font=("Arial", 14, "bold"), 
                      fg_color="black", text_color="white", width=200, height=50, hover_color="#333333",
                      command=self.go_to_payment).pack(side="right", padx=30, pady=20)

    def render_cart(self):
        for w in self.scroll_frame.winfo_children(): w.destroy()
        
        cart = self.controller.cart
        if not cart:
            ctk.CTkLabel(self.scroll_frame, text="Giỏ hàng của bạn đang trống", font=("Arial", 16), text_color="gray").pack(pady=50)
            self.lbl_total.configure(text="TỔNG CỘNG: 0 VNĐ")
            return

        total_money = 0
        for i, (pid, item) in enumerate(list(cart.items())):
            product = item['obj']
            qty = item['qty']
            subtotal = product.sale_price * qty
            total_money += subtotal

            # Item Row
            row = ctk.CTkFrame(self.scroll_frame, fg_color="white", height=80, corner_radius=0)
            row.pack(fill="x", pady=1) # Padding 1 tạo hiệu ứng dòng kẻ
            
            # Name
            ctk.CTkLabel(row, text=product.name, font=("Arial", 14, "bold"), text_color="black", width=300, anchor="w").pack(side="left", padx=20)
            
            # Price
            ctk.CTkLabel(row, text=f"{product.sale_price:,.0f} đ", text_color="gray", width=100).pack(side="left")
            
            # Qty Control (Minimalist)
            qty_frame = ctk.CTkFrame(row, fg_color="transparent")
            qty_frame.pack(side="left", padx=40)
            
            ctk.CTkButton(qty_frame, text="-", width=30, fg_color="white", border_width=1, border_color="#CCC", text_color="black", hover_color="#EEE",
                          command=lambda p=pid: self.change_qty(p, -1)).pack(side="left")
            ctk.CTkLabel(qty_frame, text=str(qty), width=40, text_color="black").pack(side="left")
            ctk.CTkButton(qty_frame, text="+", width=30, fg_color="black", text_color="white", hover_color="#333",
                          command=lambda p=pid: self.change_qty(p, 1)).pack(side="left")

            # Subtotal
            ctk.CTkLabel(row, text=f"{subtotal:,.0f} đ", font=("Arial", 14, "bold"), text_color="black", width=150).pack(side="right", padx=20)

        self.lbl_total.configure(text=f"TỔNG CỘNG: {total_money:,.0f} VNĐ")

    def change_qty(self, pid, delta):
        cart = self.controller.cart
        if pid in cart:
            cart[pid]['qty'] += delta
            if cart[pid]['qty'] <= 0:
                del cart[pid]
            elif cart[pid]['qty'] > cart[pid]['obj'].stock_quantity:
                 cart[pid]['qty'] -= 1
                 messagebox.showwarning("Cảnh báo", "Đã đạt giới hạn kho")
            self.render_cart()

    def go_to_payment(self):
        if not self.controller.cart:
            messagebox.showinfo("Thông báo", "Giỏ hàng trống!")
            return
        self.controller.show_payment()