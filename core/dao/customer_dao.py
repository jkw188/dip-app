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

    def select_by_username(self, username):
        """
        Tìm khách hàng theo username.
        Dùng cho chức năng Đăng nhập.
        """
        if self.conn is None:
            return None
            
        # FIX: Bỏ dictionary=True để tránh lỗi TypeError với một số driver DB
        cursor = self.conn.cursor()
        try:
            # FIX: Thay %s thành ? cho tương thích với SQLite
            query = "SELECT id, username, password_hash, full_name, phone, address FROM customers WHERE username = ?"
            cursor.execute(query, (username,))
            row = cursor.fetchone()
            
            if row:
                # Convert thủ công từ Tuple sang Dictionary dựa trên tên cột
                columns = [col[0] for col in cursor.description]
                row_dict = dict(zip(columns, row))
                
                # Sử dụng phương thức classmethod từ Model để tạo đối tượng
                return Customer.from_row(row_dict)
            
            return None
            
        except Exception as e:
            print(f"Error in select_by_username: {e}")
            return None
        finally:
            cursor.close()