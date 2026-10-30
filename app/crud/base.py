from sqlalchemy import Select
from sqlalchemy.orm import Session

from app.core.deps import Pagination


def save(db: Session, obj):
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, obj, changes: dict):
    for campo, valor in changes.items():
        setattr(obj, campo, valor)
    return save(db, obj)


def deactivate(db: Session, obj):
    obj.activo = False
    return save(db, obj)


def paginate(stmt: Select, page: Pagination) -> Select:
    return stmt.limit(page.limit).offset(page.offset)
