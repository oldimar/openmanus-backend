import uuid
import os

tasks = {}

def process_task(task_text):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing", "result": None}

    try:
        uploads_dir = "uploads"
        file_list = os.listdir(uploads_dir)
        result_lines = []

        for filename in file_list:
            file_path = os.path.join(uploads_dir, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()
                result_lines.append(f"Conteúdo de {filename}:\n{file_content}\n")
            except Exception as e:
                result_lines.append(f"Erro ao ler o arquivo {filename}: {e}")

        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = "\n\n".join(result_lines)

    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["result"] = str(e)

    return task_id
