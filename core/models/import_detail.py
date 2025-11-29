from dataclasses import dataclass 
from typing import Optional 

@dataclass 
class ImportDetail:
    id: int 
    receipt_id: int 
    product_id: int 
    quantity: int 
    manufacturing_date: Optional[str] = None

    @classmethod
    def from_row(cls, row):
        if not row:
            return None 
        return cls(
            id=row['id'],
            receipt_id=row['receipt_id'],
            product_id=row['product_id'],
            quantity=row['quantity'],
            manufacturing_date=row['manufacturing_date']
        )