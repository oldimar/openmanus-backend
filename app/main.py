from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from app.logic import process_task, tasks, save_uploaded_file
import uuid
import os
from datetime import datetime

app = FastAPI()

# Rota 1: Criar uma task (com qualquer agente ou com orquestração)
@app.post("/tasks/")
async def create_task(task_text: dict = Body(...)):
    try:
        task_id = str(uuid.uuid4())
        result = await process_task(task_text, task_id)
        tasks[task_id] = {"status": "done", "result": result}
        return {"task_id": task_id, "status": "done", "result": result}
    except Exception as e:
        error_msg = f"Erro ao processar a task: {str(e)}"
        tasks[task_id] = {"status": "error", "result": error_msg}
        return {"task_id": task_id, "status": "error", "result": error_msg}

# Rota 2: Verificar status da task
@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    task = tasks.get(task_id)
    if task:
        return {"task_id": task_id, "status": task["status"], "result": task["result"]}
    else:
        raise HTTPException(status_code=404, detail="Task ID not found")

# Rota 3: Upload de arquivo único
@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    try:
        folder_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_path = os.path.join("uploads", folder_name)
        os.makedirs(folder_path, exist_ok=True)

        file_location = os.path.join(folder_path, file.filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())

        return {
            "task_id_files": folder_name,
            "filename": file.filename,
            "message": "File uploaded successfully"
        }
    except Exception as e:
        return {"error": str(e)}

# Rota 4: Upload de múltiplos arquivos
@app.post("/uploadfiles/")
async def upload_multiple_files(files: list[UploadFile] = File(...)):
    try:
        folder_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_path = os.path.join("uploads", folder_name)
        os.makedirs(folder_path, exist_ok=True)

        saved_files = []
        for file in files:
            file_location = os.path.join(folder_path, file.filename)
            with open(file_location, "wb") as f:
                f.write(await file.read())
            saved_files.append(file.filename)

        return {
            "task_id_files": folder_name,
            "filenames": saved_files,
            "message": "Files uploaded successfully"
        }
    except Exception as e:
        return {"error": str(e)}
