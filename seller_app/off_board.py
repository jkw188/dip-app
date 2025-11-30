import customtkinter as ctk
from tkinter import messagebox
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from core.dao.offboard_request_dao import OffboardRequestDAO
from core.dao.employee_dao import EmployeeDAO
from core.models.offboard_request import OffboardRequest

class OffBoardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.db_conn = controller.db.get_connection()
        
        self.request_dao = OffboardRequestDAO(self.db_conn)
        self.employee_dao = EmployeeDAO(self.db_conn)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        if self.controller.current_user.is_manager:
            self.setup_manager_view()
        else:
            self.setup_employee_view()

    def setup_employee_view(self):
        container = ctk.CTkFrame(self, fg_color="white", corner_radius=10, width=500, height=400)
        container.place(relx=0.5, rely=0.5, anchor="center")
        container.pack_propagate(False)

        ctk.CTkLabel(container, text="RESIGNATION REQUEST", font=("Arial", 22, "bold"), text_color="#2D3436").pack(pady=(30, 20))
        
        self.lbl_status = ctk.CTkLabel(container, text="", font=("Arial", 14, "italic"))
        self.lbl_status.pack(pady=(0, 10))
        self.check_existing_request()

        ctk.CTkLabel(container, text="Reason:", text_color="gray", anchor="w").pack(fill="x", padx=40)
        
        self.txt_reason = ctk.CTkTextbox(container, height=100, border_color="#dfe6e9", border_width=2, fg_color="white", text_color="black")
        self.txt_reason.pack(fill="x", padx=40, pady=(5, 20))

        self.btn_submit = ctk.CTkButton(container, text="SUBMIT", height=45, fg_color="#d63031", command=self.submit_request)
        self.btn_submit.pack(fill="x", padx=40)

    def check_existing_request(self):
        requests = self.request_dao.get_by_employee_id(self.controller.current_user.id)
        if requests:
            latest = requests[0]
            self.lbl_status.configure(text=f"Status: {latest.status.upper()}", text_color="blue")
            if latest.status == 'pending':
                self.btn_submit.configure(state="disabled", text="Waiting Approval")

    def submit_request(self):
        reason = self.txt_reason.get("1.0", "end").strip()
        if not reason: return
        
        try:
            self.request_dao.insert(OffboardRequest(id=0, employee_id=self.controller.current_user.id, reason=reason))
            messagebox.showinfo("Success", "Sent!")
            self.check_existing_request()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def setup_manager_view(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        ctk.CTkLabel(header, text="OFFBOARDING REQUESTS", font=("Arial", 24, "bold"), text_color="#2D3436").pack(side="left")
        ctk.CTkButton(header, text="Refresh", width=80, fg_color="gray", command=self.load_requests).pack(side="right")

        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="white")
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        self.load_requests()

    def load_requests(self):
        for w in self.list_frame.winfo_children(): w.destroy()
        requests = self.request_dao.select_all_pending()
        
        if not requests:
            ctk.CTkLabel(self.list_frame, text="No pending requests.", text_color="gray").pack(pady=20)
            return

        for req in requests:
            row = ctk.CTkFrame(self.list_frame, height=60, fg_color="#F5F6FA")
            row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(row, text=f"Emp ID: {req.employee_id}", width=80, text_color="gray").pack(side="left")
            ctk.CTkLabel(row, text=req.employee_name or "Unknown", width=150, text_color="black", font=("Arial", 12, "bold")).pack(side="left")
            ctk.CTkLabel(row, text=req.reason, width=200, text_color="black", anchor="w").pack(side="left", padx=10)
            
            ctk.CTkButton(row, text="APPROVE", width=70, fg_color="green", command=lambda r=req: self.approve(r)).pack(side="right", padx=5)
            ctk.CTkButton(row, text="REJECT", width=70, fg_color="red", command=lambda r=req: self.reject(r)).pack(side="right", padx=5)

    def approve(self, req):
        if messagebox.askyesno("Confirm", "Approve resignation?"):
            self.request_dao.update_status(req.id, 'approved')
            self.employee_dao.soft_delete(req.employee_id)
            self.load_requests()

    def reject(self, req):
        if messagebox.askyesno("Confirm", "Reject request?"):
            self.request_dao.update_status(req.id, 'rejected')
            self.load_requests()