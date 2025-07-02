import re
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Mapeamento para normalizar temas extraídos em categorias úteis
TEMA_NORMALIZADO = {
    "compreensão de texto": "leitura",
    "leitura e interpretação": "leitura",
    "interpretação": "leitura",
    "interpretação textual": "leitura",
    "texto": "leitura",
    "vocabulário": "vocabulário",
    "palavras": "vocabulário",
    "sinônimos": "vocabulário",
    "animais": "animais",
    "matemática": "matemática",
    "meio ambiente": "meio ambiente",
    "cidadania": "cidadania",
    "frutas": "alimentação",
    "alimentação": "alimentação",
    "educação": "educação"
}


def extract_activity_theme(texto_base: str) -> str | None:
    try:
        texto_limpo = texto_base.strip()

        texto_reduzido = re.sub(r"(Resultado do agente '.*?':|---+)", "", texto_limpo).strip()

        if not texto_reduzido or len(texto_reduzido.split()) < 5:
            print("[TEMA] Erro ao extrair tema: Texto insuficiente após limpeza.")
            return None

        prompt = f"""
        Abaixo está a descrição de uma atividade educacional. Extraia apenas um tema curto e representativo (máximo 3 palavras), como "meio ambiente", "vocabulário", "cidadania", etc.

        Texto:
        {texto_reduzido}

        Tema:
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um extrator de temas educacionais."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        tema = response.choices[0].message.content.strip().lower()

        # Normalização do tema
        tema_normalizado = TEMA_NORMALIZADO.get(tema, tema)

        if not tema_normalizado or tema_normalizado in ["tema", "atividade", "imagem", "null", "none"]:
            print(f"[TEMA] Tema extraído inválido: '{tema}'")
            return None

        print(f"[TEMA] Tema extraído com sucesso: '{tema_normalizado}'")
        return tema_normalizado

    except Exception as e:
        print(f"[TEMA] Erro ao extrair tema via IA: {str(e)}")
        return None
