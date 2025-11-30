import customtkinter as ctk
import os
import sys

# --- Thiết lập đường dẫn để import được các module trong folder core ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from seller_app.login import LoginForm
from seller_app.base import BaseApp

if __name__ == "__main__":
    # Vòng lặp chính của ứng dụng
    while True:
        # BƯỚC 1: Khởi tạo và chạy màn hình Login
        login_app = LoginForm()
        login_app.mainloop()

        # BƯỚC 2: Kiểm tra kết quả sau khi Login đóng lại
        if login_app.current_user:
            # Nếu có current_user -> Đăng nhập thành công -> Mở Dashboard
            user = login_app.current_user
            
            # Khởi tạo Dashboard (Lúc này login_app đã bị destroy hoàn toàn nên không lo xung đột)
            dashboard_app = BaseApp(current_user=user)
            dashboard_app.mainloop()

            # BƯỚC 3: Kiểm tra xem người dùng làm gì sau khi Dashboard đóng
            if dashboard_app.is_logout:
                # Nếu người dùng bấm Logout -> Tiếp tục vòng lặp (Mở lại Login)
                print("Logging out...")
                continue
            else:
                # Nếu người dùng bấm X (đóng app) -> Thoát vòng lặp
                print("Exiting application...")
                break
        else:
            # Nếu không có user (Người dùng tắt form Login mà chưa đăng nhập) -> Thoát
            break