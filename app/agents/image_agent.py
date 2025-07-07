import os
import time
import re
import json
import unicodedata
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🎯 Prompt base para o estilo coloring book (cartoon preto e branco)
PROMPT_BASE = (
    "A cute black and white cartoon-style line drawing of {tema}, "
    "with bold outlines, no color, and no shading. "
    "Child-friendly and simple, perfect for coloring books. Clean white background."
)

def montar_prompt_imagem(tema: str) -> str:
    """
    Limpa o tema, remove acentos e insere no prompt base para DALL·E.
    """
    tema_normalizado = unicodedata.normalize("NFKD", tema)
    tema_ascii = tema_normalizado.encode("ascii", "ignore").decode("ascii")
    tema_limpo = re.sub(r"[^\w\s\-]", "", tema_ascii).strip()
    return PROMPT_BASE.replace("{tema}", tema_limpo)

def gerar_imagem_dalle(prompt_en: str, tentativas=0) -> str:
    try:
        print(f"[DALL·E] 🎨 Gerando imagem com prompt: {prompt_en}")
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt_en,
            n=1,
            size="1024x1024",
            quality="standard"
        )
        url = response.data[0].url
        print(f"[DALL·E] ✅ Imagem gerada: {url}")
        return url

    except Exception as e:
        if tentativas < 1:
            print(f"[DALL·E] ⚠️ Erro, tentando fallback... {e}")
            time.sleep(2)
            prompt_fallback = montar_prompt_imagem("a forest animal")
            return gerar_imagem_dalle(prompt_fallback, tentativas + 1)
        else:
            print(f"[DALL·E] ❌ Falha ao gerar imagem: {e}")
            return "https://cdn.pixabay.com/photo/2020/12/09/20/07/education-5816931_1280.jpg"

def generate_images_from_list(lista: list[dict]) -> list[str]:
    """
    Gera imagens com base nos temas passados como lista de dicionários.
    Exemplo de entrada:
    [{"tema": "onça-pintada"}, {"tema": "tatu-bola"}]

    Retorna lista com as URLs das imagens geradas.
    """
    imagens = []
    for idx, item in enumerate(lista):
        tema = item.get("tema", "").strip()
        if not tema:
            print(f"[IMAGE_AGENT] ⚠️ Tema ausente para item {idx+1}, pulando...")
            imagens.append(None)
            continue

        try:
            print(f"[IMAGE_AGENT] 📸 Gerando imagem {idx+1}/{len(lista)} para tema: '{tema}'")
            prompt = montar_prompt_imagem(tema)
            url = gerar_imagem_dalle(prompt)
            imagens.append(url)
        except Exception as e:
            print(f"[IMAGE_AGENT] ❌ Erro ao gerar imagem para item: {json.dumps(item, ensure_ascii=False)}")
            print(f"[IMAGE_AGENT] Detalhes do erro: {e}")
            imagens.append(None)
    return imagens
