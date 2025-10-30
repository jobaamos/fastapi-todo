from fastapi import FastAPI, HTTPException, Query
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
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_todos(todos: List[dict]):
    """Save todos to JSON file"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=4, ensure_ascii=False)

# --- Model ---
class Todo(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    is_completed: bool
    department: Optional[str] = None   # new optional field

# --- Endpoints ---
@app.get("/api/departments")
def get_departments():
    """Return unique department names found in todos.json"""
    todos = load_todos()
    seen = []
    for t in todos:
        d = t.get("department")
        if d and d not in seen:
            seen.append(d)
    return {"departments": seen}

@app.get("/api/todos")
def get_todos(department: Optional[str] = Query(None, description="Filter todos by department")):
    todos = load_todos()
    if department:
        filtered = [t for t in todos if t.get("department") == department]
        return {"todos": filtered}
    return {"todos": todos}

@app.post("/api/todos")
def create_todo(todo: Todo):
    todos = load_todos()
    # allocate id robustly (handles non-sequential ids)
    max_id = max([t.get("id", 0) for t in todos], default=0)
    todo.id = max_id + 1
    # ensure department default
    if todo.department is None:
        todo.department = "General"
    todos.append(todo.dict())
    save_todos(todos)
    return {"message": "Todo created successfully", "todo": todo}

@app.get("/api/todos/{todo_id}")
def get_todo_by_id(todo_id: int):
    todos = load_todos()
    for todo in todos:
        if todo.get("id") == todo_id:
            return {"todo": todo}
    raise HTTPException(status_code=404, detail="Todo not found")

@app.put("/api/todos/{todo_id}")
def update_todo(todo_id: int, updated_todo: Todo):
    todos = load_todos()
    for index, todo in enumerate(todos):
        if todo.get("id") == todo_id:
            todos[index]["title"] = updated_todo.title
            todos[index]["description"] = updated_todo.description
            todos[index]["is_completed"] = updated_todo.is_completed
            # allow department update if present (can be None)
            if updated_todo.department is not None:
                todos[index]["department"] = updated_todo.department
            save_todos(todos)
            return {"message": "Todo updated successfully", "todo": todos[index]}
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: int):
    todos = load_todos()
    for index, todo in enumerate(todos):
        if todo.get("id") == todo_id:
            deleted_todo = todos.pop(index)
            save_todos(todos)
            return {"message": "Todo deleted successfully", "todo": deleted_todo}
    raise HTTPException(status_code=404, detail="Todo not found")

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_homepage():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()
