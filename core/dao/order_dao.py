from .base_dao import BaseDAO
from core.models.order import Order 

class OrderDAO(BaseDAO):
    def select_all(self):
        self.cursor.execute("SELECT * FROM orders")
        return [Order.from_row(row) for row in self.cursor.fetchall()]

    def select_by_id(self, order_id):
        self.cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        return Order.from_row(self.cursor.fetchone())

    def insert(self, order: Order):
        query = """
            INSERT INTO orders (customer_id, employee_id, total_amount, status)
            VALUES (?, ?, ?, ?)
        """
        self.cursor.execute(query, (order.customer_id, order.employee_id, order.total_amount, order.status))
        self.commit()
        return self.cursor.lastrowid

    def update_status(self, order_id, new_status):
        self.cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
        self.commit()

    def delete(self, order_id):
        self.cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        self.commit()