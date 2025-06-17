from fastapi import UploadFile, File
from uuid import uuid4
import os
import shutil

@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    # Gerar um task_id único
    task_id = str(uuid4())

    # Criar pasta para essa task
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
