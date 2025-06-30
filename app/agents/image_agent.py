from openai import OpenAI
import os
import requests
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")


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
        search_term = search_term.strip()
        if not search_term:
            raise ValueError("Termo de busca vazio ao consultar Pixabay.")

        url = "https://pixabay.com/api/"
        params = {
            "key": PIXABAY_API_KEY,
            "q": search_term,
            "image_type": "photo",
            "safesearch": "true",
            "per_page": 5,
            "lang": "pt"
        }

        response = requests.get(url, params=params)

        # 🔒 Verifica se a resposta é válida antes de usar .json()
        if response.status_code != 200:
            raise Exception(f"Erro HTTP {response.status_code} ao consultar Pixabay")

        if not response.text or response.text.strip() == "":
            raise Exception("Resposta vazia da API do Pixabay")

        data = response.json()
        if data.get("hits"):
            return data["hits"][0]["largeImageURL"]
        else:
            return "https://cdn.pixabay.com/photo/2017/01/31/17/44/question-mark-2026615_960_720.png"  # fallback

    except Exception as e:
        return f"Erro ao buscar imagem do Pixabay: {str(e)}"
