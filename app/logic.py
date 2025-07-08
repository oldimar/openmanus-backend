import uuid
import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv

from app.agents.plan_agent import generate_plan as generate_activity_plan
from app.agents.code_agent import generate_code
from app.agents.write_agent import generate_text, generate_text_from_activity
from app.agents.report_agent import generate_report
from app.agents.image_agent import generate_images_from_list
from app.agents.task_router_agent import decide_agents

from app.ocr_reader import extract_text_from_pdf
from app.formatters import format_task_output_as_worksheet
from app.parser import parse_task_output_into_structured_data
from app.formatters import format_atividades_para_app  # ✅ AJUSTADO
from app.atividade_schema import Atividade  # IMPORTAÇÃO PARA VALIDAÇÃO

load_dotenv()

tasks = {}
UPLOAD_FOLDER = "uploads"
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def extrair_numero_atividades(descricao: str, default: int = 5) -> int:
    match = re.search(r"\b(\d+)\s+(atividades|questões|perguntas|exercícios)", descricao.lower())
    if match:
        return int(match.group(1))
    return default


def validar_atividades_modelo_final(atividades: list) -> list:
    """
    Recebe uma lista de atividades, garante que todas estejam no modelo final.
    Substitui por placeholder qualquer atividade inválida.
    """
    atividades_corrigidas = []
    for idx, atv in enumerate(atividades, start=1):
        try:
            obj = Atividade(**atv)
            atividades_corrigidas.append(obj.dict())
        except Exception as e:
            print(f"[LOGIC] Atividade {idx} inválida ao validar modelo final: {e}")
            atividades_corrigidas.append({
                "titulo": f"ATIVIDADE {idx}",
                "instrucao": "🔊 Erro ao gerar atividade. Favor revisar.",
                "opcoes": ["( ) Alternativa 1", "( ) Alternativa 2"],
                "imagem_url": None
            })
    return atividades_corrigidas


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
            from app.task_types.diagnostica import gerar_atividades_diagnosticas
            atividades = gerar_atividades_diagnosticas(final_prompt, task_grade)
            atividades_validas = validar_atividades_modelo_final(atividades)
            atividades_formatadas = format_atividades_para_app(atividades_validas)
            tasks[task_id]["result"] = json.dumps(atividades_validas, ensure_ascii=False, indent=2)
            tasks[task_id]["structured_result"] = atividades_formatadas
            tasks[task_id]["status"] = "done"
            save_task_log(task_id=task_id, task_data=task_data, agents_run=["diagnostica"], results=tasks[task_id]["result"])
            return tasks[task_id]["result"], tasks[task_id]["structured_result"]

        # ✅ NOVO FLUXO — TAREFA DO TIPO 'trilha'
        elif task_type == "trilha":
            from app.task_types.trilha import gerar_atividades_trilha
            atividades = gerar_atividades_trilha(final_prompt, task_grade)
            atividades_validas = validar_atividades_modelo_final(atividades)
            tasks[task_id]["result"] = json.dumps(atividades_validas, ensure_ascii=False, indent=2)
            tasks[task_id]["structured_result"] = atividades_validas
            tasks[task_id]["status"] = "done"
            save_task_log(task_id=task_id, task_data=task_data, agents_run=["trilha"], results=tasks[task_id]["result"])
            return tasks[task_id]["result"], tasks[task_id]["structured_result"]

        # 🔁 FLUXO ORIGINAL — plan → image → write
        plan_result = generate_activity_plan(final_prompt, task_grade)

        if not isinstance(plan_result, list):
            raise Exception("Resposta inválida do agente plan. Esperado: lista de atividades.")

        lista_para_imagem = [
            {"tema": a.get("tema", ""), "descricao": a.get("descricao", "")}
            for a in plan_result if a.get("com_imagem") and a.get("tema")
        ]
        imagens_geradas = generate_images_from_list(lista_para_imagem) if lista_para_imagem else []

        atividades_estruturadas = []
        imagem_index = 0

        for i, atividade in enumerate(plan_result, start=1):
            descricao = atividade.get("descricao", "")
            com_imagem = atividade.get("com_imagem", False)
            imagem_url = imagens_geradas[imagem_index] if com_imagem and imagem_index < len(imagens_geradas) else None

            if com_imagem and imagem_url:
                imagem_index += 1

            atividade_gerada = generate_text_from_activity(descricao, imagem_url=imagem_url)
            atividades_estruturadas.append(atividade_gerada)

        atividades_validas = validar_atividades_modelo_final(atividades_estruturadas)
        full_result = json.dumps(atividades_validas, ensure_ascii=False, indent=2)
        atividades_final = parse_task_output_into_structured_data(atividades_validas, agentes=["write"])

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
        erro_msg = f"Erro ao processar a task: {str(e)}"
        tasks[task_id]["status"] = "error"
        tasks[task_id]["result"] = erro_msg
        save_task_log(task_id, task_data if 'task_data' in locals() else {}, [], erro_msg)

    return tasks[task_id]["result"], tasks[task_id]["structured_result"]


def run_agent_by_type(agent_type, prompt_text, quantidade_atividades=5):
    if agent_type == "plan":
        return generate_activity_plan(prompt_text)
    elif agent_type == "code":
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
