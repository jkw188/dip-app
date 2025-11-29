import customtkinter as ctk
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
from seller_app.login import LoginForm

if __name__ == "__main__":
    app = LoginForm()
    app.mainloop()