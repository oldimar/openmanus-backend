import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def generate_report(prompt_text: str) -> str:
    escaped_prompt = json.dumps(prompt_text, ensure_ascii=False)
    prompt = f"""
Você é um gerador de relatórios. Com base na solicitação abaixo, crie um resumo claro e organizado:
{escaped_prompt}

O relatório deve conter no máximo 4 parágrafos curtos, sem listas, sem repetição do texto original.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você gera relatórios com linguagem clara e concisa."},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0.5
    )

    return response.choices[0].message.content.strip()
