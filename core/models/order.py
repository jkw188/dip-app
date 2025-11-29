from dataclasses import dataclass
from typing import Optional

@dataclass 
class Order:
    id: int 
    total_amount: float 
    customer_id: Optional[int] = None 
    employee_id: Optional[int] = None
    order_date: Optional[str] = None 
    status: str = 'conpleted'

    @classmethod
    def from_row(cls, row):
        if not row:
            return None 
        return cls(
            id=row['id'],
            total_amount=row['total_amount'],
            customer_id=row['customer_id'],
            employee_id=row['employee_id'],
            order_date=row['order_date'],
            status=row['status']
        )