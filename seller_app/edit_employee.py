import customtkinter as ctk
from tkinter import messagebox
import hashlib
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from core.dao.employee_dao import EmployeeDAO
from core.models.employee import Employee

class EditEmployeeFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, employee_data):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.employee_data = employee_data # Object Employee cần sửa
        self.db_conn = controller.db.get_connection()
        self.employee_dao = EmployeeDAO(self.db_conn)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.setup_ui()
        self.load_current_data()

    def setup_ui(self):
        # HEADER
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkButton(header, text="< Back", width=80, fg_color="gray", 
                      command=self.go_back).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(header, text=f"EDIT EMPLOYEE: {self.employee_data.username}", font=("Arial", 24, "bold"), 
                     text_color="#2D3436").pack(side="left")

        # FORM CONTAINER
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        self.shadow_frame = ctk.CTkFrame(container, width=500, height=600, fg_color="#E0E0E0", corner_radius=15)
        self.shadow_frame.place(relx=0.503, rely=0.505, anchor="center")

        self.form_frame = ctk.CTkFrame(container, width=500, height=600, fg_color="white", corner_radius=15)
        self.form_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.form_frame.pack_propagate(False) 

        # --- NỘI DUNG FORM ---
        ctk.CTkLabel(self.form_frame, text="Update Information", font=("Arial", 20, "bold"), text_color="#2D3436").pack(pady=(30, 20))

        # Username (Read-only)
        self.entry_username = self.create_input_field(self.form_frame, "Username (Cannot change):")
        self.entry_username.configure(state="disabled", fg_color="#f0f0f0") # Xám đi
        
        # Full Name
        self.entry_fullname = self.create_input_field(self.form_frame, "Full Name")

        # Password (Optional)
        ctk.CTkLabel(self.form_frame, text="New Password (Leave blank to keep current):", text_color="gray", font=("Arial", 12, "bold")).pack(anchor="w", padx=60, pady=(10, 0))
        self.entry_password = ctk.CTkEntry(self.form_frame, height=40, border_color="#dfe6e9", border_width=2, fg_color="white", text_color="black", show="*")
        self.entry_password.pack(fill="x", padx=60, pady=(0, 15))

        # Status
        ctk.CTkLabel(self.form_frame, text="Status:", text_color="gray", font=("Arial", 12, "bold")).pack(anchor="w", padx=60, pady=(5, 0))
        self.var_status = ctk.StringVar(value="active")
        self.combo_status = ctk.CTkComboBox(self.form_frame, values=["active", "resigned"], variable=self.var_status, height=40, border_color="#dfe6e9", fg_color="white", text_color="black")
        self.combo_status.pack(fill="x", padx=60, pady=(0, 15))

        # Role Switch
        self.var_is_manager = ctk.BooleanVar(value=False)
        switch_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        switch_frame.pack(fill="x", padx=60, pady=(10, 20))
        
        ctk.CTkSwitch(switch_frame, text="Is Manager (Quản lý)", 
                      variable=self.var_is_manager, onvalue=True, offvalue=False,
                      text_color="black", font=("Arial", 12, "bold"), 
                      progress_color="#00b894").pack(side="left")

        # Footer Button
        btn_save = ctk.CTkButton(self.form_frame, text="SAVE CHANGES", height=45, fg_color="#00b894", 
                                 font=("Arial", 14, "bold"), command=self.save_employee)
        btn_save.pack(fill="x", padx=60, pady=20)

    def create_input_field(self, parent, label_text):
        ctk.CTkLabel(parent, text=label_text, text_color="gray", font=("Arial", 12, "bold")).pack(anchor="w", padx=60, pady=(5, 0))
        entry = ctk.CTkEntry(parent, height=40, border_color="#dfe6e9", border_width=2, fg_color="white", text_color="black")
        entry.pack(fill="x", padx=60, pady=(0, 15))
        return entry

    def load_current_data(self):
        self.entry_username.configure(state="normal")
        self.entry_username.insert(0, self.employee_data.username)
        self.entry_username.configure(state="disabled")
        
        self.entry_fullname.insert(0, self.employee_data.full_name)
        self.var_status.set(self.employee_data.status)
        self.var_is_manager.set(self.employee_data.is_manager)

    def save_employee(self):
        fullname = self.entry_fullname.get().strip()
        password = self.entry_password.get().strip()
        status = self.var_status.get()
        is_manager = self.var_is_manager.get()

        if not fullname:
            messagebox.showerror("Error", "Full Name is required!")
            return
        
        try:
            # Update object
            self.employee_data.full_name = fullname
            self.employee_data.status = status
            self.employee_data.is_manager = is_manager
            
            # Chỉ update password nếu người dùng có nhập
            if password:
                pwd_hash = hashlib.sha256(password.encode()).hexdigest()
                self.employee_data.password_hash = pwd_hash
            
            self.employee_dao.update(self.employee_data)
            messagebox.showinfo("Success", "Employee updated successfully!")
            self.go_back()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def go_back(self):
        self.controller.load_employee_dashboard_frame()