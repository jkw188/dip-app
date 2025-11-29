from dataclasses import dataclass

@dataclass 
class Customer:
    id: int
    username: str
    password_hash: str
    full_name: str
    phone: str
    address: str

    @classmethod 
    def from_row(cls, row):
        if not row:
            return None 
        return cls(
            id=row['id'],
            username=row['username'],
            password_hash=row['password_hash'],
            full_name=row['full_name'],
            phone=row['phone'],
            address=row['address']
        )