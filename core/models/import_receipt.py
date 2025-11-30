from dataclasses import dataclass 
from typing import Optional

@dataclass
class ImportReceipt:
    id: int 
    employee_id: int 
    import_date: str 
    is_confirm: bool = False # Trường mới

    @classmethod
    def from_row(cls, row):
        if not row:
            return None 
        
        is_confirm = False
        if 'is_confirm' in row.keys():
            is_confirm = bool(row['is_confirm'])

        return cls(
            id=row['id'],
            employee_id=row['employee_id'],
            import_date=row['import_date'],
            is_confirm=is_confirm
        )