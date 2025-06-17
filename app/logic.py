import uuid
import os
from PyPDF2 import PdfReader
from docx import Document

tasks = {}

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


def process_task(task_text: str):
    task_id = str(uuid.uuid4())
    result_text = ""

    uploads_dir = "uploads"

    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)

    for filename in os.listdir(uploads_dir):
        filepath = os.path.join(uploads_dir, filename)

        # Ignora pastas
        if os.path.isdir(filepath):
            continue

        file_content = read_file_content(filepath)
        result_text += f"\n---\nArquivo: {filename}\n\n{file_content}\n"

    tasks[task_id] = {
        "status": "completed",
        "result": result_text
    }

    return task_id
