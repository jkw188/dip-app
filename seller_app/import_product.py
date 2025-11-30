import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from core.dao.product_dao import ProductDAO
from core.dao.import_receipt_dao import ImportReceiptDAO
from core.dao.import_detail_dao import ImportDetailDAO
from core.models.import_receipt import ImportReceipt
from core.models.import_detail import ImportDetail

class ImportProductFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.db_conn = controller.db.get_connection()
        
        self.product_dao = ProductDAO(self.db_conn)
        self.receipt_dao = ImportReceiptDAO(self.db_conn)
        self.detail_dao = ImportDetailDAO(self.db_conn)
        
        self.cart = {}
        self.is_manager_view = self.controller.current_user.is_manager

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Phân quyền hiển thị
        if self.is_manager_view:
            self.setup_manager_view()
        else:
            self.setup_employee_view()

    # --- Method wrapper để BaseApp gọi chung ---
    def load_data(self):
        """BaseApp sẽ gọi hàm này để refresh dữ liệu khi switch tab"""
        if self.is_manager_view:
            self.load_requests()
        else:
            self.load_products()

    # =========================================================================
    # GIAO DIỆN NHÂN VIÊN (TẠO PHIẾU NHẬP)
    # =========================================================================
    def setup_employee_view(self):
        # Reset layout grid cho view nhân viên (2 cột)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- CỘT TRÁI ---
        left_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)

        search_frame = ctk.CTkFrame(left_frame, fg_color="transparent", height=60)
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(search_frame, text="IMPORT STOCK", font=("Arial", 20, "bold"), text_color="black").pack(side="left", padx=10)
        
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Search Product...", width=250)
        self.entry_search.pack(side="right", padx=5)
        self.entry_search.bind("<Return>", lambda e: self.search_product())
        
        ctk.CTkButton(search_frame, text="Find", width=60, fg_color="#2D3436", command=self.search_product).pack(side="right")

        self.product_grid = ctk.CTkScrollableFrame(left_frame, fg_color="#F5F6FA")
        self.product_grid.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self.load_products()

        # --- CỘT PHẢI ---
        right_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(right_frame, text="IMPORT LIST", font=("Arial", 18, "bold"), text_color="black").grid(row=0, column=0, pady=15)

        self.cart_list = ctk.CTkScrollableFrame(right_frame, fg_color="#F5F6FA")
        self.cart_list.grid(row=1, column=0, sticky="nsew", padx=10)

        total_frame = ctk.CTkFrame(right_frame, fg_color="#2D3436", height=120, corner_radius=10)
        total_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(total_frame, text="ESTIMATED COST:", text_color="white").pack(anchor="w", padx=20, pady=(15, 5))
        self.lbl_total = ctk.CTkLabel(total_frame, text="0", text_color="#00b894", font=("Arial", 28, "bold"))
        self.lbl_total.pack(anchor="e", padx=20)

        ctk.CTkButton(right_frame, text="SEND REQUEST", height=50, fg_color="#00b894", 
                      font=("Arial", 16, "bold"), command=self.send_import_request).grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 20))

    def load_products(self, keyword=None):
        if not hasattr(self, 'product_grid'): return # Safety check

        for w in self.product_grid.winfo_children(): w.destroy()
        if keyword:
            products = self.product_dao.search_by_name(keyword)
        else:
            products = self.product_dao.select_all()

        for p in products:
            self.create_card(p)

    def search_product(self):
        self.load_products(self.entry_search.get().strip())

    def create_card(self, product):
        card = ctk.CTkFrame(self.product_grid, fg_color="white", corner_radius=8)
        card.pack(fill="x", pady=5)
        
        ctk.CTkLabel(card, text="📥", font=("Arial", 24)).pack(side="left", padx=10)
        ctk.CTkLabel(card, text=product.name, text_color="black", font=("Arial", 14, "bold")).pack(side="left")
        
        btn = ctk.CTkButton(card, text="ADD", width=60, height=30, fg_color="#0984e3", 
                            command=lambda p=product: self.add_to_cart(p))
        btn.pack(side="right", padx=10, pady=10)

    def add_to_cart(self, product):
        if product.id in self.cart:
            self.cart[product.id]['qty'] += 1
        else:
            self.cart[product.id] = {'obj': product, 'qty': 1}
        self.render_cart()

    def render_cart(self):
        for w in self.cart_list.winfo_children(): w.destroy()
        total = 0
        for pid, item in list(self.cart.items()):
            prod = item['obj']
            qty = item['qty']
            cost = (prod.import_price or 0) * qty
            total += cost
            
            row = ctk.CTkFrame(self.cart_list, fg_color="white", height=50)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=prod.name, text_color="black", width=120).pack(side="left")
            ctk.CTkButton(row, text="-", width=30, fg_color="gray", command=lambda p=pid: self.change_qty(p, -1)).pack(side="left")
            ctk.CTkLabel(row, text=str(qty), text_color="black", width=30).pack(side="left")
            ctk.CTkButton(row, text="+", width=30, fg_color="gray", command=lambda p=pid: self.change_qty(p, 1)).pack(side="left")
            ctk.CTkLabel(row, text=f"{cost:,.0f}", text_color="black").pack(side="right", padx=10)

        self.lbl_total.configure(text=f"{total:,.0f} VNĐ")

    def change_qty(self, pid, delta):
        if pid in self.cart:
            self.cart[pid]['qty'] += delta
            if self.cart[pid]['qty'] <= 0: del self.cart[pid]
            self.render_cart()

    def send_import_request(self):
        if not self.cart:
            messagebox.showinfo("Empty", "Import list is empty!")
            return
            
        if messagebox.askyesno("Confirm", "Send import request for approval?"):
            try:
                receipt = ImportReceipt(
                    id=0,
                    employee_id=self.controller.current_user.id,
                    import_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    is_confirm=False 
                )
                r_id = self.receipt_dao.insert(receipt)
                
                for pid, item in self.cart.items():
                    detail = ImportDetail(
                        id=0, receipt_id=r_id, product_id=pid,
                        quantity=item['qty'],
                        manufacturing_date=datetime.now().strftime("%Y-%m-%d")
                    )
                    self.detail_dao.insert(detail)
                
                messagebox.showinfo("Success", "Request sent! Waiting for manager.")
                self.cart = {}
                self.render_cart()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # =========================================================================
    # GIAO DIỆN QUẢN LÝ (DUYỆT PHIẾU NHẬP)
    # =========================================================================
    def setup_manager_view(self):
        # Reset layout grid cho view quản lý (1 cột)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        ctk.CTkLabel(header, text="PENDING IMPORT REQUESTS", font=("Arial", 24, "bold"), text_color="#2D3436").pack(side="left")
        ctk.CTkButton(header, text="Refresh List", width=100, fg_color="#2D3436", command=self.load_requests).pack(side="right")

        # Table Container
        table_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(1, weight=1)

        # Header Row
        header_row = ctk.CTkFrame(table_frame, height=40, fg_color="#DFE6E9", corner_radius=5)
        header_row.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        cols = [("ID", 50), ("Creator ID", 100), ("Date", 200), ("Status", 100), ("Action", 150)]
        for name, width in cols:
            ctk.CTkLabel(header_row, text=name, font=("Arial", 12, "bold"), text_color="black", width=width).pack(side="left", padx=5, fill="x", expand=True)

        # List
        self.scroll_frame = ctk.CTkScrollableFrame(table_frame, fg_color="white")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))

        self.load_requests()

    def load_requests(self):
        if not hasattr(self, 'scroll_frame'): return

        for w in self.scroll_frame.winfo_children(): w.destroy()
        
        all_receipts = self.receipt_dao.select_all()
        # Lọc client side: chỉ lấy is_confirm=False (0)
        pending_receipts = [r for r in all_receipts if not r.is_confirm]

        if not pending_receipts:
            ctk.CTkLabel(self.scroll_frame, text="No pending import requests.", text_color="gray", font=("Arial", 14)).pack(pady=20)
            return

        for i, req in enumerate(pending_receipts):
            bg_color = "white" if i % 2 == 0 else "#F5F6FA"
            self.create_request_row(req, bg_color)

    def create_request_row(self, req, bg_color):
        row = ctk.CTkFrame(self.scroll_frame, height=50, fg_color=bg_color)
        row.pack(fill="x", pady=1)
        
        data = [
            (str(req.id), 50), 
            (str(req.employee_id), 100), 
            (req.import_date, 200), 
            ("Pending", 100)
        ]
        
        for text, width in data:
            ctk.CTkLabel(row, text=text, text_color="black", width=width, anchor="center").pack(side="left", padx=5, fill="x", expand=True)
        
        action_frame = ctk.CTkFrame(row, fg_color="transparent", width=150)
        action_frame.pack(side="left", padx=5, fill="x", expand=True)

        # Nút xem chi tiết
        ctk.CTkButton(action_frame, text="DETAILS", width=70, fg_color="gray", 
                      command=lambda r=req: self.show_details(r)).pack(side="left", padx=2)

        # Nút duyệt
        ctk.CTkButton(action_frame, text="APPROVE", width=70, fg_color="#00b894", 
                      command=lambda r=req: self.approve_import(r)).pack(side="left", padx=2)

    def show_details(self, req):
        details = self.detail_dao.select_by_receipt(req.id)
        msg = f"Receipt #{req.id} Details:\n\n"
        for d in details:
            msg += f"- Product ID: {d.product_id}, Qty: {d.quantity}\n"
        messagebox.showinfo("Request Details", msg)

    def approve_import(self, req):
        if messagebox.askyesno("Confirm Approval", f"Approve import receipt #{req.id}?\nStock will be updated."):
            try:
                self.receipt_dao.confirm_receipt(req.id)
                
                details = self.detail_dao.select_by_receipt(req.id)
                for d in details:
                    prod = self.product_dao.select_by_id(d.product_id)
                    if prod:
                        prod.stock_quantity += d.quantity
                        self.product_dao.update(prod)
                
                messagebox.showinfo("Done", "Import approved and stock updated.")
                self.load_requests()
            except Exception as e:
                messagebox.showerror("Error", str(e))