from unittest.mock import Mock

import pytest

from app.models.category import CategoryORM
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.category import CategoryNotFoundError, CategoryService


def test_list_categories_returns_pydantic_models(
    category_service: CategoryService,
    category_repository_mock: Mock,
) -> None:
    category_repository_mock.get_all.return_value = [
        CategoryORM(id="001", name="Категория 1"),
        CategoryORM(id="002", name="Категория 2"),
    ]

    result = category_service.list_categories()

    assert result == [
        CategoryRead(id="001", name="Категория 1"),
        CategoryRead(id="002", name="Категория 2"),
    ]


def test_create_category_commits_created_task(
    category_service: CategoryService,
    db_mock: Mock,
    category_repository_mock: Mock,
) -> None:
    created_category = CategoryORM(id="001", name="Новая категория")
    category_repository_mock.create.return_value = created_category

    result = category_service.create_category(CategoryCreate(name="Новая категория"))

    category_repository_mock.create.assert_called_once_with(name="Новая категория")
    db_mock.commit.assert_called_once_with()
    assert result.model_dump() == {
        "id": "001",
        "name": "Новая категория",
    }


def test_update_category_commits_returns_pydantic_model(
    category_service: CategoryService,
    db_mock: Mock,
    category_repository_mock: Mock,
) -> None:
    category = CategoryORM(id="001", name="Старая категория")
    category_repository_mock.get_by_id.return_value = category

    result = category_service.update_category(
        "001", CategoryUpdate(name="Обновленная категория")
    )

    category_repository_mock.get_by_id.assert_called_once_with("001")
    db_mock.commit.assert_called_once_with()
    assert result.model_dump() == {
        "id": "001",
        "name": "Обновленная категория",
    }


def test_update_category_raises_when_category_not_found(
    category_service: CategoryService,
    db_mock: Mock,
    category_repository_mock: Mock,
) -> None:
    category_repository_mock.get_by_id.return_value = None

    with pytest.raises(CategoryNotFoundError):  # Должна произойти указанная ошибка
        category_service.update_category(
            "missing_category_id", CategoryUpdate(name="Новая категория")
        )

    db_mock.commit.assert_not_called()  # Проверяем, что коммит не был вызван


def test_delete_category_commits(
    category_service: CategoryService,
    db_mock: Mock,
    category_repository_mock: Mock,
) -> None:
    category = CategoryORM(id="001", name="Категория для удаления")
    category_repository_mock.get_by_id.return_value = category

    category_service.delete_category("001")

    category_repository_mock.get_by_id.assert_called_once_with("001")
    category_repository_mock.delete.assert_called_once_with(category)
    db_mock.commit.assert_called_once_with()


def test_delete_category_raises_when_category_not_found(
    category_service: CategoryService,
    db_mock: Mock,
    category_repository_mock: Mock,
) -> None:
    category_repository_mock.get_by_id.return_value = None

    with pytest.raises(CategoryNotFoundError):  # Должна произойти указанная ошибка
        category_service.delete_category("missing_category_id")

    db_mock.commit.assert_not_called()  # Проверяем, что коммит не был вызван
