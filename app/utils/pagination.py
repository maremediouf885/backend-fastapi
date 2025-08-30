from typing import List, TypeVar, Generic
from pydantic import BaseModel
from sqlalchemy.orm import Query

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

def paginate(query: Query, page: int = 1, size: int = 50) -> dict:
    """Utilitaire pour paginer les résultats de requête"""
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }