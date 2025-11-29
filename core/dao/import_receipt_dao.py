from .base_dao import BaseDAO
from core.models.import_receipt import ImportReceipt

class ImportReceiptDAO(BaseDAO):
    def select_all(self):
        self.cursor.execute("SELECT * FROM import_receipts")
        return [ImportReceipt.from_row(row) for row in self.cursor.fetchall()]

    def select_by_id(self, receipt_id):
        self.cursor.execute("SELECT * FROM import_receipts WHERE id = ?", (receipt_id,))
        return ImportReceipt.from_row(self.cursor.fetchone())

    def insert(self, receipt: ImportReceipt):
        query = "INSERT INTO import_receipts (employee_id) VALUES (?)"
        # import_date tự động sinh bởi database (DEFAULT CURRENT_TIMESTAMP)
        self.cursor.execute(query, (receipt.employee_id,))
        self.commit()
        return self.cursor.lastrowid

    def delete(self, receipt_id):
        self.cursor.execute("DELETE FROM import_receipts WHERE id = ?", (receipt_id,))
        self.commit()