import customtkinter as ctk
from tkinter import messagebox
import hashlib
from datetime import datetime
from core.dao.order_dao import OrderDAO
from core.dao.order_detail_dao import OrderDetailDAO
from core.dao.product_dao import ProductDAO
from core.models.order import Order
from core.models.order_detail import OrderDetail

class ConfirmPaymentFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="white")
        self.controller = controller
        self.db_conn = controller.db.get_connection()
        self.order_dao = OrderDAO(self.db_conn)
        self.detail_dao = OrderDetailDAO(self.db_conn)
        self.product_dao = ProductDAO(self.db_conn)
        
        self.setup_ui()

    def setup_ui(self):
        # Modal
        card = ctk.CTkFrame(self, fg_color="white", width=400, height=300, corner_radius=8, border_width=1, border_color="#CCC")
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        ctk.CTkLabel(card, text="🔒 BẢO MẬT", font=("Arial", 18, "bold"), text_color="black").pack(pady=(40, 10))
        ctk.CTkLabel(card, text="Nhập mật khẩu để xác nhận giao dịch", text_color="gray").pack(pady=5)
        
        self.entry_pass = ctk.CTkEntry(card, show="*", width=250, height=40, fg_color="#FAFAFA", border_color="#DDD", text_color="black")
        self.entry_pass.pack(pady=20)

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(pady=10)
        
        ctk.CTkButton(btn_row, text="HỦY", fg_color="white", text_color="black", border_width=1, border_color="#CCC", width=100,
                      command=self.controller.show_payment).pack(side="left", padx=10)
        
        ctk.CTkButton(btn_row, text="XÁC NHẬN", fg_color="black", text_color="white", width=100, hover_color="#333",
                      command=self.process_transaction).pack(side="left", padx=10)

    def process_transaction(self):
        pwd = self.entry_pass.get()
        pwd_hash = hashlib.sha256(pwd.encode()).hexdigest()

        if pwd_hash != self.controller.current_user.password_hash:
            messagebox.showerror("Lỗi", "Mật khẩu không đúng!")
            return

        try:
            total = sum([item['obj'].sale_price * item['qty'] for item in self.controller.cart.values()])
            
            # --- FIX LỖI FOREIGN KEY TẠI ĐÂY ---
            new_order = Order(
                id=0,
                total_amount=total,
                # 1. Truyền ID khách hàng hiện tại
                customer_id=self.controller.current_user.id, 
                # 2. Truyền None thay vì 0. DB sẽ lưu là NULL (hợp lệ vì không có nhân viên tạo đơn này)
                employee_id=None, 
                order_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                status="pending"
            )
            
            order_id = self.order_dao.insert(new_order) 

            # Detail & Trừ kho
            for pid, item in self.controller.cart.items():
                prod = item['obj']
                qty = item['qty']
                detail = OrderDetail(id=0, order_id=order_id, product_id=pid, quantity=qty, unit_price=prod.sale_price)
                self.detail_dao.insert(detail)
                
                prod.stock_quantity -= qty
                self.product_dao.update(prod)

            messagebox.showinfo("Thành công", f"Đơn hàng #{order_id} đã đặt thành công!")
            self.controller.cart = {} 
            self.controller.show_history()

        except Exception as e:
            print(f"Transaction Error: {e}") # In lỗi ra console để dễ debug
            messagebox.showerror("Lỗi hệ thống", f"Chi tiết lỗi: {str(e)}")