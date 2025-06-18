import uuid, os, json
from dotenv import load_dotenv
from app.agents.plan_agent import generate_plan
from app.agents.code_agent import generate_code
from app.agents.write_agent import generate_text  # Corrigido aqui
from app.agents.report_agent import generate_report
from app.agents.image_agent import generate_image

load_dotenv()

tasks = {}
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
UPLOAD_FOLDER = "uploads"

def process_task(task_text):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing", "result": None}

    try:
        # Tenta converter o campo enviado em JSON
        task_data = json.loads(task_text) if isinstance(task_text, str) else task_text

        task_description = task_data.get("task_description", "")
        task_type = task_data.get("task_type", "")
        task_id_files = task_data.get("task_id_files", "")

        # 🧠 Orquestração multi-agente (Bloco 3 - Etapa 1)
        if "planejar" in task_description.lower():
            try:
                plan_result = generate_plan(task_description)
                code_result = generate_code(plan_result)
                report_result = generate_report(code_result)
                write_result = generate_text(report_result)
                tasks[task_id]["result"] = write_result
                tasks[task_id]["status"] = "done"
                return task_id
            except Exception as e:
                tasks[task_id]["status"] = "error"
                tasks[task_id]["result"] = f"Erro durante a orquestração multi-agente: {str(e)}"
                return task_id

        # Execução direta de um agente pelo campo task_type
        if task_type == "plan":
            result = generate_plan(task_description)

        elif task_type == "code":
            result = generate_code(task_description)

        elif task_type == "write":
            # Se task_id_files for informado, tenta ler os arquivos da pasta de upload
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
                    tasks[task_id]["status"] = "error"
                    tasks[task_id]["result"] = f"Erro: Pasta '{folder_path}' não encontrada."
                    return task_id
                except Exception as e:
                    tasks[task_id]["status"] = "error"
                    tasks[task_id]["result"] = f"Erro ao ler arquivos: {str(e)}"
                    return task_id
            else:
                result = generate_text(task_description)

        elif task_type == "report":
            result = generate_report(task_description)

        elif task_type == "image":
            result = generate_image(task_description)

        else:
            tasks[task_id]["status"] = "error"
            tasks[task_id]["result"] = f"Erro: task_type '{task_type}' não reconhecido."
            return task_id

        tasks[task_id]["result"] = result
        tasks[task_id]["status"] = "done"

    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["result"] = f"Erro interno ao processar a task: {str(e)}"

    return task_id
