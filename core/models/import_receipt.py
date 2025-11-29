from dataclasses import dataclass 

@dataclass
class ImportReceipt:
    id: int 
    employee_id: int 
    import_date: str 

    def from_row(cls, row):
        if not row:
            return None 
        return cls(
            id=row['id'],
            employee_id=row['employee_id'],
            import_date=row['import_date']
        )