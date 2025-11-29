from .base_dao import BaseDAO
from core.models.customer import Customer

class CustomerDAO(BaseDAO):
    def select_all(self):
        self.cursor.execute("SELECT * FROM customers")
        rows = self.cursor.fetchall()
        return [Customer.from_row(row) for row in rows]

    def select_by_id(self, cus_id):
        self.cursor.execute("SELECT * FROM customers WHERE id = ?", (cus_id,))
        row = self.cursor.fetchone()
        return Customer.from_row(row)

    def insert(self, cus: Customer):
        query = """
            INSERT INTO customers (username, password_hash, full_name, phone, address)
            VALUES (?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (cus.username, cus.password_hash, cus.full_name, cus.phone, cus.address))
        self.commit()
        return self.cursor.lastrowid

    def update(self, cus: Customer):
        query = """
            UPDATE customers SET username=?, password_hash=?, full_name=?, phone=?, address=?
            WHERE id=?
        """
        self.cursor.execute(query, (cus.username, cus.password_hash, cus.full_name, cus.phone, cus.address, cus.id))
        self.commit()

    def delete(self, cus_id):
        self.cursor.execute("DELETE FROM customers WHERE id = ?", (cus_id,))
        self.commit()