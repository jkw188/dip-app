from .base_dao import BaseDAO
from core.models.product_image import ProductImage
import numpy as np

class ProductImageDAO(BaseDAO):
    def select_all(self):
        self.cursor.execute("SELECT * FROM product_images")
        return [ProductImage.from_row(row) for row in self.cursor.fetchall()]

    def select_by_product_id(self, product_id):
        self.cursor.execute("SELECT * FROM product_images WHERE product_id = ?", (product_id,))
        return [ProductImage.from_row(row) for row in self.cursor.fetchall()]

    def select_thumbnail(self, product_id):
        self.cursor.execute("SELECT * FROM product_images WHERE product_id = ? AND is_thumbnail = 1", (product_id,))
        row = self.cursor.fetchone()
        return ProductImage.from_row(row)

    def insert(self, img: ProductImage):
        query = """
            INSERT INTO product_images (product_id, image_path, feature_vector, is_thumbnail)
            VALUES (?, ?, ?, ?)
        """
        self.cursor.execute(query, (img.product_id, img.image_path, img.feature_vector, int(img.is_thumbnail)))
        self.commit()
        return self.cursor.lastrowid

    def delete(self, img_id):
        self.cursor.execute("DELETE FROM product_images WHERE id = ?", (img_id,))
        self.commit()

    def select_all_vectors(self):
        """
        Lấy toàn bộ vector đặc trưng từ database để phục vụ tìm kiếm AI.
        Output: List các tuple (product_id, numpy_vector)
        """
        # Chỉ lấy những dòng có vector (feature_vector IS NOT NULL)
        self.cursor.execute("SELECT product_id, feature_vector FROM product_images WHERE feature_vector IS NOT NULL")
        rows = self.cursor.fetchall()
        
        results = []
        for row in rows:
            pid = row['product_id']
            blob = row['feature_vector']
            
            # Convert BLOB binary trở lại thành Numpy Array
            if blob:
                try:
                    # np.frombuffer giúp đọc chuỗi bytes thành array cực nhanh
                    vec = np.frombuffer(blob, dtype=np.float32)
                    results.append((pid, vec))
                except Exception as e:
                    print(f"Lỗi convert vector cho sản phẩm {pid}: {e}")
                    
        return results