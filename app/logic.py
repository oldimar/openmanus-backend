import uuid, time, threading

tasks = {}

def process_task(task_text):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing", "result": None}
    def worker():
        time.sleep(5)
        tasks[task_id]["status"] = "done"
        tasks[task_id]["result"] = f"Resultado da tarefa: '{task_text}'"
    threading.Thread(target=worker, daemon=True).start()
    return task_id
