from dataclasses import dataclass
from typing import Optional

@dataclass 
class ProductImage:
    id: int
    product_id: int
    image_path: Optional[str] = None 
    feature_vector: Optional[bytes] = None
    is_thumbnail: bool = False

    @classmethod 
    def from_row(cls, row):
        if not row:
            return None 
        return cls(
            id=row['id'],
            product_id=row['product_id'],
            image_path=row['image_path'],
            feature_vector=row['feature_vector'],
            is_thumbnail=bool(row['is_thumbnail'])
        )