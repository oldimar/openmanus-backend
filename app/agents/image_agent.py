import os
import requests
import urllib.parse
from openai import OpenAI
from dotenv import load_dotenv

# 🟢 Carrega variáveis do .env (ambiente local)
load_dotenv()

# 🔑 APIs
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🔐 Cliente OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ Verificação da API
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


def fetch_image_from_pixabay(search_term: str) -> str:
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
            "per_page": 5,
            "lang": "pt"
        }

        # 🔍 Log mais claro
        print(f"[PIXABAY] Tema usado: '{search_term}' - URL: {url}?key=***&q={search_term_encoded}")

        response = requests.get(url, params=params)

        if response.status_code != 200:
            raise Exception(f"Erro HTTP {response.status_code} ao consultar Pixabay")

        data = response.json()
        if data.get("hits"):
            hit = data["hits"][0]
            return hit.get("largeImageURL") or hit.get("webformatURL")

        raise Exception("Nenhuma imagem encontrada na resposta")

    except Exception as e:
        print(f"[Pixabay] Erro ao buscar imagem: {str(e)}")
        return "https://cdn.pixabay.com/photo/2020/12/09/20/07/education-5816931_1280.jpg"
