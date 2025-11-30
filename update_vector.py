import os
import sys
import numpy as np
from PIL import Image

# Setup đường dẫn
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from core.database import Database
from core.dao.product_image_dao import ProductImageDAO
from core.ai_model import FeatureExtractor

def update_vectors():
    print("--- BẮT ĐẦU CẬP NHẬT VECTOR ---")
    
    # 1. Kết nối DB
    db = Database()
    conn = db.get_connection()
    img_dao = ProductImageDAO(conn)
    
    # 2. Khởi tạo AI
    print("Đang tải model AI (có thể mất vài giây)...")
    extractor = FeatureExtractor()
    
    # 3. Lấy tất cả ảnh trong DB
    all_images = img_dao.select_all()
    print(f"Tìm thấy {len(all_images)} ảnh trong Database.")
    
    count = 0
    for img_record in all_images:
        # Nếu chưa có vector hoặc muốn cập nhật lại
        if img_record.image_path:
            full_path = os.path.abspath(img_record.image_path)
            
            if os.path.exists(full_path):
                try:
                    # Load ảnh
                    pil_img = Image.open(full_path)
                    
                    # Trích xuất đặc trưng (ra numpy array)
                    vector = extractor.extract(pil_img)
                    
                    # Chuyển thành bytes để lưu vào BLOB SQLite
                    vector_blob = vector.tobytes()
                    
                    # Cập nhật vào DB
                    # (Ta dùng câu lệnh SQL trực tiếp vì DAO hiện tại chưa có hàm update riêng cho vector)
                    conn.execute(
                        "UPDATE product_images SET feature_vector = ? WHERE id = ?",
                        (vector_blob, img_record.id)
                    )
                    conn.commit()
                    
                    print(f"[OK] Đã cập nhật vector cho ID {img_record.id} ({img_record.image_path})")
                    count += 1
                except Exception as e:
                    print(f"[Lỗi] Không thể xử lý ảnh ID {img_record.id}: {e}")
            else:
                print(f"[Bỏ qua] Không tìm thấy file: {full_path}")
                
    print(f"--- HOÀN TẤT: Đã cập nhật {count} sản phẩm ---")
    db.close()

if __name__ == "__main__":
    update_vectors()