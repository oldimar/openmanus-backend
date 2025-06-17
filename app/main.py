from fastapi import FastAPI, UploadFile, File
from typing import List
import os
from app.logic import process_task, tasks

app = FastAPI()

@app.post("/tasks/")
async def create_task(task_text: str):
    task_id = process_task(task_text)
    return {"task_id": task_id, "status": tasks[task_id]["status"]}

@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    task = tasks.get(task_id)
    if task:
        return {"task_id": task_id, "status": task["status"], "result": task["result"]}
    return {"error": "Task ID not found"}

@app.post("/uploadfile/")
async def upload_file(files: List[UploadFile] = File(...)):
    os.makedirs("uploads", exist_ok=True)
    saved_files = []

    try:
        for file in files:
            file_location = f"uploads/{file.filename}"
            with open(file_location, "wb") as f:
                f.write(await file.read())
            saved_files.append(file_location)

        return {"filenames": [file.filename for file in files], "message": "Files uploaded successfully"}

    except Exception as e:
        return {"error": str(e)}
