import sqlite3
import numpy as np
import io 
import hashlib
from datetime import datetime 

class Database:
    def __init__(self, db_path='data/db/shop.db'):
        self.conn = sqlite3.connect(
            db_path, 
            check_same_thread=False # Khi làm việc với GUI có thể gây lỗi xử lý luồng dữ liệu
        )
        self.conn.row_factory = sqlite3.Row
        self.conn.execute('PRAGMA FOREIGN_KEYS = 1') # bật foreign key
        self.cursor = self.conn.cursor()

    def setup(self):
        self.create_tables()
        self.init_admin_account()

    def create_tables(self):
        # code tạo cơ sở dữ liệu
        sql_script = """
            -- 1. Bảng Nhân viên
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                is_manager INTEGER DEFAULT 0, -- 1: Quản lý, 0: Nhân viên
                status TEXT DEFAULT 'active'  -- 'active' hoặc 'resigned'
            );

            -- 2. Bảng Khách hàng
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                phone TEXT,
                address TEXT
            );

            -- 3. Bảng Sản phẩm
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                supplier_info TEXT, 
                import_price REAL,  
                sale_price REAL NOT NULL,
                stock_quantity INTEGER DEFAULT 0,
                shelf_life_days INTEGER DEFAULT 0,
                is_deleted INTEGER DEFAULT 0 -- Hỗ trợ xóa mềm
            );

            -- 4. Bảng Hình ảnh sản phẩm
            CREATE TABLE IF NOT EXISTS product_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                image_path TEXT,      
                feature_vector BLOB,  
                is_thumbnail INTEGER DEFAULT 0, 
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            );

            -- 5. Bảng Phiếu nhập
            CREATE TABLE IF NOT EXISTS import_receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                import_date TEXT DEFAULT CURRENT_TIMESTAMP,
                is_confirm INTEGER DEFAULT 0, -- Trạng thái duyệt nhập kho
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            );

            -- 6. Bảng Chi tiết nhập
            CREATE TABLE IF NOT EXISTS import_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                receipt_id INTEGER,
                product_id INTEGER,
                quantity INTEGER NOT NULL,
                manufacturing_date TEXT, 
                FOREIGN KEY (receipt_id) REFERENCES import_receipts(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id)
            );

            -- 7. Bảng Hóa đơn
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                employee_id INTEGER, 
                order_date TEXT DEFAULT CURRENT_TIMESTAMP,
                total_amount REAL,
                status TEXT DEFAULT 'completed',
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
                FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE SET NULL
            );

            -- 8. Bảng Chi tiết hóa đơn
            CREATE TABLE IF NOT EXISTS order_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                unit_price REAL, 
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id)
            );
            
            -- 9. Bảng Đơn nghỉ việc (Offboard Requests)
             CREATE TABLE IF NOT EXISTS offboard_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                reason TEXT,
                request_date TEXT DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending', -- pending, approved, rejected
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            );
        """
        try:
            self.cursor.executescript(sql_script)
            self.conn.commit()
            print('Create tables successfully!!')
        except Exception as e:
            print(f'Error creating tables: {e}')

    # Các hàm hỗ trợ
    def init_admin_account(self):
        try:
            check = self.cursor.execute(
                "SELECT * FROM EMPLOYEES WHERE USERNAME='ADMIN' "
            ).fetchone()
            if not check:
                pwd_hash = hashlib.sha256("123456".encode()).hexdigest()
                self.cursor.execute(
                    "INSERT INTO employees (username, password_hash, full_name, is_manager) VALUES (?, ?, ?, ?)",
                    ("ADMIN", pwd_hash, "System Admin", 1)
                )
                self.conn.commit()
                print('Init admin account successfully!!')
        except Exception as e:
            print(f'Error checking admin account: {e}')

    # Chuyển đổi qua lại giữa BLOB trong csdl và mảng np
    def adapt_array(self, arr):
        out= io.BytesIO()
        np.save(out, arr)
        out.seek(0)
        return out.read()
    def convert_array(self, text):
        out = io.BytesIO(text)
        out.seek(0)
        return np.load(out)
    
    # lấy kết nối
    def get_connection(self):
        return self.conn

    # đóng kết nối
    def close(self):
        self.conn.close()

# Phần test nhanh khi chạy trực tiếp file này
if __name__ == "__main__":
    # Code khởi tạo db (chỉ cần chạy 1 lần)
    init_db = Database()
    init_db.setup()
    init_db.close()
