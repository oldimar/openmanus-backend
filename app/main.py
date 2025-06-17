from fastapi import FastAPI, UploadFile, File
from app.logic import process_task, tasks
from pydantic import BaseModel
import os
import shutil
from uuid import uuid4
from typing import List

app = FastAPI()

# Modelo para criar uma task
class TaskRequest(BaseModel):
    task_text: str
    task_id_files: str | None = None  # Novo campo opcional para referenciar arquivos de upload

# Endpoint: Criar uma nova task
@app.post("/tasks/")
async def create_task(request: TaskRequest):
    task_id = process_task(request.task_text, request.task_id_files)
    return {"task_id": task_id, "status": tasks[task_id]["status"]}

# Endpoint: Consultar status de uma task
@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    task = tasks.get(task_id)
    if task:
        return {"task_id": task_id, "status": task["status"], "result": task["result"]}
    return {"error": "Task ID not found"}

# Endpoint: Upload de múltiplos arquivos
@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    try:
        # Gera um novo task_id exclusivo para os arquivos
        task_id = str(uuid4())

        # Cria a pasta de destino
        upload_folder = os.path.join("uploads", task_id)
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
            "folder_path": upload_folder
        }

    except Exception as e:
        return {"error": str(e)}
