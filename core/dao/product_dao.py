from .base_dao import BaseDAO
from core.models.product import Product 

class ProductDAO(BaseDAO):
    def select_all(self):
        self.cursor.execute("SELECT * FROM products")
        rows = self.cursor.fetchall()
        return [Product.from_row(row) for row in rows]

    def select_by_id(self, product_id):
        self.cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = self.cursor.fetchone()
        return Product.from_row(row)
    
    def search_by_name(self, keyword):
        self.cursor.execute("SELECT * FROM products WHERE name LIKE ?", ('%' + keyword + '%',))
        rows = self.cursor.fetchall()
        return [Product.from_row(row) for row in rows]

    def insert(self, p: Product):
        query = """
            INSERT INTO products (name, description, supplier_info, import_price, sale_price, stock_quantity, shelf_life_days)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (p.name, p.description, p.supplier_info, p.import_price, p.sale_price, p.stock_quantity, p.shelf_life_days))
        self.commit()
        return self.cursor.lastrowid

    def update(self, p: Product):
        query = """
            UPDATE products 
            SET name=?, description=?, supplier_info=?, import_price=?, sale_price=?, stock_quantity=?, shelf_life_days=?
            WHERE id=?
        """
        self.cursor.execute(query, (p.name, p.description, p.supplier_info, p.import_price, p.sale_price, p.stock_quantity, p.shelf_life_days, p.id))
        self.commit()

    def delete(self, product_id):
        self.cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        self.commit()