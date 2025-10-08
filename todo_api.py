from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
app = FastAPI()

from typing import Optional

class Todo(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    is_completed: bool


todos = []
@app.get("/api/todos")
def get_todos():
    return {"todos": todos}

@app.post("/api/todos")
def create_todo(todo: Todo):
    # Automatically assign ID
    todo.id = len(todos) + 1  
    todos.append(todo)
    return {"message": "Todo created successfully", "todo": todo}


@app.get("/api/todos/{todo_id}")
def get_todo_by_id(todo_id: int):
    for todo in todos:
        if todo.id == todo_id:
            return {"todo": todo}
    raise HTTPException(status_code=404, detail="Todo not found")

@app.put("/api/todos/{todo_id}")
def update_todo(todo_id: int, updated_todo: Todo):
    for index, todo in enumerate(todos):
        if todo.id == todo_id:
            todos[index].title = updated_todo.title
            todos[index].description = updated_todo.description
            todos[index].is_completed = updated_todo.is_completed
            return {"message": "Todo updated successfully", "todo": todos[index]}
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: int):
    for index, todo in enumerate(todos):
        if todo.id == todo_id:
            deleted_todo = todos.pop(index)
            return {"message": "Todo deleted successfully", "todo": deleted_todo}
    raise HTTPException(status_code=404, detail="Todo not found")
