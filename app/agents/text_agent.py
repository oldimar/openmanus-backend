import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_activity_theme(texto: str) -> str:
    """
    Usa IA para extrair o tema principal da atividade.
    Sempre retorna algo útil e seguro (máximo 3 palavras).
    """
    prompt = f"""Resuma o tema principal desta atividade em até 3 palavras.
Não escreva frases ou explicações. Apenas o tema.

Atividade:
\"\"\"{texto}\"\"\"

Tema:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=10
        )

        tema = response.choices[0].message.content.strip().lower()

        # Valida tema
        termos_invalidos = {"", "tema", "null", "none", "-", "atividade"}
        if tema in termos_invalidos or len(tema) < 3:
            raise ValueError(f"Tema inválido gerado: '{tema}'")

        return tema

    except Exception as e:
        print(f"[IA] Erro ao extrair tema da atividade: {e}")
        return "educação básica"
