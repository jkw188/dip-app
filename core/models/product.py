from dataclasses import dataclass
from typing import Optional

@dataclass 
class Product:
    id: int 
    name: str 
    sale_price: float 
    description: Optional[str] = None 
    supplier_info: Optional[str] = None 
    import_price: Optional[float] = 0.0
    stock_quantity: int = 0 
    shelf_life_days: int = 0
    is_deleted: bool = False # Trường mới

    @classmethod 
    def from_row(cls, row):
        if not row:
            return None 
        
        # Xử lý tương thích ngược: Nếu DB chưa có cột này thì mặc định False
        is_deleted = False
        if 'is_deleted' in row.keys():
            is_deleted = bool(row['is_deleted'])
            
        return cls(
            id=row['id'],
            name=row['name'],
            sale_price=row['sale_price'],
            description=row['description'],
            supplier_info=row['supplier_info'],
            import_price=row['import_price'],
            stock_quantity=row['stock_quantity'],
            shelf_life_days=row['shelf_life_days'],
            is_deleted=is_deleted
        )