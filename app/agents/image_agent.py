import os
import requests
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


def traduzir_para_ingles(termo_pt: str) -> str:
    """
    Dicionário de traduções básicas PT → EN para termos que causam erro 400 na Pixabay.
    """
    mapa = {
        "animais aquáticos": "aquatic animals",
        "mamíferos marinhos": "marine mammals",
        "peixe": "fish",
        "peixes": "fish",
        "tartaruga": "turtle",
        "tartarugas marinhas": "sea turtles",
        "golfinho": "dolphin",
        "formação educacional": "education",
        "ecossistema aquático": "aquatic ecosystem",
        "relatório escolar": "school report",
        "educação": "education"
    }
    return mapa.get(termo_pt.lower(), termo_pt)


def fetch_image_from_pixabay(search_term: str, quantidade: int = 1) -> list[str]:
    try:
        search_term = (search_term or "").strip().lower()

        # Termos inválidos comuns
        termos_invalidos = {"", "tema", "atividade", "atividade 1", "imagem", "null", "none"}
        if search_term in termos_invalidos or len(search_term) < 3:
            raise ValueError(f"Termo inválido para Pixabay: '{search_term}'")

        # Termo traduzido (Pixabay requer termos em inglês, mesmo com lang=pt)
        translated_term = traduzir_para_ingles(search_term)
        if translated_term != search_term:
            print(f"[PIXABAY] Tradução aplicada: '{search_term}' → '{translated_term}'")
        else:
            print(f"[PIXABAY] Nenhuma tradução encontrada para '{search_term}', usando original.")

        fallback_term = "education"

        url = "https://pixabay.com/api/"
        params = {
            "key": PIXABAY_API_KEY,
            "q": translated_term,
            "image_type": "photo",
            "safesearch": "true",
            "per_page": quantidade,
            "lang": "pt"
        }

        print(f"[PIXABAY] Buscando imagem para: '{translated_term}'")

        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Erro HTTP {response.status_code}")

        data = response.json()

        if not data.get("hits"):
            print(f"[PIXABAY] Nenhum resultado para '{translated_term}'. Tentando fallback '{fallback_term}'...")
            return fetch_image_from_pixabay(fallback_term, quantidade)

        imagens = []
        for hit in data["hits"]:
            image_url = hit.get("largeImageURL") or hit.get("webformatURL")
            if image_url and image_url.startswith("http"):
                imagens.append(image_url)
                if len(imagens) >= quantidade:
                    break

        if imagens:
            print(f"[PIXABAY] {len(imagens)} imagem(ns) encontrada(s).")
            return imagens

        raise Exception("Nenhuma imagem válida retornada.")

    except Exception as e:
        print(f"[PIXABAY] Erro ao buscar imagem: {str(e)}")
        return ["https://cdn.pixabay.com/photo/2020/12/09/20/07/education-5816931_1280.jpg"]
