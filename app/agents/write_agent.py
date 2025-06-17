from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def generate_text(task_description: str):
    prompt = f"""
    Você é um redator de conteúdo. Gere um texto, artigo, email ou post com base no pedido do usuário.

    Pedido:
    {task_description}
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um escritor criativo e direto ao ponto."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()
