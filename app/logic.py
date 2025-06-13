import uuid, os, sys
from dotenv import load_dotenv

# ✅ Garante que "agents" será encontrado mesmo no deploy
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.plan_agent import generate_plan
from agents.code_agent import generate_code
from agents.write_agent import generate_text
from agents.report_agent import generate_report

load_dotenv()

tasks = {}
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def process_task(task_text):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing", "result": None}

    try:
        if task_text.lower().startswith("codigo:"):
            prompt = task_text[7:].strip()
            result = generate_code(prompt)

        elif task_text.lower().startswith("texto:"):
            prompt = task_text[6:].strip()
            result = generate_text(prompt)

        elif task_text.lower().startswith("relatorio:"):
            prompt = task_text[10:].strip()
            result = generate_report(prompt)

        else:
            result = generate_plan(task_text)

        tasks[task_id]["status"] = "done"
        tasks[task_id]["result"] = result

    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["result"] = f"Erro: {str(e)}"

    return task_id
