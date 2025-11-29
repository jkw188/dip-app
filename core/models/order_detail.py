from dataclasses import dataclass 

@dataclass
class OrderDetail:
    id: int 
    order_id: int 
    product_id: int
    quantity: int 
    unit_price: float

    @classmethod
    def from_row(cls, row):
        if not row:
            return None 
        return cls(
            id=row['id'],
            order_id=row['order_id'],
            product_id=row['product_id'],
            quantity=row['quantity'],
            unit_price=row['unit_price']
        )
