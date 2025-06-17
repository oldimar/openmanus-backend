import uuid, os
from dotenv import load_dotenv
from app.agents.plan_agent import generate_plan
from app.agents.code_agent import generate_code
from app.agents.write_agent import generate_text
from app.agents.report_agent import generate_report
from app.agents.image_agent import generate_image

load_dotenv()

tasks = {}

model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def process_task(task_text):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing", "result": None}

    try:
        if task_text.lower().startswith("codigo:"):
            result = generate_code(task_text[7:].strip())
        elif task_text.lower().startswith("texto:"):
            result = generate_text(task_text[6:].strip())
        elif task_text.lower().startswith("relatorio:"):
            result = generate_report(task_text[10:].strip())
        elif task_text.lower().startswith("imagem:"):
            result = generate_image(task_text[7:].strip())
        else:
            result = generate_plan(task_text)

        tasks[task_id]["status"] = "done"
        tasks[task_id]["result"] = result

    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["result"] = f"Erro: {str(e)}"

    return task_id
