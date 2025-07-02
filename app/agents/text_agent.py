import re
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_activity_theme(texto_base: str) -> str | None:
    try:
        texto_limpo = texto_base.strip()

        # 1. Remover marcadores e cabeçalhos irrelevantes
        texto_reduzido = re.sub(r"(Resultado do agente '.*?':|---+)", "", texto_limpo).strip()

        if not texto_reduzido or len(texto_reduzido.split()) < 5:
            print("[TEMA] Erro ao extrair tema: Texto insuficiente após limpeza.")
            return None

        # 2. Envia prompt curto para a IA extrair o tema principal
        prompt = f"""
Abaixo está a descrição de uma atividade educacional. Extraia apenas um tema curto e representativo (máximo 3 palavras), como "meio ambiente", "vocabulário", "emoções", etc.

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

        # 3. Validação do tema
        if not tema or tema in ["tema", "atividade", "imagem", "null", "none"]:
            print(f"[TEMA] Tema extraído inválido: '{tema}'")
            return None

        # 4. Normalização de termos específicos para temas mais amplos
        normalizacao = {
            "compreensão de texto": "leitura",
            "interpretação de texto": "leitura",
            "resolução de conflitos": "emoções",
            "habilidades sociais": "crianças",
            "consumo consciente": "meio ambiente",
            "educação financeira": "dinheiro",
            "ética e cidadania": "cidadania",
            "cuidado com o corpo": "higiene",
            "expressão corporal": "atividades físicas",
            "desenvolvimento emocional": "emoções"
        }

        tema_normalizado = normalizacao.get(tema, tema)

        if tema != tema_normalizado:
            print(f"[TEMA] Tema normalizado: '{tema}' → '{tema_normalizado}'")

        return tema_normalizado

    except Exception as e:
        print(f"[TEMA] Erro ao extrair tema via IA: {str(e)}")
        return None
