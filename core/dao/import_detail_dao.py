from .base_dao import BaseDAO
from core.models.import_detail import ImportDetail

class ImportDetailDAO(BaseDAO):
    def select_by_receipt(self, receipt_id):
        self.cursor.execute("SELECT * FROM import_details WHERE receipt_id = ?", (receipt_id,))
        return [ImportDetail.from_row(row) for row in self.cursor.fetchall()]

    def insert(self, detail: ImportDetail):
        query = """
            INSERT INTO import_details (receipt_id, product_id, quantity, manufacturing_date)
            VALUES (?, ?, ?, ?)
        """
        self.cursor.execute(query, (detail.receipt_id, detail.product_id, detail.quantity, detail.manufacturing_date))
        self.commit()
        return self.cursor.lastrowid
    
    # Hàm này thường dùng khi hiển thị hàng sắp hết hạn
    def select_expiring_products(self):
        query = """
            SELECT d.*, p.shelf_life_days 
            FROM import_details d
            JOIN products p ON d.product_id = p.id
            WHERE d.manufacturing_date IS NOT NULL
        """
        self.cursor.execute(query)
        # Lưu ý: Kết quả này trả về Row raw vì cần join bảng, 
        # nên xử lý logic ở Service hoặc App
        return self.cursor.fetchall()