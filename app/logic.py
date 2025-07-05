import uuid
import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv

from app.agents.plan_agent import generate_plan
from app.agents.code_agent import generate_code
from app.agents.write_agent import generate_text
from app.agents.report_agent import generate_report
from app.agents.image_agent import generate_image
from app.agents.task_router_agent import decide_agents

from app.ocr_reader import extract_text_from_pdf
from app.formatters import format_task_output_as_worksheet
from app.parser import parse_task_output_into_structured_data

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

        # ✅ NOVO FLUXO — TAREFA DO TIPO 'diagnostica'
        if task_type == "diagnostica":
            from task_types.diagnostica import gerar_atividades_diagnosticas
            atividades = gerar_atividades_diagnosticas(final_prompt, task_grade)
            formatted_result = format_task_output_as_worksheet(task_id, atividades, ["diagnostica"])
            tasks[task_id]["result"] = json.dumps(atividades, ensure_ascii=False, indent=2)
            tasks[task_id]["structured_result"] = atividades
            tasks[task_id]["status"] = "done"
            save_task_log(task_id=task_id, task_data=task_data, agents_run=["diagnostica"], results=tasks[task_id]["result"])
            return tasks[task_id]["result"], tasks[task_id]["structured_result"]

        # ✅ NOVO FLUXO — TAREFA DO TIPO 'trilha'
        elif task_type == "trilha":
            from task_types.trilha import gerar_atividades_trilha
            atividades = gerar_atividades_trilha(final_prompt, task_grade)
            formatted_result = format_task_output_as_worksheet(task_id, atividades, ["trilha"])
            tasks[task_id]["result"] = json.dumps(atividades, ensure_ascii=False, indent=2)
            tasks[task_id]["structured_result"] = atividades
            tasks[task_id]["status"] = "done"
            save_task_log(task_id=task_id, task_data=task_data, agents_run=["trilha"], results=tasks[task_id]["result"])
            return tasks[task_id]["result"], tasks[task_id]["structured_result"]

        # 🔁 FLUXO ORIGINAL — plan → image → write
        plan_result = generate_plan(final_prompt)

        if not isinstance(plan_result, list):
            raise Exception("Resposta inválida do agente plan. Esperado: lista de atividades.")

        descricoes_com_imagem = [a["descricao"] for a in plan_result if a.get("com_imagem")]
        imagens_geradas = []

        if descricoes_com_imagem:
            imagens_geradas = generate_image(descricoes_com_imagem)
            if not isinstance(imagens_geradas, list):
                raise Exception("Resposta inválida do agente image. Esperado: lista de URLs.")

        atividades_estruturadas = []
        imagem_index = 0

        for atividade in plan_result:
            descricao = atividade.get("descricao", "")
            com_imagem = atividade.get("com_imagem", False)
            imagem_url = imagens_geradas[imagem_index] if com_imagem and imagem_index < len(imagens_geradas) else None

            if com_imagem:
                imagem_index += 1

            atividade_gerada = generate_text(descricao, imagem_url=imagem_url)
            atividades_estruturadas.append(atividade_gerada)

        full_result = json.dumps(atividades_estruturadas, ensure_ascii=False, indent=2)

        atividades_final = parse_task_output_into_structured_data(atividades_estruturadas, agentes=["write"])
        resultado_formatado = format_task_output_as_worksheet(task_id, atividades_final, agents_run=["plan", "image", "write"])

        tasks[task_id]["result"] = full_result
        tasks[task_id]["structured_result"] = atividades_final
        tasks[task_id]["status"] = "done"

        save_task_log(
            task_id=task_id,
            task_data=task_data,
            agents_run=["plan", "image", "write"],
            results=full_result
        )

    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["result"] = f"Erro ao processar a task: {str(e)}"
        save_task_log(task_id, task_data, [], tasks[task_id]["result"])

    return tasks[task_id]["result"], tasks[task_id]["structured_result"]


def run_agent_by_type(agent_type, prompt_text, quantidade_atividades=5):
    if agent_type == "plan":
        return generate_plan(prompt_text)
    elif agent_type == "code":
        return generate_code(prompt_text)
    elif agent_type == "write":
        return generate_text(prompt_text, quantidade_atividades)
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
