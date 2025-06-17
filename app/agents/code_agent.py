from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def generate_code(task_description: str):
    prompt = f"""
    Você é um assistente de programação. Gere o código-fonte abaixo com base no pedido do usuário.

    Requisitos:
    - Seja direto.
    - Responda somente com o código em um único bloco (sem comentários, sem explicações).
    - Mantenha a indentação correta.
    - Se o código for em HTML, JS, CSS ou Python, use boas práticas.
    - Se for necessário mais de uma linguagem (ex: HTML + JS), coloque todos os blocos.

    Pedido:
    {task_description}
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um gerador de código eficiente e objetivo."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()
