import os
import sys
import hashlib
import random
from datetime import datetime, timedelta

# Thêm đường dẫn project vào sys.path để import được core
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from core.database import Database
from core.dao.employee_dao import EmployeeDAO
from core.dao.customer_dao import CustomerDAO
from core.dao.product_dao import ProductDAO
from core.dao.product_image_dao import ProductImageDAO
from core.dao.import_receipt_dao import ImportReceiptDAO
from core.dao.import_detail_dao import ImportDetailDAO
from core.dao.order_dao import OrderDAO
from core.dao.order_detail_dao import OrderDetailDAO

from core.models.employee import Employee
from core.models.customer import Customer
from core.models.product import Product
from core.models.product_image import ProductImage
from core.models.import_receipt import ImportReceipt
from core.models.import_detail import ImportDetail
from core.models.order import Order
from core.models.order_detail import OrderDetail

def create_data():
    print("--- BẮT ĐẦU TẠO DỮ LIỆU GIẢ ---")
    
    # 1. Kết nối Database
    db = Database()
    db.setup() # Đảm bảo bảng đã được tạo
    conn = db.get_connection()

    # Khởi tạo các DAO
    emp_dao = EmployeeDAO(conn)
    cus_dao = CustomerDAO(conn)
    prod_dao = ProductDAO(conn)
    img_dao = ProductImageDAO(conn)
    receipt_dao = ImportReceiptDAO(conn)
    receipt_detail_dao = ImportDetailDAO(conn)
    order_dao = OrderDAO(conn)
    order_detail_dao = OrderDetailDAO(conn)

    # 2. Xóa dữ liệu cũ (Optional - Cẩn thận khi dùng)
    # conn.execute("DELETE FROM order_details")
    # conn.execute("DELETE FROM orders")
    # conn.execute("DELETE FROM import_details")
    # conn.execute("DELETE FROM import_receipts")
    # conn.execute("DELETE FROM product_images")
    # conn.execute("DELETE FROM products")
    # conn.execute("DELETE FROM customers")
    # conn.execute("DELETE FROM employees")
    # conn.commit()
    # print("Đã xóa dữ liệu cũ.")

    # 3. Tạo Nhân viên (Employees)
    employees = []
    # Admin mặc định đã được tạo trong Database.setup(), nên ta chỉ tạo thêm nhân viên thường
    for i in range(1, 21):
        username = f"staff{i}"
        # Kiểm tra xem user đã tồn tại chưa để tránh lỗi UNIQUE
        if not emp_dao.select_by_username(username):
            pwd_hash = hashlib.sha256("123456".encode()).hexdigest()
            emp = Employee(
                id=0,
                username=username,
                password_hash=pwd_hash,
                full_name=f"Nhân viên {i}",
                is_manager=False,
                status='active'
            )
            emp_id = emp_dao.insert(emp)
            employees.append(emp_id)
            print(f"Tạo nhân viên: {username}")
    
    # Lấy ID của admin để dùng cho nhập kho
    admin_user = emp_dao.select_by_username("ADMIN")
    admin_id = admin_user.id if admin_user else employees[0]

    # 4. Tạo Khách hàng (Customers)
    customers = []
    for i in range(1, 31):
        username = f"customer{i}"
        pwd_hash = hashlib.sha256("123456".encode()).hexdigest()
        cus = Customer(
            id=0,
            username=username,
            password_hash=pwd_hash,
            full_name=f"Khách hàng {i}",
            phone=f"090{random.randint(1000000, 9999999)}",
            address=f"Số {i}, Đường ABC, Quận {random.randint(1, 12)}"
        )
        cus_id = cus_dao.insert(cus)
        customers.append(cus_id)
        print(f"Tạo khách hàng: {username}")

    # 5. Tạo Sản phẩm (Products)
    products = []
    product_names = [
        "Mì Hảo Hảo", "Nước tương Tam Thái Tử", "Dầu ăn Tường An", "Gạo ST25", 
        "Nước mắm Nam Ngư", "Bột giặt OMO", "Nước xả Downy", "Kem đánh răng PS",
        "Sữa tươi Vinamilk", "Sữa đặc Ông Thọ", "Bánh Cosy", "Bánh Chocopie",
        "Kẹo Alpengliebe", "Snack Oishi", "Nước ngọt Coca Cola", "Nước ngọt Pepsi",
        "Bia Tiger", "Bia Heineken", "Xúc xích Vissan", "Trứng gà Ba Huân"
    ]

    for i, name in enumerate(product_names):
        import_price = random.randint(5, 50) * 1000 # Giá nhập 5k - 50k
        sale_price = import_price * 1.2 # Lời 20%
        
        prod = Product(
            id=0,
            name=name,
            description=f"Mô tả cho sản phẩm {name}",
            supplier_info=f"Nhà cung cấp {random.choice(['A', 'B', 'C'])}",
            import_price=import_price,
            sale_price=sale_price,
            stock_quantity=0, # Ban đầu = 0, sẽ tăng khi nhập kho
            shelf_life_days=random.choice([180, 365, 720])
        )
        prod_id = prod_dao.insert(prod)
        products.append(prod_id)
        
        # Tạo ảnh giả (Không có file thật, chỉ lưu đường dẫn text)
        img = ProductImage(
            id=0,
            product_id=prod_id,
            image_path=f"data/images/prod_{prod_id}.jpg",
            feature_vector=None, # Chưa có vector thật
            is_thumbnail=True
        )
        img_dao.insert(img)
        print(f"Tạo sản phẩm: {name}")

    # 6. Nhập kho (Import Receipts) - Để tăng tồn kho
    # Tạo 5 phiếu nhập, mỗi phiếu nhập 5-10 loại sản phẩm
    for i in range(5):
        receipt = ImportReceipt(
            id=0,
            employee_id=admin_id,
            import_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        receipt_id = receipt_dao.insert(receipt)
        
        # Chi tiết nhập
        selected_prods = random.sample(products, k=random.randint(5, 10))
        for prod_id in selected_prods:
            qty = random.randint(50, 200)
            mfg_date = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
            
            detail = ImportDetail(
                id=0,
                receipt_id=receipt_id,
                product_id=prod_id,
                quantity=qty,
                manufacturing_date=mfg_date
            )
            receipt_detail_dao.insert(detail)
            
            # Cập nhật tồn kho cho sản phẩm
            current_prod = prod_dao.select_by_id(prod_id)
            current_prod.stock_quantity += qty
            prod_dao.update(current_prod)
            
        print(f"Tạo phiếu nhập kho #{receipt_id}")

    # 7. Tạo Đơn hàng (Orders) - Bán hàng
    # Tạo 20 đơn hàng ngẫu nhiên
    for i in range(20):
        is_online = random.choice([True, False])
        cus_id = random.choice(customers) if is_online else None
        emp_id = random.choice(employees) if not is_online else None
        
        order = Order(
            id=0,
            total_amount=0, # Tính sau
            customer_id=cus_id,
            employee_id=emp_id,
            order_date=(datetime.now() - timedelta(days=random.randint(0, 10))).strftime("%Y-%m-%d %H:%M:%S"),
            status='completed'
        )
        order_id = order_dao.insert(order)
        
        # Chi tiết đơn hàng
        total_money = 0
        selected_prods = random.sample(products, k=random.randint(1, 5))
        
        for prod_id in selected_prods:
            current_prod = prod_dao.select_by_id(prod_id)
            qty = random.randint(1, 5)
            
            # Kiểm tra tồn kho (đơn giản)
            if current_prod.stock_quantity >= qty:
                detail = OrderDetail(
                    id=0,
                    order_id=order_id,
                    product_id=prod_id,
                    quantity=qty,
                    unit_price=current_prod.sale_price
                )
                order_detail_dao.insert(detail)
                
                total_money += (qty * current_prod.sale_price)
                
                # Trừ tồn kho
                current_prod.stock_quantity -= qty
                prod_dao.update(current_prod)
        
        # Cập nhật tổng tiền đơn hàng
        # Order object ở đây là dataclass, cần update lại vào DB
        # Tuy nhiên hàm update order chưa có trong DAO của bạn, tôi sẽ viết câu SQL raw ở đây cho nhanh
        conn.execute("UPDATE orders SET total_amount = ? WHERE id = ?", (total_money, order_id))
        conn.commit()
        
        print(f"Tạo đơn hàng #{order_id} - Tổng tiền: {total_money:,.0f}")

    print("--- HOÀN TẤT TẠO DỮ LIỆU ---")
    db.close()

if __name__ == "__main__":
    create_data()