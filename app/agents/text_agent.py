import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


def extract_activity_theme(texto: str) -> str:
    """
    Usa IA para extrair o tema principal de uma atividade.
    Retorna um resumo de até 3 palavras, direto.
    """
    prompt = f"""Resuma o tema principal desta atividade em até 3 palavras.
Não escreva frases ou explicações. Apenas o tema.

Atividade:
\"\"\"{texto}\"\"\"

Tema:"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0.2
        )

        tema = response["choices"][0]["message"]["content"]
        return tema.strip().lower()

    except Exception as e:
        print(f"[IA] Erro ao extrair tema da atividade: {e}")
        return "tema"
