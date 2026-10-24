from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.category import (
    CategoryRepository,
)
from app.schemas.category import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
)


class CategoryNotFoundException(Exception):
    """Исключение при отсутствии категории в базе данных"""


class CategoryService:
    def __init__(
        self,
        db: Session = Depends(get_db),
    ):
        self.db = db
        self.repository = CategoryRepository(db)

    def list_categories(
        self,
    ) -> list[CategoryRead]:
        categories_orm = self.repository.get_all()
        categories = [
            CategoryRead.model_validate(category) for category in categories_orm
        ]

        return categories

    def create_category(self, payload: CategoryCreate) -> CategoryRead:
        new_category = self.repository.create(name=payload.name)

        self.db.commit()

        return CategoryRead.model_validate(new_category)

    def update_category(
        self,
        category_id: str,
        payload: CategoryUpdate,
    ) -> CategoryRead:
        category_orm = self.repository.get_by_id(category_id)

        if category_orm is None:
            raise CategoryNotFoundException(
                f"Категория с id = {category_id} не найдена в базе данных"
            )

        if category_orm is not None:
            category_orm.name = payload.name
            self.db.commit()

        return CategoryRead.model_validate(category_orm)

    def delete_category(self, category_id: str) -> None:
        category_orm = self.repository.get_by_id(category_id)

        if category_orm is None:
            raise CategoryNotFoundException(
                f"Категория с id = {category_id} не найдена в базе данных"
            )

        self.repository.delete(category_orm)
        self.db.commit()
