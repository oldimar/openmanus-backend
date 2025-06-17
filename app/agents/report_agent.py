from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def generate_report(task_description: str):
    prompt = f"""
    Você é um assistente de escrita formal. Gere um relatório organizado e bem estruturado com base no pedido do usuário.

    Pedido:
    {task_description}
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é especialista em escrever relatórios profissionais e claros."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()
