import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

from core.dao.product_dao import ProductDAO
from core.dao.order_dao import OrderDAO
from core.dao.order_detail_dao import OrderDetailDAO
from core.models.order import Order
from core.models.order_detail import OrderDetail

class CashierFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.db_conn = controller.db.get_connection()
        
        self.product_dao = ProductDAO(self.db_conn)
        self.order_dao = OrderDAO(self.db_conn)
        self.detail_dao = OrderDetailDAO(self.db_conn)
        
        self.cart = {} 

        self.grid_columnconfigure(0, weight=2) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)

        self.setup_left_panel()
        self.setup_right_panel()

    def setup_left_panel(self):
        left_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)

        # Header Search
        search_frame = ctk.CTkFrame(left_frame, fg_color="transparent", height=50)
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(search_frame, text="CASHIER", font=("Arial", 20, "bold"), text_color="black").pack(side="left", padx=10)
        
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Enter Product ID or Name...", width=250)
        self.entry_search.pack(side="right", padx=5)
        self.entry_search.bind("<Return>", lambda e: self.search_product())
        
        ctk.CTkButton(search_frame, text="Find", width=60, fg_color="#2D3436", command=self.search_product).pack(side="right")

        self.lbl_error = ctk.CTkLabel(left_frame, text="", text_color="red", font=("Arial", 12))
        self.lbl_error.grid(row=2, column=0, pady=(0, 5))

        # Grid sản phẩm
        self.product_grid = ctk.CTkScrollableFrame(left_frame, fg_color="#F5F6FA")
        self.product_grid.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self.load_products_to_grid()

    def load_products_to_grid(self, keyword=None):
        for widget in self.product_grid.winfo_children():
            widget.destroy()
        
        if keyword:
            try:
                p_id = int(keyword)
                product = self.product_dao.select_by_id(p_id)
                products = [product] if product else []
            except ValueError:
                products = self.product_dao.search_by_name(keyword)
        else:
            products = self.product_dao.select_all()

        if not products:
            self.lbl_error.configure(text=f"Product not found: '{keyword}'")
            return
        else:
            self.lbl_error.configure(text="")

        for p in products:
            self.create_product_card(p)

    def search_product(self):
        kw = self.entry_search.get().strip()
        self.load_products_to_grid(kw)

    def create_product_card(self, product):
        card = ctk.CTkFrame(self.product_grid, fg_color="white", corner_radius=8, height=60)
        card.pack(fill="x", pady=5)
        
        ctk.CTkLabel(card, text="📦", font=("Arial", 24)).pack(side="left", padx=10)
        
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", padx=10)
        ctk.CTkLabel(info, text=product.name, text_color="black", font=("Arial", 14, "bold")).pack(anchor="w")
        ctk.CTkLabel(info, text=f"Stock: {product.stock_quantity}", text_color="gray", font=("Arial", 11)).pack(anchor="w")
        
        btn_add = ctk.CTkButton(card, text="ADD +", width=60, height=30, fg_color="#00b894",
                                command=lambda p=product: self.add_to_cart(p))
        btn_add.pack(side="right", padx=10)
        
        ctk.CTkLabel(card, text=f"{product.sale_price:,.0f} đ", text_color="#00b894", font=("Arial", 14, "bold")).pack(side="right", padx=10)

    def setup_right_panel(self):
        right_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(right_frame, text="CURRENT ORDER", font=("Arial", 18, "bold"), text_color="black").grid(row=0, column=0, pady=15)

        self.bill_list = ctk.CTkScrollableFrame(right_frame, fg_color="#F5F6FA")
        self.bill_list.grid(row=1, column=0, sticky="nsew", padx=10)

        total_frame = ctk.CTkFrame(right_frame, fg_color="#2D3436", height=120, corner_radius=10)
        total_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(total_frame, text="TOTAL:", text_color="white", font=("Arial", 16)).pack(anchor="w", padx=20, pady=(15, 5))
        self.lbl_total_money = ctk.CTkLabel(total_frame, text="0", text_color="#00b894", font=("Arial", 28, "bold"))
        self.lbl_total_money.pack(anchor="e", padx=20)

        ctk.CTkButton(right_frame, text="PAY (THANH TOÁN)", height=50, fg_color="#00b894", 
                      font=("Arial", 16, "bold"), hover_color="#00a884",
                      command=self.process_payment).grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 20))

    def add_to_cart(self, product):
        if product.stock_quantity <= 0:
            messagebox.showwarning("Warning", "Out of stock!")
            return

        if product.id in self.cart:
            if self.cart[product.id]['qty'] < product.stock_quantity:
                self.cart[product.id]['qty'] += 1
            else:
                messagebox.showwarning("Limit", "Not enough stock!")
        else:
            self.cart[product.id] = {'obj': product, 'qty': 1}
        
        self.render_cart()

    def render_cart(self):
        for widget in self.bill_list.winfo_children():
            widget.destroy()
        
        total_money = 0
        
        for pid, item in list(self.cart.items()):
            product = item['obj']
            qty = item['qty']
            subtotal = product.sale_price * qty
            total_money += subtotal
            
            row = ctk.CTkFrame(self.bill_list, fg_color="white", height=50)
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=product.name, text_color="black", width=100, anchor="w").pack(side="left", padx=5)
            
            ctk.CTkButton(row, text="-", width=30, fg_color="gray", 
                          command=lambda p=pid: self.change_qty(p, -1)).pack(side="left")
            
            ctk.CTkLabel(row, text=str(qty), text_color="black", width=30).pack(side="left")
            
            ctk.CTkButton(row, text="+", width=30, fg_color="gray", 
                          command=lambda p=pid: self.change_qty(p, 1)).pack(side="left")
            
            ctk.CTkLabel(row, text=f"{subtotal:,.0f}", text_color="black", font=("Arial", 12, "bold")).pack(side="right", padx=10)

        self.lbl_total_money.configure(text=f"{total_money:,.0f} VNĐ")

    def change_qty(self, pid, delta):
        if pid in self.cart:
            self.cart[pid]['qty'] += delta
            if self.cart[pid]['qty'] <= 0:
                del self.cart[pid]
            elif delta > 0:
                prod = self.cart[pid]['obj']
                if self.cart[pid]['qty'] > prod.stock_quantity:
                    self.cart[pid]['qty'] -= 1
                    messagebox.showwarning("Limit", "Not enough stock!")
            
            self.render_cart()

    def process_payment(self):
        if not self.cart:
            messagebox.showinfo("Empty", "Cart is empty!")
            return
            
        total = sum([item['obj'].sale_price * item['qty'] for item in self.cart.values()])
        
        if messagebox.askyesno("Confirm Payment", f"Pay {total:,.0f} VNĐ via Cash?"):
            try:
                new_order = Order(
                    id=0,
                    total_amount=total,
                    employee_id=self.controller.current_user.id,
                    order_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    status="completed"
                )
                order_id = self.order_dao.insert(new_order)
                
                for pid, item in self.cart.items():
                    prod = item['obj']
                    qty = item['qty']
                    
                    detail = OrderDetail(
                        id=0, order_id=order_id, product_id=pid, 
                        quantity=qty, unit_price=prod.sale_price
                    )
                    self.detail_dao.insert(detail)
                    
                    prod.stock_quantity -= qty
                    self.product_dao.update(prod)
                
                messagebox.showinfo("Success", f"Payment successful! Order #{order_id}")
                
                self.cart = {}
                self.render_cart()
                self.load_products_to_grid()
                
            except Exception as e:
                messagebox.showerror("Error", str(e))