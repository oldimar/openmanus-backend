from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from app.logic import process_task, tasks
from app.docx_generator import generate_docx_from_result
import uuid
import os
from datetime import datetime
from fastapi.responses import FileResponse

app = FastAPI()

UPLOAD_FOLDER = "uploads"
DOCX_FOLDER = "generated_docs"

@app.post("/tasks/")
async def create_task(task_text: dict = Body(...)):
    try:
        task_id = str(uuid.uuid4())
        result = await process_task(task_text, task_id)
        tasks[task_id] = {"status": "done", "result": result}
        return {"task_id": task_id, "status": "done"}
    except Exception as e:
        error_msg = f"Erro ao processar a task: {str(e)}"
        tasks[task_id] = {"status": "error", "result": error_msg}
        return {"task_id": task_id, "status": "error", "result": error_msg}

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    task = tasks.get(task_id)
    if task:
        return {"task_id": task_id, "status": task["status"], "result": task["result"]}
    else:
        raise HTTPException(status_code=404, detail="Task ID not found")

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    try:
        folder_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
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

@app.post("/uploadfiles/")
async def upload_multiple_files(files: list[UploadFile] = File(...)):
    try:
        folder_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
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
        
from app.ocr_reader import extract_text_from_pdf

@app.get("/extract-pdf-text/{task_id_files}")
async def extract_pdf_text(task_id_files: str):
    try:
        extracted_text = extract_text_from_pdf(task_id_files)
        return {"task_id_files": task_id_files, "extracted_text": extracted_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao extrair texto: {str(e)}")

@app.get("/generate-docx/{task_id}")
async def generate_docx_endpoint(task_id: str):
    try:
        task = tasks.get(task_id)
        if not task or task["status"] != "done":
            raise HTTPException(status_code=404, detail="Task não encontrada ou não finalizada.")

        result = task["result"]
        output_path = generate_docx_from_result(task_id, result)

        if not os.path.exists(output_path):
            raise HTTPException(status_code=404, detail="Arquivo DOCX não encontrado.")

        return FileResponse(
            output_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"{task_id}.docx"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar DOCX: {str(e)}")

# 🆕 NOVA ROTA DE RESULTADO FORMATADO
@app.get("/tasks/{task_id}/formatted")
async def get_formatted_result(task_id: str):
    task = tasks.get(task_id)
    if not task or task.get("status") != "done":
        raise HTTPException(status_code=404, detail="Task não encontrada ou não finalizada.")

    structured = task.get("structured_result")
    if not structured:
        raise HTTPException(status_code=404, detail="Resultado estruturado ainda não disponível.")

    return {
        "task_id": task_id,
        "structured_result": structured
    }
