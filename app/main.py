from fastapi import FastAPI, UploadFile, File
from app.logic import process_task, tasks
import os
import shutil

app = FastAPI()

# Rota: Criar Task
@app.post("/tasks/")
async def create_task(task_text: str):
    task_id = process_task(task_text)
    return {"task_id": task_id, "status": tasks[task_id]["status"]}

# Rota: Verificar Status
@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    task = tasks.get(task_id)
    if task:
        return {"task_id": task_id, "status": task["status"], "result": task["result"]}
    return {"error": "Task ID not found"}

# Rota: Upload de Arquivo
@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Garantir que a pasta uploads exista
        upload_folder = "uploads"
        os.makedirs(upload_folder, exist_ok=True)

        # Caminho final do arquivo
        file_path = os.path.join(upload_folder, file.filename)

        # Salvar o arquivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"filename": file.filename, "message": "File uploaded successfully"}

    except Exception as e:
        return {"error": str(e)}
