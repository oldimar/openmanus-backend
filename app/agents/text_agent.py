import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_activity_theme(texto_base: str) -> str:
    try:
        if not texto_base or len(texto_base.strip()) < 10:
            raise ValueError("Texto muito curto para extrair tema.")

        # Remove prefixos técnicos (evita pegar 'Resultado do agente...')
        linhas = texto_base.strip().split("\n")
        linhas = [l for l in linhas if "resultado do agente" not in l.lower()]
        texto_limpo = " ".join(linhas).strip()

        if len(texto_limpo) < 10:
            raise ValueError("Texto insuficiente após limpeza.")

        prompt = (
            f"Texto da atividade: \"{texto_limpo}\"\n\n"
            "Com base nesse texto, qual é o tema principal tratado? "
            "Responda apenas com uma ou duas palavras (ex: 'animais', 'cores', 'números')."
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        tema = response.choices[0].message.content.strip().lower()

        termos_invalidos = {"atividade", "tema", "imagem", "nenhum", "inexistente", "texto", "null", "none"}
        if tema in termos_invalidos or len(tema) < 3:
            raise ValueError(f"Tema considerado inválido: '{tema}'")

        print(f"[TEMA] Tema extraído: '{tema}'")
        return tema

    except Exception as e:
        print(f"[TEMA] Erro ao extrair tema: {str(e)}")
        return "educação"  # fallback neutro
