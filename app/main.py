from fastapi import FastAPI, UploadFile, File
from logic import process_task, tasks
from fastapi.responses import JSONResponse
from uuid import uuid4
import os
import shutil

app = FastAPI()

# Endpoint original - Criação de tarefa (usa os agentes logic.py)
@app.post("/task")
async def create_task(task_text: str):
    task_id = process_task(task_text)
    return {"task_id": task_id}

# Endpoint original - Verificar status da tarefa
@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task = tasks.get(task_id)
    if task:
        return {"task_id": task_id, **task}
    else:
        return JSONResponse(status_code=404, content={"error": "Task not found"})

# Novo Endpoint - Upload de arquivos
@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    task_id = str(uuid4())
    upload_folder = f"app/uploads/{task_id}"
    os.makedirs(upload_folder, exist_ok=True)

    saved_files = []

    for file in files:
        file_path = os.path.join(upload_folder, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(file.filename)

    return {
        "task_id": task_id,
        "status": "success",
        "saved_files": saved_files,
        "path": upload_folder
    }
