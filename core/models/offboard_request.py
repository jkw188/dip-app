from dataclasses import dataclass
from typing import Optional

@dataclass
class OffboardRequest:
    id: int
    employee_id: int
    reason: str
    request_date: Optional[str] = None
    status: str = 'pending'
    employee_name: Optional[str] = None # Dùng để join và hiển thị tên

    @classmethod
    def from_row(cls, row):
        if not row: return None
        # Xử lý trường hợp join có thêm cột full_name
        emp_name = row['full_name'] if 'full_name' in row.keys() else None
        
        return cls(
            id=row['id'],
            employee_id=row['employee_id'],
            reason=row['reason'],
            request_date=row['request_date'],
            status=row['status'],
            employee_name=emp_name
        )