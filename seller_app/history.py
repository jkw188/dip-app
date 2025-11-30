import customtkinter as ctk

class HistoryFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.pack(fill="both", expand=True)
        
        ctk.CTkLabel(self, text="HISTORY & REVENUE", font=("Arial", 30), text_color="#2D3436").place(relx=0.5, rely=0.5, anchor="center")