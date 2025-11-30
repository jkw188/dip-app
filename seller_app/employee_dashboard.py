import customtkinter as ctk
from core.dao.employee_dao import EmployeeDAO
from math import ceil

class EmployeeDashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # Kết nối DAO
        self.employee_dao = EmployeeDAO(self.controller.db.get_connection())

        # Config phân trang
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.all_employees = [] 

        # Grid Layout chính
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Kiểm tra quyền: Chỉ Manager mới được xem
        if not self.controller.current_user.is_manager:
            self.show_access_denied()
        else:
            self.setup_ui()
            self.load_data()

    def show_access_denied(self):
        ctk.CTkLabel(self, text="ACCESS DENIED: MANAGERS ONLY", 
                     font=("Arial", 30, "bold"), text_color="red").place(relx=0.5, rely=0.5, anchor="center")

    def setup_ui(self):
        # 1. HEADER
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(header, text="EMPLOYEE MANAGEMENT", font=("Arial", 24, "bold"), text_color="#2D3436").pack(side="left")
        
        right_group = ctk.CTkFrame(header, fg_color="transparent")
        right_group.pack(side="right")
        
        self.entry_search = ctk.CTkEntry(right_group, placeholder_text="Search Name/User...", width=250)
        self.entry_search.pack(side="left", padx=10)
        self.entry_search.bind("<Return>", lambda e: self.search_employee())

        ctk.CTkButton(right_group, text="Search", width=80, fg_color="#2D3436", command=self.search_employee).pack(side="left", padx=5)
        ctk.CTkButton(right_group, text="+ NEW EMPLOYEE", width=150, fg_color="#2D3436", command=self.controller.load_add_employee_frame).pack(side="left")

        # 2. TABLE CONTAINER
        self.table_container = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.table_container.grid(row=1, column=0, sticky="nsew", padx=20)
        
        self.table_container.grid_columnconfigure(0, weight=1)
        self.table_container.grid_rowconfigure(1, weight=1)

        # Table Header Row
        header_row = ctk.CTkFrame(self.table_container, height=40, fg_color="#DFE6E9", corner_radius=5)
        header_row.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Cấu hình cột
        columns = [
            ("ID", 50), ("Username", 150), ("Full Name", 200), 
            ("Role", 100), ("Status", 100), ("Action", 100)
        ]
        
        for name, width in columns:
            lbl = ctk.CTkLabel(header_row, text=name, font=("Arial", 12, "bold"), text_color="black", width=width)
            lbl.pack(side="left", padx=5, fill="x", expand=True)

        # List Frame (Container chứa rows)
        self.list_frame = ctk.CTkFrame(self.table_container, fg_color="white", corner_radius=0)
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=0)

        # 3. FOOTER
        footer = ctk.CTkFrame(self, fg_color="transparent", height=40)
        footer.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
        self.btn_prev = ctk.CTkButton(footer, text="< Prev", width=80, fg_color="#636E72", command=self.prev_page)
        self.btn_prev.pack(side="left")
        
        self.lbl_page = ctk.CTkLabel(footer, text="Page 1 / 1", text_color="black", font=("Arial", 12, "bold"))
        self.lbl_page.pack(side="left", padx=20)
        
        self.btn_next = ctk.CTkButton(footer, text="Next >", width=80, fg_color="#636E72", command=self.next_page)
        self.btn_next.pack(side="left")

    def load_data(self):
        self.all_employees = self.employee_dao.select_all()
        
        self.total_pages = ceil(len(self.all_employees) / self.items_per_page)
        if self.total_pages == 0: self.total_pages = 1
        
        self.current_page = 1
        self.render_table()

    def search_employee(self):
        keyword = self.entry_search.get().strip().lower()
        if not keyword:
            self.load_data()
            return
        
        # Filter trong Python (Vì DAO chưa có hàm search)
        all_data = self.employee_dao.select_all()
        self.all_employees = [
            e for e in all_data 
            if keyword in e.username.lower() or keyword in e.full_name.lower()
        ]
        
        self.total_pages = ceil(len(self.all_employees) / self.items_per_page)
        if self.total_pages == 0: self.total_pages = 1
        self.current_page = 1
        self.render_table()

    def render_table(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        self.lbl_page.configure(text=f"Page {self.current_page} / {self.total_pages}")
        self.btn_prev.configure(state="normal" if self.current_page > 1 else "disabled")
        self.btn_next.configure(state="normal" if self.current_page < self.total_pages else "disabled")

        start = (self.current_page - 1) * self.items_per_page
        end = start + self.items_per_page
        page_data = self.all_employees[start:end]

        # Render rows thật
        current_rows_count = 0
        if page_data:
            for i, emp in enumerate(page_data):
                bg_color = "white" if i % 2 == 0 else "#F0F0F0"
                self.create_row(emp, bg_color)
                current_rows_count += 1
        else:
            lbl = ctk.CTkLabel(self.list_frame, text="No employees found.", text_color="gray")
            lbl.pack(fill="both", expand=True)
            current_rows_count += 1

        # Fill blank rows để lấp đầy (Quan trọng)
        rows_to_fill = self.items_per_page - current_rows_count
        for j in range(rows_to_fill):
            idx = current_rows_count + j
            bg_color = "white" if idx % 2 == 0 else "#F0F0F0"
            self.create_blank_row(bg_color)

    def create_row(self, emp, bg_color):
        row = ctk.CTkFrame(self.list_frame, fg_color=bg_color, corner_radius=0, height=50)
        # Giãn dòng để lấp đầy chiều cao
        row.pack(fill="both", expand=True, pady=1)
        
        role_str = "Manager" if emp.is_manager else "Staff"
        
        data = [
            (str(emp.id), 50), 
            (emp.username, 150), 
            (emp.full_name, 200), 
            (role_str, 100), 
            (emp.status, 100)
        ]
        
        for text, width in data:
            lbl = ctk.CTkLabel(row, text=text, text_color="black", width=width, anchor="center")
            lbl.pack(side="left", padx=5, fill="x", expand=True)
        
        # Action Buttons
        btn_frame = ctk.CTkFrame(row, fg_color="transparent", width=100)
        btn_frame.pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(btn_frame, text="✏️", width=30, height=25, fg_color="#0984e3",
                      command=lambda e=emp: self.edit_employee(e)).pack(side="left", padx=2)
        
        ctk.CTkButton(btn_frame, text="🔒", width=30, height=25, fg_color="#d63031",
                      command=lambda e=emp: self.lock_employee(e)).pack(side="left", padx=2)

    def create_blank_row(self, bg_color):
        row = ctk.CTkFrame(self.list_frame, fg_color=bg_color, corner_radius=0, height=50)
        row.pack(fill="both", expand=True, pady=1)

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.render_table()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.render_table()

    def edit_employee(self, emp):
        self.controller.load_edit_employee_frame(emp)

    def lock_employee(self, emp):
        # print(f"Lock: {emp.username}")
        self.employee_dao.soft_delete(emp.id)
        self.load_data()