import uuid, os
from dotenv import load_dotenv
import openai

# Carrega variáveis de ambiente, incluindo OPENAI_API_KEY
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

tasks = {}

def process_task(task_text):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing", "result": None}

    try:
        # Requisição real à API da OpenAI (GPT-4 ou GPT-3.5)
        response = openai.ChatCompletion.create(
            model="gpt-4",  # ou "gpt-3.5-turbo" se preferir reduzir custo
            messages=[
                {"role": "system", "content": "Você é um assistente útil, direto e criativo. Responda com o máximo de clareza possível."},
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
