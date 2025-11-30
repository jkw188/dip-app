import customtkinter as ctk

class CashierFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_ui()

    def setup_ui(self):
        left = ctk.CTkFrame(self, fg_color="white")
        left.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        ctk.CTkLabel(left, text="PRODUCT SEARCH & SCAN", font=("Arial", 18, "bold"), text_color="black").pack(pady=10)
        
        right = ctk.CTkFrame(self, fg_color="white")
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        ctk.CTkLabel(right, text="BILLING", font=("Arial", 18, "bold"), text_color="black").pack(pady=10)
        ctk.CTkButton(right, text="PAY", fg_color="#00b894", height=50).pack(side="bottom", fill="x", padx=20, pady=20)