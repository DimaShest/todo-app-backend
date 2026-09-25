from uuid import uuid4

from fastapi import FastAPI, status, HTTPException
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

class Book(BaseModel):
    book: str

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
    

tasks: list[Task] = []
categories: list[Category] = []
book: str = ""



@app.get("/tasks", response_model=list[Task])
def get_tasks():
    return tasks


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    task = Task(id=str(uuid4()), title=payload.title, completed=False)
    tasks.append(task)
    return task


@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, payload: TaskUpdate) -> Task:
    for task in tasks:
        if task.id == task_id:
            if payload.title is not None:
                task.title = payload.title
            if payload.completed is not None:
                task.completed = payload.completed
            return task

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str) -> None:
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)
            return

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")


@app.get("/categories", response_model=list[Category])
def get_categories():
    return categories


@app.post("/categories", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate):
    category = Category(id=str(uuid4()), name=payload.name)
    categories.append(category)
    return category


@app.patch("/categories/{category_id}", response_model=Category)
def update_category(category_id: str, payload: CategoryUpdate) -> Category:
    for category in categories:
        if category.id == category_id:
            category.name = payload.name
            return category

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена") 


@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: str) -> None:
    for category in categories:
        if category.id == category_id:
            categories.remove(category)
            return

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")










@app.get('/book', response_model=Book) 
def get_book():
    return {"book": "Любимая книга: " + book}
       
       
@app.post("/book", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(payload: Book):
    global book
    book = payload.book
    
    return payload