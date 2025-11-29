from .base_dao import BaseDAO
from core.models.product_image import ProductImage

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