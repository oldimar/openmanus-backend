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

        # 👉 1. Ler conteúdo dos anexos (se houver)
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

        # 👉 2. Monta o prompt final
        final_prompt = f"{task_description}\n\n{extra_context}" if extra_context else task_description

        all_results = []
        agents_to_run = []

        # 👉 3. Se task_type vier, executa só o agente informado
        if task_type:
            result = run_agent_by_type(task_type, final_prompt)
            all_results.append(f"Resultado do agente '{task_type}':\n{result}\n\n---\n")
            agents_to_run = [task_type]
        else:
            # 👉 4. Se task_type estiver vazio, deixa a IA decidir
            agents_to_run = decide_agents(final_prompt)

            for agent in agents_to_run:
                try:
                    agent_result = run_agent_by_type(agent, final_prompt)
                    all_results.append(f"Resultado do agente '{agent}':\n{agent_result}\n\n---\n")
                except Exception as e:
                    all_results.append(f"[Erro ao rodar o agente {agent}: {str(e)}]")

        tasks[task_id]["result"] = "\n".join(all_results)
        tasks[task_id]["status"] = "done"

        # 👉 5. Salvar log detalhado
        save_task_log(
            task_id=task_id,
            task_data=task_data,
            agents_run=agents_to_run,
            results=tasks[task_id]["result"]
        )

    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["result"] = f"Erro interno ao processar a task: {str(e)}"

        # 👉 Também salva log mesmo no caso de erro
        save_task_log(
            task_id=task_id,
            task_data=task_data,
            agents_run=[],
            results=tasks[task_id]["result"]
        )


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


# 👉 Função de salvar log da task
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
