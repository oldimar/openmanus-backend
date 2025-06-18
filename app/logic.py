import uuid
import os
import json
from datetime import datetime
from dotenv import load_dotenv

from app.agents.plan_agent import generate_plan
from app.agents.code_agent import generate_code
from app.agents.write_agent import generate_text
from app.agents.report_agent import generate_report
from app.agents.image_agent import generate_image

load_dotenv()

tasks = {}
UPLOAD_FOLDER = "uploads"
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


# Função para processar tasks (incluindo orquestração)
async def process_task(task_text, task_id):
    tasks[task_id] = {"status": "processing", "result": None}

    try:
        task_data = json.loads(task_text) if isinstance(task_text, str) else task_text
        task_description = task_data.get("task_description", "")
        task_type = task_data.get("task_type", "")
        task_id_files = task_data.get("task_id_files", "")

        # Orquestração automática se o texto pedir "planejar"
        if "planejar" in task_description.lower():
            plan_result = generate_plan(task_description)
            code_result = generate_code(plan_result)
            report_result = generate_report(code_result)
            write_result = generate_text(report_result)
            tasks[task_id]["result"] = write_result
            tasks[task_id]["status"] = "done"
            return write_result

        # Execução manual pelo campo task_type
        if task_type == "plan":
            result = generate_plan(task_description)

        elif task_type == "code":
            result = generate_code(task_description)

        elif task_type == "write":
            if task_id_files:
                folder_path = os.path.join(UPLOAD_FOLDER, task_id_files)
                try:
                    file_contents = []
                    for filename in os.listdir(folder_path):
                        file_path = os.path.join(folder_path, filename)
                        with open(file_path, "r", encoding="utf-8") as f:
                            file_contents.append(f.read())
                    combined_text = "\n\n".join(file_contents)
                    result = generate_text(combined_text)

                except FileNotFoundError:
                    raise Exception(f"Pasta '{folder_path}' não encontrada.")
                except Exception as e:
                    raise Exception(f"Erro ao ler arquivos: {str(e)}")
            else:
                result = generate_text(task_description)

        elif task_type == "report":
            result = generate_report(task_description)

        elif task_type == "image":
            result = generate_image(task_description)

        else:
            raise Exception(f"task_type '{task_type}' não reconhecido.")

        tasks[task_id]["result"] = result
        tasks[task_id]["status"] = "done"
        return result

    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["result"] = f"Erro ao processar a task: {str(e)}"
        return f"Erro ao processar a task: {str(e)}"


# Função para salvar um único arquivo
async def save_uploaded_file(file):
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


# Função para salvar múltiplos arquivos
async def save_uploaded_files(files):
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
