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


async def process_task(task_text, task_id):
    tasks[task_id] = {"status": "processing", "result": None}

    try:
        task_data = json.loads(task_text) if isinstance(task_text, str) else task_text
        task_description = task_data.get("task_description", "")
        task_type = task_data.get("task_type", "")
        task_id_files = task_data.get("task_id_files", "")

        # 👉 1. Lê o conteúdo dos arquivos (se houver uploads)
        extra_context = ""
        if task_id_files:
            folder_path = os.path.join(UPLOAD_FOLDER, task_id_files)
            if os.path.exists(folder_path):
                file_contents = []
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            file_contents.append(f.read())
                    except Exception as e:
                        file_contents.append(f"[Erro ao ler {filename}: {str(e)}]")
                extra_context = "\n\n".join(file_contents)

        # 👉 2. Monta o prompt final com anexo + descrição
        final_prompt = f"{task_description}\n\n{extra_context}" if extra_context else task_description

        # 👉 3. Se task_type vier definido → força o agente escolhido
        if task_type:
            if task_type == "plan":
                result = generate_plan(final_prompt)
            elif task_type == "code":
                result = generate_code(final_prompt)
            elif task_type == "write":
                result = generate_text(final_prompt)
            elif task_type == "report":
                result = generate_report(final_prompt)
            elif task_type == "image":
                result = generate_image(final_prompt)
            else:
                tasks[task_id]["status"] = "error"
                tasks[task_id]["result"] = f"Erro: task_type '{task_type}' não reconhecido."
                return
        else:
            # 👉 4. Se task_type não vier → Decidir automaticamente com base na descrição
            desc_lower = task_description.lower()

            if "planejar" in desc_lower:
                plan_result = generate_plan(final_prompt)
                code_result = generate_code(plan_result)
                report_result = generate_report(code_result)
                result = generate_text(report_result)

            elif "código" in desc_lower or "code" in desc_lower:
                result = generate_code(final_prompt)

            elif "relatório" in desc_lower:
                result = generate_report(final_prompt)

            elif "imagem" in desc_lower:
                result = generate_image(final_prompt)

            else:
                result = generate_plan(final_prompt)

        tasks[task_id]["result"] = result
        tasks[task_id]["status"] = "done"

    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["result"] = f"Erro interno ao processar a task: {str(e)}"


# Upload de arquivo único
async def save_uploaded_file(file):
    folder_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    file_location = os.path.join(folder_path, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    return {"task_id_files": folder_name, "filename": file.filename, "message": "File uploaded successfully"}


# Upload de múltiplos arquivos
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
    return {"task_id_files": folder_name, "filenames": saved_files, "message": "Files uploaded successfully"}
