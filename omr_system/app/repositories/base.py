"""Repositório base genérico com operações CRUD."""
from typing import Generic, TypeVar, List, Optional, Type
from app.extensions import db

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """CRUD base para qualquer model SQLAlchemy."""

    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, id: int) -> Optional[T]:
        return self.model.query.filter_by(id=id, deleted_at=None).first()

    def get_all(self) -> List[T]:
        return self.model.query.filter_by(deleted_at=None).all()

    def paginate(self, page: int, per_page: int):
        return (
            self.model.query
            .filter_by(deleted_at=None)
            .order_by(self.model.id.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

    def save(self, entity: T) -> T:
        db.session.add(entity)
        db.session.commit()
        return entity

    def save_all(self, entities: List[T]) -> List[T]:
        db.session.add_all(entities)
        db.session.commit()
        return entities

    def delete(self, entity: T) -> None:
        """Soft-delete: apenas marca deleted_at."""
        entity.soft_delete()
        db.session.commit()

    def hard_delete(self, entity: T) -> None:
        """Remove fisicamente — use com cuidado."""
        db.session.delete(entity)
        db.session.commit()
