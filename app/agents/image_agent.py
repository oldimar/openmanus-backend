import os
import requests
import urllib.parse
from openai import OpenAI
from dotenv import load_dotenv

# 🟢 Carrega variáveis do .env
load_dotenv()

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ Log da API
if not PIXABAY_API_KEY:
    print("[ERRO] Chave da API do Pixabay não foi carregada!")
else:
    print("[INFO] Chave do Pixabay carregada com sucesso.")


def generate_image(task_description: str) -> str:
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=task_description,
            size="1024x1024",
            n=1
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        return f"Erro ao gerar imagem: {str(e)}"


def fetch_image_from_pixabay(search_term: str, quantidade: int = 2) -> list[str]:
    try:
        search_term = (search_term or "").strip().lower()
        termos_invalidos = {"", "tema", "atividade", "atividade 1", "imagem", "null", "none"}

        if search_term in termos_invalidos or len(search_term) < 3:
            raise ValueError(f"Termo inválido para Pixabay: '{search_term}'")

        search_term_encoded = urllib.parse.quote_plus(search_term)
        url = "https://pixabay.com/api/"
        params = {
            "key": PIXABAY_API_KEY,
            "q": search_term_encoded,
            "image_type": "photo",
            "safesearch": "true",
            "per_page": max(quantidade, 1),
            "lang": "pt"
        }

        log_url = f"{url}?key=***&q={search_term_encoded}"
        print(f"[PIXABAY] Buscando imagens para: '{search_term}'")
        print(f"[PIXABAY] Requisição: {log_url}")

        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Erro HTTP {response.status_code}")

        data = response.json()
        urls = []

        for hit in data.get("hits", []):
            img = hit.get("largeImageURL") or hit.get("webformatURL")
            if img and img.startswith(("http://", "https://")):
                urls.append(img)

        if urls:
            print(f"[PIXABAY] {len(urls)} imagem(ns) encontradas.")
            return urls[:quantidade]

        print("[PIXABAY] Nenhuma imagem válida encontrada.")
        return []

    except Exception as e:
        fallback = "https://cdn.pixabay.com/photo/2020/12/09/20/07/education-5816931_1280.jpg"
        print(f"[PIXABAY] Erro ao buscar imagem: {str(e)} — usando fallback.")
        return [fallback]
