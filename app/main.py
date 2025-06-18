from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from app.logic import process_task, tasks, save_uploaded_file, save_uploaded_files
import uuid

app = FastAPI()


# Rota 1: Criar uma Task (orquestração ou task_type específico)
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
    try:
        task_id = str(uuid.uuid4())
        result = await process_task(task_text, task_id)
        tasks[task_id] = {"status": "done", "result": result}
        return {"task_id": task_id, "status": "done", "result": result}
    except Exception as e:
        error_msg = f"Erro ao processar a task: {str(e)}"
        tasks[task_id] = {"status": "error", "result": error_msg}
        return {"task_id": task_id, "status": "error", "result": error_msg}


# Rota 2: Consultar Status da Task
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
