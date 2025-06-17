import uuid
import os
from dotenv import load_dotenv
from app.agents.plan_agent import generate_plan
from app.agents.code_agent import generate_code
from app.agents.write_agent import generate_text
from app.agents.report_agent import generate_report
from app.agents.image_agent import generate_image

load_dotenv()

tasks = {}
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def process_task(task_text, task_id_files=None):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing", "result": None}

    try:
        # Se um task_id_files foi passado, vamos ler os arquivos dessa task
        if task_id_files:
            folder_path = os.path.join("uploads", task_id_files)
            file_contents = []

            if os.path.exists(folder_path):
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    # Tenta abrir os arquivos como texto
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            file_contents.append(f.read())
                    except Exception as e:
                        file_contents.append(f"[Erro ao ler o arquivo {filename}: {e}]")

                # Concatena o conteúdo de todos os arquivos
                task_text = task_text + "\n\n" + "\n\n".join(file_contents)

        # Seleciona o agente correto
        if task_text.lower().startswith("codigo:"):
            result = generate_code(task_text.replace("codigo:", "").strip())
        elif task_text.lower().startswith("texto:"):
            result = generate_text(task_text.replace("texto:", "").strip())
        elif task_text.lower().startswith("relatorio:"):
            result = generate_report(task_text.replace("relatorio:", "").strip())
        elif task_text.lower().startswith("imagem:"):
            result = generate_image(task_text.replace("imagem:", "").strip())
        else:
            result = generate_plan(task_text)

        tasks[task_id]["status"] = "done"
        tasks[task_id]["result"] = result

    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["result"] = f"Erro: {str(e)}"

    return task_id
