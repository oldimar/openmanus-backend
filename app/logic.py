import uuid
import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv

from app.agents.code_agent import generate_code
from app.agents.write_agent import generate_text, generate_text_from_activity
from app.agents.report_agent import generate_report
from app.agents.image_agent import generate_images_from_list
from app.agents.task_router_agent import decide_agents

from app.ocr_reader import extract_text_from_pdf
from app.formatters import format_task_output_as_worksheet, format_atividades_para_app

load_dotenv()

tasks = {}
UPLOAD_FOLDER = "uploads"
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def extrair_numero_atividades(descricao: str, default: int = 5) -> int:
    match = re.search(r"\b(\d+)\s+(atividades|questões|perguntas|exercícios)", descricao.lower())
    if match:
        return int(match.group(1))
    return default


async def process_task(task_text, task_id):
    tasks[task_id] = {"status": "processing", "result": None, "structured_result": None}

    try:
        task_data = json.loads(task_text) if isinstance(task_text, str) else task_text
        task_description = task_data.get("task_description", "")
        task_type = task_data.get("task_type", "")
        task_id_files = task_data.get("task_id_files", "")
        task_grade = task_data.get("task_grade", "")

        extra_context = ""
        if task_id_files:
            folder_path = os.path.join(UPLOAD_FOLDER, task_id_files)
            if os.path.exists(folder_path):
                file_contents = []

                try:
                    pdf_text = extract_text_from_pdf(task_id_files)
                    if pdf_text and "Nenhum PDF" not in pdf_text:
                        file_contents.append(pdf_text)
                except Exception as e:
                    file_contents.append(f"[Erro ao extrair texto de PDF: {str(e)}]")

                for filename in os.listdir(folder_path):
                    if filename.lower().endswith(".txt"):
                        file_path = os.path.join(folder_path, filename)
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                file_contents.append(f.read())
                        except Exception as e:
                            file_contents.append(f"[Erro ao ler {filename}: {str(e)}]")

                extra_context = "\n\n".join(file_contents)

        final_prompt = f"{task_description}\n\n{extra_context}" if extra_context else task_description
        if task_grade:
            final_prompt += f"\n\n[Série/ano da turma: {task_grade}]"

        quantidade_atividades = extrair_numero_atividades(task_description)

        # ✅ FLUXO — DIAGNOSTICA
        if task_type == "diagnostica":
            from app.task_types.diagnostica import gerar_atividades_diagnosticas
            atividades = gerar_atividades_diagnosticas(final_prompt, task_grade)
            atividades_formatadas = format_atividades_para_app(atividades)
            tasks[task_id]["result"] = json.dumps(atividades, ensure_ascii=False, indent=2)
            tasks[task_id]["structured_result"] = atividades_formatadas
            tasks[task_id]["status"] = "done"
            save_task_log(task_id=task_id, task_data=task_data, agents_run=["diagnostica"], results=tasks[task_id]["result"])
            return tasks[task_id]["result"], tasks[task_id]["structured_result"]

        # ✅ FLUXO — TRILHA
        elif task_type == "trilha":
            from app.task_types.trilha import gerar_atividades_trilha
            atividades = gerar_atividades_trilha(final_prompt, task_grade)
            atividades_formatadas = format_atividades_para_app(atividades)
            tasks[task_id]["result"] = json.dumps(atividades, ensure_ascii=False, indent=2)
            tasks[task_id]["structured_result"] = atividades_formatadas
            tasks[task_id]["status"] = "done"
            save_task_log(task_id=task_id, task_data=task_data, agents_run=["trilha"], results=tasks[task_id]["result"])
            return tasks[task_id]["result"], tasks[task_id]["structured_result"]

        # ❌ FLUXO DESCONHECIDO
        else:
            raise Exception(f"Tipo de task '{task_type}' não suportado. Use 'diagnostica' ou 'trilha'.")

    except Exception as e:
        erro_msg = f"Erro ao processar a task: {str(e)}"
        tasks[task_id]["status"] = "error"
        tasks[task_id]["result"] = erro_msg
        save_task_log(task_id, task_data if 'task_data' in locals() else {}, [], erro_msg)

    return tasks[task_id]["result"], tasks[task_id]["structured_result"]


def run_agent_by_type(agent_type, prompt_text, quantidade_atividades=5):
    if agent_type == "code":
        return generate_code(prompt_text)
    elif agent_type == "write":
        return generate_text(prompt_text, quantidade_atividades)
    elif agent_type == "report":
        return generate_report(prompt_text)
    elif agent_type == "image":
        return generate_images_from_list([{"tema": prompt_text}])
    else:
        raise Exception(f"Agente desconhecido: '{agent_type}'")


async def save_uploaded_file(file):
    folder_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    file_location = os.path.join(folder_path, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    return {"task_id_files": folder_name, "filename": file.filename, "message": "File uploaded successfully"}


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


def save_task_log(task_id, task_data, agents_run, results):
    try:
        logs_folder = os.path.join("app", "task_logs")
        os.makedirs(logs_folder, exist_ok=True)
        log_file_path = os.path.join(logs_folder, f"task_{task_id}.log")

        def make_serializable(obj):
            try:
                json.dumps(obj)
                return obj
            except TypeError:
                return str(obj)

        log_content = {
            "task_id": task_id,
            "task_data": make_serializable(task_data),
            "agents_executed": agents_run,
            "results": results,
            "status": tasks[task_id]["status"]
        }

        with open(log_file_path, "w", encoding="utf-8") as log_file:
            json.dump(log_content, log_file, ensure_ascii=False, indent=2)

        print(f"✅ Log salvo: {log_file_path}")

    except Exception as e:
        print(f"❌ Erro ao salvar log da task {task_id}: {str(e)}")
