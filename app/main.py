from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from app.logic import process_task, tasks, save_uploaded_file, save_uploaded_files
import uuid

app = FastAPI()

# Rota 1: Criar uma task (com ou sem task_type)
@app.post("/tasks/")
async def create_task(
    task_text: dict = Body(
        ...,
        example={
            "task_description": "Planejar uma sequência de atividades para o 2º ano com imagens",
            "task_type": "",  # Pode ser deixado vazio para o sistema decidir automaticamente
            "task_id_files": "20250618_134129"
        }
    )
):
    task_id = str(uuid.uuid4())
    await process_task(task_text, task_id)
    return {"task_id": task_id, "status": tasks[task_id]["status"]}

# Rota 2: Consultar status + resultado
@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    task = tasks.get(task_id)
    if task:
        return {
            "task_id": task_id,
            "status": task["status"],
            "result": task["result"]
        }
    else:
        raise HTTPException(status_code=404, detail="Task ID not found")

# Rota 3: Upload de arquivo único
@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    try:
        return await save_uploaded_file(file)
    except Exception as e:
        return {"error": str(e)}

# Rota 4: Upload de múltiplos arquivos
@app.post("/uploadfiles/")
async def upload_files(files: list[UploadFile] = File(...)):
    try:
        return await save_uploaded_files(files)
    except Exception as e:
        return {"error": str(e)}
