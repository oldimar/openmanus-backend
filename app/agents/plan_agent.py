import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def generate_plan(prompt_text: str, task_grade: str = "") -> list:
    """
    Gera um plano de atividades com descrições, temas e indicação se requerem imagem.
    """
    escaped_prompt = json.dumps(prompt_text, ensure_ascii=False)
    prompt = f"""
Você é um planejador de atividades pedagógicas para alunos de 6 a 9 anos do ensino fundamental.

Com base no pedido do professor abaixo, gere uma lista de atividades, cada uma com os seguintes campos:
- "descricao": descrição curta e clara da atividade
- "tema": o tema principal abordado
- "com_imagem": true ou false, indicando se essa atividade deve conter imagem

Pedido do professor:
{escaped_prompt}

Formato de saída JSON esperado:
[
  {{
    "descricao": "atividade sobre o animal onça-pintada",
    "com_imagem": true,
    "tema": "onça-pintada"
  }},
  ...
]

❗ Gere apenas o JSON bruto, sem explicações adicionais.
""".strip()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Você é um planejador de atividades pedagógicas. Responda apenas em JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4
        )

        content = response.choices[0].message.content.strip()

        # Debug
        print("[PLAN_AGENT] Conteúdo retornado:", repr(content))

        if content.startswith("```json"):
            content = content.removeprefix("```json").removesuffix("```").strip()
        elif content.startswith("```"):
            content = content.removeprefix("```").removesuffix("```").strip()

        return json.loads(content)

    except Exception as e:
        print(f"[PLAN_AGENT] ❌ Erro ao gerar plano de atividades: {e}")
        return []
