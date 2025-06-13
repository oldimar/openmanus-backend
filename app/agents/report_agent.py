# app/agents/report_agent.py

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def generate_report(task_description: str):
    prompt = f"""
Você é um redator profissional especializado em relatórios. Com base no conteúdo abaixo, escreva um relatório claro, direto e bem formatado. O relatório pode conter subtítulos e tópicos, mas deve evitar floreios ou linguagem excessivamente informal.

Conteúdo:
{task_description}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um gerador de relatórios objetivos, profissionais e bem formatados."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()
