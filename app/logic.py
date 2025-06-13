import uuid, os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

tasks = {}

def process_task(task_text):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing", "result": None}

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # ou "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "Você é um assistente útil, direto e criativo."},
                {"role": "user", "content": task_text}
            ]
        )

        result = response.choices[0].message.content.strip()
        tasks[task_id]["status"] = "done"
        tasks[task_id]["result"] = result

    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["result"] = f"Erro: {str(e)}"

    return task_id
