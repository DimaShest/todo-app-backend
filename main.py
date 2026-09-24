from uuid import uuid4

from fastapi import FastAPI, status
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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


class Book(BaseModel):
    book: str


tasks: list[Task] = []
book: str = ""


@app.get("/tasks", response_model=list[Task])
def get_tasks():
    """Получить список задач"""
    print(book)
    return tasks


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    """Создать новую задачу"""
    task = Task(id=str(uuid4()), title=payload.title, completed=False)
    tasks.append(task)
    return task


@app.get('/book', response_model=Book) 
def get_book():
    return {"book": "Любимая книга: " + book}
    
    
@app.post("/book", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(payload: Book):
    global book
    book = payload.book
    
    return payload