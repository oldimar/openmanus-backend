import uuid
import os
from dotenv import load_dotenv
from app.agents.plan_agent import generate_plan
from app.agents.code_agent import generate_code
from app.agents.write_agent import generate_text
from app.agents.report_agent import generate_report
from app.agents.image_agent import generate_image
from app.task_orchestrator import orchestrate_task
from PyPDF2 import PdfReader
from docx import Document

load_dotenv()

tasks = {}
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def get_uploads_for_task(task_id):
    upload_folder = os.path.join("uploads", task_id)
    if os.path.exists(upload_folder):
        return [os.path.join(upload_folder, f) for f in os.listdir(upload_folder)]
    return []


def read_file_content(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == ".txt":
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()

        elif ext == ".pdf":
            text = ""
            with open(filepath, "rb") as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
            return text

        elif ext == ".docx":
            text = ""
            doc = Document(filepath)
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text

        else:
            return f"[Arquivo não suportado: {os.path.basename(filepath)}]"

    except Exception as e:
        return f"[Erro ao ler {os.path.basename(filepath)}: {str(e)}]"


def process_task(task_text, task_id_files=None):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing", "result": None}

    try:
        # Se houver arquivos relacionados à task, leia os conteúdos
        extra_context = ""
        if task_id_files:
            upload_folder = os.path.join("uploads", task_id_files)
            if os.path.exists(upload_folder):
                file_texts = []
                for filename in os.listdir(upload_folder):
                    filepath = os.path.join(upload_folder, filename)
                    file_texts.append(f"--- Conteúdo de {filename} ---\n")
                    file_texts.append(read_file_content(filepath))
                extra_context = "\n\n".join(file_texts)

        # Junta o prompt do usuário + os conteúdos dos arquivos
        final_prompt = f"{task_text}\n\n{extra_context}" if extra_context else task_text

        # Verificar se a task envolve a palavra "planejar" para acionar o orquestrador
        if "planejar" in task_text.lower():
            result = orchestrate_task(final_prompt)

        # Se não for orquestração, vai para o agente individual
        elif task_text.lower().startswith("codigo:"):
            result = generate_code(final_prompt.replace("codigo:", "").strip())

        elif task_text.lower().startswith("texto:"):
            result = generate_text(final_prompt.replace("texto:", "").strip())

        elif task_text.lower().startswith("relatorio:"):
            result = generate_report(final_prompt.replace("relatorio:", "").strip())

        elif task_text.lower().startswith("imagem:"):
            result = generate_image(final_prompt.replace("imagem:", "").strip())

        else:
            result = generate_plan(final_prompt)

        tasks[task_id]["status"] = "done"
        tasks[task_id]["result"] = result

    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["result"] = f"Erro: {str(e)}"

    return task_id
