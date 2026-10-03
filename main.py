from unicodedata import category
from uuid import uuid4

from fastapi import Depends, FastAPI, status, HTTPException
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

###############################################################################
DATABASE_URL = "postgresql+psycopg://postgres:admin@127.0.0.1:5432/postgres"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей таблиц БД"""
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))


class TaskORM(Base):
    """Модель для таблицы задачи в Базе Данных"""
    __tablename__ = "tasks"

    title: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False) # по умолчанию False
    
class CategoryORM(Base):
    __tablename__ = "categories"
    
    name: Mapped[str]


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

def get_db():
    """Функция для создания сессий с БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
###############################################################################

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

class Task(BaseModel):
    """Модель задачи"""
    id: str
    title: str
    completed: bool = False

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: str | None = None
    completed: bool | None = None
    
class Book(BaseModel):
    book: str

class Category(BaseModel):
    """Модель категории"""
    id: str
    name: str

class CategoryCreate(BaseModel):
    name: str

class CategoryUpdate(BaseModel):
    name: str  
    





def task_to_model(task: TaskORM) -> Task:
    """Конвертация объекта ORM в Pydantic"""
    return Task(id=task.id, title=task.title, completed=task.completed)

def category_to_model(category: CategoryORM) -> Category:
    """Конвертация объекта category из ORM в Pydantic"""
    return Category(id=category.id, name=category.name)


@app.get("/tasks", response_model=list[Task])
def get_tasks(db: Session = Depends(get_db)) -> list[Task]:
    """Получить список задач"""
    tasks = db.scalars(select(TaskORM)).all()
    return [task_to_model(task) for task in tasks]



@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> Task:
    """Создать новую задачу"""
    task = TaskORM(title=payload.title, completed=False)

    db.add(task)
    db.commit()
    return task_to_model(task)


@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, payload: TaskUpdate, db: Session = Depends(get_db)) -> Task:
    """
    Обновить существующую задачу
    task_id получаем из url
    payload получаем из тела запроса
    """
    task = db.get(TaskORM, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

    task.title = payload.title if payload.title is not None else task.title
    task.completed = payload.completed if payload.completed is not None else task.completed
    db.commit()
    return task_to_model(task)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: Session = Depends(get_db)) -> None:
    """Удалить задачу"""
    task = db.get(TaskORM, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

    db.delete(task)
    db.commit()
    
    
    
    

@app.get("/categories", response_model=list[Category])
def get_categories(db: Session = Depends(get_db)) -> list[Category]:
    categories_orm = db.scalars(select(CategoryORM)).all()
    categories = [category_to_model(category) for category in categories_orm]
    return categories


@app.post("/categories", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate,  db: Session = Depends(get_db)):
    category_orm = CategoryORM(name=payload.name)
    db.add(category_orm)
    db.commit()

    return category_to_model(category_orm)


@app.patch("/categories/{category_id}", response_model=Category)
def update_category(category_id: str, payload: CategoryUpdate, db: Session = Depends(get_db)) -> Category:
    category_orm = db.get(CategoryORM, category_id)
    
    if category_orm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена") 
    if category_orm is not None:
        category_orm.name = payload.name
        db.commit()
        
    return category_to_model(category_orm)
    

@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: str, db: Session = Depends(get_db)) -> None:
    category_orm = db.get(CategoryORM, category_id)
    
    if category_orm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")
    
    db.delete(category_orm)
    db.commit()


    


class Book(BaseModel):
    book: str
book: str = ""

@app.get('/book', response_model=Book) 
def get_book():
    return {"book": "Любимая книга: " + book}
       
       
@app.post("/book", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(payload: Book):
    global book
    book = payload.book
    
    return payload