from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from app.logic import process_task, tasks, save_uploaded_file, save_uploaded_files
import uuid

app = FastAPI()

# Criar uma task
@app.post("/tasks/")
async def create_task(
    task_text: dict = Body(
        ...,
        example={
            "task_description": "Planejar uma sequência de atividades para o 2º ano",
            "task_type": "plan",
            "task_id_files": "20240618_123456"
        }
    )
):
    task_id = str(uuid.uuid4())
    # Apenas cria a task de forma assíncrona (não devolve o result)
    await process_task(task_text, task_id)
    return {"task_id": task_id, "status": tasks[task_id]["status"]}

# Consultar status e resultado da task
@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    task = tasks.get(task_id)
    if task:
        return {"task_id": task_id, "status": task["status"], "result": task["result"]}
    else:
        raise HTTPException(status_code=404, detail="Task ID not found")

# Upload de arquivo único
@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    try:
        return await save_uploaded_file(file)
    except Exception as e:
        return {"error": str(e)}

# Upload de múltiplos arquivos
@app.post("/uploadfiles/")
async def upload_files(files: list[UploadFile] = File(...)):
    try:
        return await save_uploaded_files(files)
    except Exception as e:
        return {"error": str(e)}
