# File này dùng để tạo thư mục, file thay vì tạo thủ công thôi nha các bạn (chạy 1 lần duy nhất)
import os

structure = [
    "core",
    "data",
    "data/images",  # Thêm folder chứa ảnh sản phẩm
    "data/db",      # Thêm folder chứa file SQLite
]

files = [
    "core/__init__.py",
    "core/camera.py",
    "core/image_processing.py",
    "core/ai_model.py",
    "core/database.py",
    "seller_app.py",
    "buyer_app.py",
    "requirements.txt"
]

for folder in structure:
    os.makedirs(folder, exist_ok=True)
    print(f"Created folder: {folder}")

for file in files:
    with open(file, 'w') as f:
        pass
    print(f"Created file: {file}")