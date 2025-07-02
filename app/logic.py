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
from app.agents.task_router_agent import decide_agents

from app.ocr_reader import extract_text_from_pdf
from app.image_mapper import associate_images_to_activities
from app.formatters import format_task_output_as_worksheet
from app.parser import parse_task_output_into_structured_data  # 🆕

load_dotenv()

tasks = {}
UPLOAD_FOLDER = "uploads"
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


async def process_task(task_text, task_id):
    tasks[task_id] = {"status": "processing", "result": None, "structured_result": None}

    try:
        task_data = json.loads(task_text) if isinstance(task_text, str) else task_text
        task_description = task_data.get("task_description", "")
        task_type = task_data.get("task_type", "")
        task_id_files = task_data.get("task_id_files", "")

        # 👉 1. Ler conteúdo dos anexos (OCR de PDF + TXT puro)
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

        all_results = []
        agents_to_run = []

        # 👉 3. Rodar agentes
        if task_type:
            try:
                result = run_agent_by_type(task_type, final_prompt)
                all_results.append(f"Resultado do agente '{task_type}':\n{result}\n\n---\n")
                agents_to_run = [task_type]
            except Exception as e:
                all_results.append(f"[Erro ao rodar o agente '{task_type}': {str(e)}]")
        else:
            agents_to_run = decide_agents(final_prompt)
            for agent in agents_to_run:
                try:
                    agent_result = run_agent_by_type(agent, final_prompt)
                    all_results.append(f"Resultado do agente '{agent}':\n{agent_result}\n\n---\n")
                except Exception as e:
                    all_results.append(f"[Erro ao rodar o agente '{agent}': {str(e)}]")

        full_result = "\n".join(all_results)

        if full_result is None or full_result.strip() == "":
            tasks[task_id]["status"] = "error"
            tasks[task_id]["result"] = "Erro: Nenhum resultado foi gerado por nenhum agente."
            return tasks[task_id]["result"]

        # ✅ Filtra apenas agentes suportados pelo parser
        agentes_validos = {"write", "report", "code"}
        resultados_filtrados = []
        agentes_filtrados = []

        for a, r in zip(agents_to_run, all_results):
            if a in agentes_validos:
                agentes_filtrados.append(a)
                resultados_filtrados.append(r)

        # ✅ Agora sim, parse apenas com dados úteis
        atividades = parse_task_output_into_structured_data(resultados_filtrados, agentes_filtrados)

        # ✅ Adiciona imagens
        atividades_com_imagem = associate_images_to_activities(atividades)

        # ✅ Gera saída formatada (para DOCX e exibição)
        formatted_result = format_task_output_as_worksheet(task_id, atividades_com_imagem, agents_to_run)

        tasks[task_id]["result"] = full_result
        tasks[task_id]["structured_result"] = atividades_com_imagem
        tasks[task_id]["status"] = "done"

        save_task_log(
            task_id=task_id,
            task_data=task_data,
            agents_run=agents_to_run,
            results=tasks[task_id]["result"]
        )

    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["result"] = f"Erro ao processar a task: {str(e)}"
        save_task_log(task_id, task_data, [], tasks[task_id]["result"])

    return tasks[task_id]["result"], tasks[task_id]["structured_result"]  # ✅ devolve os dois


def run_agent_by_type(agent_type, prompt_text):
    if agent_type == "plan":
        return generate_plan(prompt_text)
    elif agent_type == "code":
        return generate_code(prompt_text)
    elif agent_type == "write":
        return generate_text(prompt_text)
    elif agent_type == "report":
        return generate_report(prompt_text)
    elif agent_type == "image":
        return generate_image(prompt_text)
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

        log_content = {
            "task_id": task_id,
            "task_data": task_data,
            "agents_executed": agents_run,
            "results": results,
            "status": tasks[task_id]["status"]
        }

        with open(log_file_path, "w", encoding="utf-8") as log_file:
            json.dump(log_content, log_file, ensure_ascii=False, indent=2)

        print(f"✅ Log salvo: {log_file_path}")

    except Exception as e:
        print(f"❌ Erro ao salvar log da task {task_id}: {str(e)}")
