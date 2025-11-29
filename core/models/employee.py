from dataclasses import dataclass

@dataclass
class Employee:
    id: int 
    username: str 
    password_hash: str 
    full_name: str 
    is_manager: bool = False 
    status: str = 'active'

    @classmethod 
    def from_row(cls, row):
        if not row:
            return None
        return cls(
            id=row['id'],
            username=row['username'],
            password_hash=row['password_hash'],
            full_name=row['full_name'],
            is_manager=bool(row['is_manager']),
            status=row['status']
        )
