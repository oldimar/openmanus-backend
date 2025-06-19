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

from fastapi.responses import FileResponse
from app.docx_generator import generate_docx
import os

EXPORT_FOLDER = "exports"

@app.get("/generate-docx/{task_id}")
async def generate_task_docx(task_id: str):
    try:
        # Verifica se a task existe
        task = tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task ID not found")

        # Busca task result e description
        task_result = task["result"]
        task_description = task.get("description", "")

        # Verifica se tem pasta de arquivos (opcional - ajuste conforme sua lógica de upload)
        task_data_folder = None
        # Exemplo: Se você estiver salvando o task_id_files dentro da task:
        # task_data_folder = task.get("task_id_files", "")

        # Gera o DOCX
        output_path = generate_docx(
            task_id=task_id,
            task_result=task_result,
            task_description=task_description,
            file_folder=task_data_folder
        )

        # Retorna o arquivo para download
        if os.path.exists(output_path):
            filename = os.path.basename(output_path)
            return FileResponse(
                path=output_path,
                filename=filename,
                media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        else:
            raise HTTPException(status_code=500, detail="Falha ao gerar o DOCX.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar DOCX: {str(e)}")

from fastapi.responses import FileResponse
import os

EXPORT_FOLDER = "exports"

@app.get("/download/{task_id}")
async def download_docx(task_id: str):
    try:
        file_path = os.path.join(EXPORT_FOLDER, f"{task_id}.docx")
        if os.path.exists(file_path):
            filename = f"resultado_{task_id}.docx"
            return FileResponse(
                path=file_path,
                filename=filename,
                media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        else:
            raise HTTPException(status_code=404, detail="Arquivo DOCX não encontrado para essa task.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer download: {str(e)}")

