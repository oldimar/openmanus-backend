import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

# 🟢 Carrega variáveis do .env
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


def generate_images_from_list(descriptions: list[str]) -> list[str]:
    """
    Recebe uma lista de descrições e gera uma imagem para cada uma usando o Pixabay.
    Garante que nenhuma imagem se repita.
    """
    urls = []
    urls_utilizadas = set()

    for i, desc in enumerate(descriptions):
        print(f"[IMAGE_AGENT] Buscando imagem {i+1}/{len(descriptions)} para: '{desc[:60]}...'")

        try:
            imagens = fetch_image_from_pixabay(desc, quantidade=5)  # busca mais de uma

            imagem_escolhida = None
            for url in imagens:
                if url not in urls_utilizadas:
                    imagem_escolhida = url
                    urls_utilizadas.add(url)
                    break

            if not imagem_escolhida:
                print("[IMAGE_AGENT] ⚠️ Nenhuma imagem nova encontrada. Usando fallback.")
                imagem_escolhida = "https://cdn.pixabay.com/photo/2020/12/09/20/07/education-5816931_1280.jpg"

            urls.append(imagem_escolhida)

        except Exception as e:
            print(f"[IMAGE_AGENT] ❌ Erro ao gerar imagem para '{desc}': {e}")
            urls.append("https://cdn.pixabay.com/photo/2020/12/09/20/07/education-5816931_1280.jpg")

    return urls


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


def limpar_termo_para_pixabay(descricao: str) -> str:
    """
    Reduz uma descrição longa a termos curtos para busca mais eficaz na API do Pixabay.
    """
    palavras_chave = [
        "floresta", "animal", "animais", "natureza", "educação", "desenho",
        "mamífero", "aves", "répteis", "savana", "bicho", "infantil"
    ]
    descricao = descricao.lower()
    encontrados = [p for p in palavras_chave if p in descricao]
    termo_final = " ".join(set(encontrados)) or "educacao"
    print(f"[PIXABAY] 🔍 Termo reduzido para busca: '{termo_final}'")
    return termo_final


def fetch_image_from_pixabay(search_term: str, quantidade: int = 1, tentativas: int = 0) -> list[str]:
    try:
        original_term = (search_term or "").strip().lower()
        termos_invalidos = {"", "tema", "atividade", "atividade 1", "imagem", "null", "none"}
        if original_term in termos_invalidos or len(original_term) < 3:
            raise ValueError(f"Termo inválido para Pixabay: '{original_term}'")

        termo_limpo = limpar_termo_para_pixabay(original_term)
        translated_term = traduzir_para_ingles(termo_limpo)

        if translated_term != termo_limpo:
            print(f"[PIXABAY] Tradução aplicada: '{termo_limpo}' → '{translated_term}'")
        else:
            print(f"[PIXABAY] Nenhuma tradução encontrada. Usando termo: '{translated_term}'")

        if len(translated_term) > 100:
            translated_term = translated_term[:100]

        url = "https://pixabay.com/api/"
        params = {
            "key": PIXABAY_API_KEY,
            "q": translated_term,
            "lang": "pt",
            "image_type": "photo",
            "safesearch": "true",
            "per_page": max(quantidade * 2, 5)  # busca mais para evitar repetições
        }

        print(f"[PIXABAY] Buscando imagem para: '{translated_term}'")

        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Erro HTTP {response.status_code}: {response.text}")

        data = response.json()
        imagens = []

        for hit in data.get("hits", []):
            image_url = hit.get("webformatURL") or hit.get("largeImageURL")
            if image_url and image_url.startswith("http"):
                imagens.append(image_url)
                print(f"[PIXABAY] ➕ Imagem coletada: {image_url}")
                if len(imagens) >= quantidade:
                    break

        if imagens:
            print(f"[PIXABAY] ✅ {len(imagens)} imagem(ns) encontrada(s).")
            return imagens

        if tentativas == 0:
            print(f"[PIXABAY] ⚠️ Nenhuma imagem válida. Tentando fallback com 'education'...")
            return fetch_image_from_pixabay("education", quantidade, tentativas=1)

        raise Exception("Nenhuma imagem válida retornada.")

    except Exception as e:
        print(f"[PIXABAY] ❌ Erro ao buscar imagem: {str(e)}")
        return ["https://cdn.pixabay.com/photo/2020/12/09/20/07/education-5816931_1280.jpg"]
