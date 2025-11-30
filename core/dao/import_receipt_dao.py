from .base_dao import BaseDAO
from core.models.import_receipt import ImportReceipt

class ImportReceiptDAO(BaseDAO):
    def select_all(self):
        self.cursor.execute("SELECT * FROM import_receipts ORDER BY import_date DESC")
        return [ImportReceipt.from_row(row) for row in self.cursor.fetchall()]

    def select_by_id(self, receipt_id):
        self.cursor.execute("SELECT * FROM import_receipts WHERE id = ?", (receipt_id,))
        return ImportReceipt.from_row(self.cursor.fetchone())

    def insert(self, receipt: ImportReceipt):
        query = "INSERT INTO import_receipts (employee_id, is_confirm) VALUES (?, 0)"
        self.cursor.execute(query, (receipt.employee_id,))
        self.commit()
        return self.cursor.lastrowid
    
    def confirm_receipt(self, receipt_id):
        # Cập nhật trạng thái đã xác nhận
        query = "UPDATE import_receipts SET is_confirm = 1 WHERE id = ?"
        self.cursor.execute(query, (receipt_id,))
        self.commit()

    def delete(self, receipt_id):
        self.cursor.execute("DELETE FROM import_receipts WHERE id = ?", (receipt_id,))
        self.commit()