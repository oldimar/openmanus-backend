from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def generate_plan(task_description):
    prompt = f"""
Você é um planejador de tarefas. Abaixo está uma tarefa geral enviada por um usuário.
Divida essa tarefa em 3 a 7 etapas lógicas, curtas e diretas. Responda como uma lista numerada.

Tarefa:
"{task_description}"

Etapas:
"""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um assistente especialista em dividir tarefas em etapas."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()
