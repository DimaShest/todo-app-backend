from sqlalchemy.orm import Session

from app.repositories.task import (
    TaskRepository,
)
from app.schemas.task import (
    TaskCreate,
    TaskRead,
    TaskUpdate,
)


class TaskNotFound(Exception):
    """Исключение при отсутствии задачи в базе данных"""


class TaskService:
    """Ключевые операции с задачами, включая бизнес-логику, валидацию и прочее"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = TaskRepository(db)

    def list_tasks(
        self,
    ) -> list[TaskRead]:
        tasks = self.repository.get_all()
        return [TaskRead.model_validate(task) for task in tasks]

    def create_task(self, payload: TaskCreate) -> TaskRead:
        task = self.repository.create(title=payload.title)
        self.db.commit()
        return TaskRead.model_validate(task)

    def update_task(
        self,
        task_id: str,
        payload: TaskUpdate,
    ) -> TaskRead:
        task_for_update = self.repository.get_by_id(task_id)

        if task_for_update is None:
            raise TaskNotFound(f"Задача с id = {task_id} не найдена в базе данных")
        if payload.title is not None:
            task_for_update.title = payload.title
        if payload.completed is not None:
            task_for_update.completed = payload.completed

        self.db.commit()
        return TaskRead.model_validate(task_for_update)

    def delete_task(self, task_id: str) -> None:
        task_for_delete = self.repository.get_by_id(task_id)

        if task_for_delete is None:
            raise TaskNotFound(f"Задача с id = {task_id} не найдена в базе данных")

        self.repository.delete(task_for_delete)
        self.db.commit()
