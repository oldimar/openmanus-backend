from fastapi import FastAPI, UploadFile, File, Body
from app.logic import process_task, tasks
import os
from datetime import datetime
import shutil

app = FastAPI()

UPLOAD_FOLDER = "uploads"

@app.post("/tasks/")
async def create_task(task_text: dict = Body(...)):
    task_id = process_task(task_text)
    return {"task_id": task_id, "status": tasks[task_id]["status"]}

@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    task = tasks.get(task_id)
    if task:
        return {"task_id": task_id, "status": task["status"], "result": task["result"]}
    return {"error": "Task ID not found"}

@app.post("/uploadfile/")
async def upload_file(files: list[UploadFile] = File(...)):
    try:
        # Criar pasta com timestamp como task_id_files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_path = os.path.join(UPLOAD_FOLDER, timestamp)
        os.makedirs(folder_path, exist_ok=True)

        filenames = []

        for file in files:
            file_location = os.path.join(folder_path, file.filename)
            with open(file_location, "wb") as f:
                shutil.copyfileobj(file.file, f)
            filenames.append(file.filename)

        return {
            "task_id_files": timestamp,
            "filenames": filenames,
            "message": "Files uploaded successfully"
        }

    except Exception as e:
        return {"error": str(e)}
