import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

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


def fetch_image_from_pixabay(search_term: str, quantidade: int = 1, tentativas: int = 0) -> list[str]:
    try:
        original_term = (search_term or "").strip().lower()

        termos_invalidos = {"", "tema", "atividade", "atividade 1", "imagem", "null", "none"}
        if original_term in termos_invalidos or len(original_term) < 3:
            raise ValueError(f"Termo inválido para Pixabay: '{original_term}'")

        translated_term = traduzir_para_ingles(original_term)
        if translated_term != original_term:
            print(f"[PIXABAY] Tradução aplicada: '{original_term}' → '{translated_term}'")
        else:
            print(f"[PIXABAY] Nenhuma tradução encontrada para '{original_term}', usando original.")

        url = "https://pixabay.com/api/"
        params = {
            "key": PIXABAY_API_KEY,
            "q": translated_term,
            "image_type": "photo",
            "safesearch": "true",
            "per_page": quantidade
            # ⚠️ lang=pt removido — não afeta os resultados de busca
        }

        print(f"[PIXABAY] Buscando imagem para: '{translated_term}'")

        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Erro HTTP {response.status_code}: {response.text}")

        data = response.json()

        imagens = []
        for hit in data.get("hits", []):
            image_url = hit.get("largeImageURL") or hit.get("webformatURL")
            if image_url and image_url.startswith("http"):
                imagens.append(image_url)
                if len(imagens) >= quantidade:
                    break

        if imagens:
            print(f"[PIXABAY] {len(imagens)} imagem(ns) encontrada(s).")
            return imagens

        # ⛔ Não achou imagens: tenta fallback só uma vez
        if tentativas == 0:
            print(f"[PIXABAY] Nenhum resultado para '{translated_term}'. Tentando fallback com 'education'...")
            return fetch_image_from_pixabay("education", quantidade, tentativas=1)

        raise Exception("Nenhuma imagem válida retornada.")

    except Exception as e:
        print(f"[PIXABAY] Erro ao buscar imagem: {str(e)}")
        return ["https://cdn.pixabay.com/photo/2020/12/09/20/07/education-5816931_1280.jpg"]
