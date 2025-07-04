import os
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🔄 Mapeamento de temas extraídos para categorias normalizadas
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


def extract_activity_theme(texto_base: str, task_grade: str = "") -> str | None:
    try:
        texto_limpo = texto_base.strip()
        texto_reduzido = re.sub(r"(Resultado do agente '.*?':|---+)", "", texto_limpo).strip()

        if not texto_reduzido or len(texto_reduzido.split()) < 5:
            print("[TEMA] Erro ao extrair tema: Texto insuficiente após limpeza.")
            return None

        prompt_intro = (
            "Você receberá a descrição de uma atividade escolar. "
            "Seu trabalho é identificar **apenas um** tema central e representativo que se relacione com o conteúdo da atividade. "
            "O tema deve ser curto (1 a 3 palavras) e estar relacionado ao assunto tratado (ex: 'golfinhos', 'recifes de coral', 'meio ambiente', 'leitura', 'matemática', etc.)."
            "\nNão use temas genéricos como 'atividade', 'tema', 'imagem', 'educação' nem devolva frases."
        )

        if task_grade and isinstance(task_grade, str):
            prompt_intro += f"\n\nA série escolar do aluno é: {task_grade.strip()}."

        prompt = f"""{prompt_intro}

Atividade:
{texto_reduzido}

Tema:"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um especialista em classificar temas de atividades educacionais de forma concisa e útil."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        tema = response.choices[0].message.content.strip().lower()
        tema = re.sub(r"[^a-zA-Z0-9à-úÀ-ÚçÇ\s-]", "", tema)  # remove caracteres não úteis

        # ⚠️ Fallback se tema for inválido
        if tema in ["", "tema", "atividade", "imagem", "null", "none"]:
            print(f"[TEMA] Tema inválido detectado: '{tema}'. Tentando extrair manualmente...")

            palavras_chave = [
                "golfinho", "tubarão", "polvo", "caranguejo", "estrela-do-mar", "baleia", "oceano",
                "recifes", "mamíferos marinhos", "vida marinha", "animais aquáticos", "regeneração",
                "peixes", "crustáceos", "biologia", "habitat", "água doce", "água salgada"
            ]

            texto_lower = texto_reduzido.lower()
            for palavra in palavras_chave:
                if palavra in texto_lower:
                    print(f"[TEMA] Fallback manual encontrou: '{palavra}'")
                    return palavra

            print("[TEMA] Fallback manual também não encontrou tema útil.")
            return None

        tema_normalizado = TEMA_NORMALIZADO.get(tema, tema)
        print(f"[TEMA] Tema extraído com sucesso: '{tema_normalizado}'")
        return tema_normalizado

    except Exception as e:
        print(f"[TEMA] Erro ao extrair tema via IA: {str(e)}")
        return None
