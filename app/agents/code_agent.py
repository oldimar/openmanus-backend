import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def generate_code(prompt_text: str) -> str:
    escaped_prompt = json.dumps(prompt_text, ensure_ascii=False)
    prompt = f"""
Gere um código Python com base no seguinte pedido:
{escaped_prompt}

Retorne apenas o código, sem explicações nem comentários fora do código.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um assistente que gera apenas código Python, sem explicações extras."},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content.strip()

    if content.startswith("```python"):
        content = content.removeprefix("```python").removesuffix("```").strip()
    elif content.startswith("```"):
        content = content.removeprefix("```").removesuffix("```").strip()

    return content
