import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def generate_plan(prompt_text: str, task_grade: str = "", quantidade: int = 5) -> list:
    """
    Gera um plano de atividades com descrições, temas e indicação se requerem imagem.
    Retorna uma lista com exatamente 'quantidade' atividades.
    """
    prompt = f"""
Você é um planejador de atividades pedagógicas para alunos de 6 a 9 anos do ensino fundamental.

Com base no pedido do professor abaixo, gere exatamente {quantidade} atividades, cada uma no seguinte formato JSON:

{{
  "descricao": "[breve descrição da atividade]",
  "tema": "[tema principal da atividade]",
  "com_imagem": true | false
}}

Requisitos:
- A saída deve ser uma **lista JSON válida** com {quantidade} objetos como o exemplo acima.
- Nenhuma explicação ou texto fora do JSON. Gere apenas o JSON bruto.
- Evite repetir temas ou descrições.
- Varie os tipos de atividades (leitura, associação, completar, observar, etc).
- Use temas compatíveis com alunos do ensino fundamental (animais, objetos, rimas, escola...).

Pedido do professor:
{prompt_text.strip()}
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

        # Limpeza de blocos markdown
        if content.startswith("```json"):
            content = content.removeprefix("```json").removesuffix("```").strip()
        elif content.startswith("```"):
            content = content.removeprefix("```").removesuffix("```").strip()

        atividades = json.loads(content)
        if isinstance(atividades, list):
            return atividades
        else:
            print("[PLAN_AGENT] ⚠️ JSON recebido não é uma lista.")
            return []

    except Exception as e:
        print(f"[PLAN_AGENT] ❌ Erro ao gerar plano de atividades: {e}")
        return []
