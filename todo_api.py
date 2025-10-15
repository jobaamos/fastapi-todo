from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json
import os

app = FastAPI()

# JSON file path
DATA_FILE = "todos.json"

# --- Utility functions ---
def load_todos() -> List[dict]:
    """Load todos from JSON file"""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_todos(todos: List[dict]):
    """Save todos to JSON file"""
    with open(DATA_FILE, "w") as f:
        json.dump(todos, f, indent=4)

# --- Model ---
class Todo(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    is_completed: bool

# --- Endpoints ---
@app.get("/api/todos")
def get_todos():
    todos = load_todos()
    return {"todos": todos}

@app.post("/api/todos")
def create_todo(todo: Todo):
    todos = load_todos()
    todo.id = len(todos) + 1
    todos.append(todo.dict())
    save_todos(todos)
    return {"message": "Todo created successfully", "todo": todo}

@app.get("/api/todos/{todo_id}")
def get_todo_by_id(todo_id: int):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            return {"todo": todo}
    raise HTTPException(status_code=404, detail="Todo not found")

@app.put("/api/todos/{todo_id}")
def update_todo(todo_id: int, updated_todo: Todo):
    todos = load_todos()
    for index, todo in enumerate(todos):
        if todo["id"] == todo_id:
            todos[index]["title"] = updated_todo.title
            todos[index]["description"] = updated_todo.description
            todos[index]["is_completed"] = updated_todo.is_completed
            save_todos(todos)
            return {"message": "Todo updated successfully", "todo": todos[index]}
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: int):
    todos = load_todos()
    for index, todo in enumerate(todos):
        if todo["id"] == todo_id:
            deleted_todo = todos.pop(index)
            save_todos(todos)
            return {"message": "Todo deleted successfully", "todo": deleted_todo}
    raise HTTPException(status_code=404, detail="Todo not found")

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_homepage():
    with open("index.html") as f:
        return f.read()
