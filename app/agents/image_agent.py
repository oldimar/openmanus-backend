import os
import time
import random
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 💬 Função para traduzir e montar prompt para estilo cartoon preto e branco
def montar_prompt_imagem(descricao: str) -> str:
    # Remove instruções comuns e emojis para limpar o input
    descricao = re.sub(r"🔊|🎯|📚|Atividade \d+[:\-]*", "", descricao, flags=re.IGNORECASE).strip()

    # Prompt padrão em inglês (estilo coloring book)
    prompt_base = (
        "A cute black and white cartoon-style line drawing of {descricao}, "
        "with bold outlines, no color, and no shading. "
        "Child-friendly and simple, perfect for coloring books. Clean white background."
    )
    
    return prompt_base.format(descricao=descricao)


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
            return gerar_imagem_dalle("A simple cartoon-style black and white forest animal", tentativas + 1)
        else:
            print(f"[DALL·E] ❌ Falha ao gerar imagem: {e}")
            return "https://cdn.pixabay.com/photo/2020/12/09/20/07/education-5816931_1280.jpg"


# 🔁 Função principal chamada no logic.py
def generate_images_from_list(lista_descricoes: list[str]) -> list[str]:
    imagens = []
    for idx, descricao in enumerate(lista_descricoes):
        print(f"[IMAGE_AGENT] Buscando imagem {idx+1}/{len(lista_descricoes)}...")
        prompt = montar_prompt_imagem(descricao)
        url = gerar_imagem_dalle(prompt)
        imagens.append(url)
    return imagens
