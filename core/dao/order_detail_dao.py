from .base_dao import BaseDAO 
from core.models.order_detail import OrderDetail

class OrderDetailDAO(BaseDAO):
    def select_by_order(self, order_id):
        self.cursor.execute("SELECT * FROM order_details WHERE order_id = ?", (order_id,))
        return [OrderDetail.from_row(row) for row in self.cursor.fetchall()]

    def insert(self, detail: OrderDetail):
        query = """
            INSERT INTO order_details (order_id, product_id, quantity, unit_price)
            VALUES (?, ?, ?, ?)
        """
        self.cursor.execute(query, (detail.order_id, detail.product_id, detail.quantity, detail.unit_price))
        self.commit()
        return self.cursor.lastrowid