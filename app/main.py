from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .logic import process_task, tasks

class TaskRequest(BaseModel):
    task: str

app = FastAPI(title="OpenManus Backend")

@app.post("/task")
def create_task(req: TaskRequest):
    task_id = process_task(req.task)
    return {"task_id": task_id, "status": "processing"}

@app.get("/status/{task_id}")
def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task_id": task_id, **tasks[task_id]}
