import uuid, os, sys
from dotenv import load_dotenv

# ✅ Garante que "agents" será encontrado mesmo no deploy
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.plan_agent import generate_plan
from agents.code_agent import generate_code
from agents.write_agent import generate_text

load_dotenv()

tasks = {}
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def process_task(task_text):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing", "result": None}

    try:
        lower = task_text.lower().strip()

        # 🔹 Detecta prefixos e redireciona para o agente apropriado
        if lower.startswith("codigo:"):
            content = task_text[len("codigo:"):].strip()
            result = generate_code(content)

        elif lower.startswith("escreva:"):
            content = task_text[len("escreva:"):].strip()
            result = generate_text(content)

        else:
            result = generate_plan(task_text)

        tasks[task_id]["status"] = "done"
        tasks[task_id]["result"] = result

    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["result"] = f"Erro: {str(e)}"

    return task_id
