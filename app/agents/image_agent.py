import os
import random
import requests
from openai import OpenAI
from dotenv import load_dotenv

# 🟢 Carrega variáveis do .env
load_dotenv()

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

if not PIXABAY_API_KEY:
    print("[ERRO] Chave da API do Pixabay não foi carregada!")
else:
    print("[INFO] Chave do Pixabay carregada com sucesso.")


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
    palavras_chave = [
        "floresta", "animal", "animais", "natureza", "educação", "desenho",
        "mamífero", "aves", "répteis", "savana", "bicho", "infantil"
    ]
    descricao = descricao.lower()
    encontrados = [p for p in palavras_chave if p in descricao]
    termo_final = " ".join(set(encontrados)) or "educacao"
    print(f"[PIXABAY] 🔍 Termo reduzido para busca: '{termo_final}'")
    return termo_final


# Cache temporário de imagens já usadas neste ciclo de execução
imagens_usadas: set[str] = set()

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
            "per_page": max(5, quantidade)
        }

        print(f"[PIXABAY] Buscando imagem para: '{translated_term}'")
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Erro HTTP {response.status_code}: {response.text}")

        data = response.json()
        candidatos = []

        for hit in data.get("hits", []):
            url = hit.get("webformatURL") or hit.get("largeImageURL")
            if url and url.startswith("http") and url not in imagens_usadas:
                candidatos.append(url)

        if not candidatos and tentativas == 0:
            print(f"[PIXABAY] ⚠️ Sem imagens únicas. Tentando fallback com 'education'...")
            return fetch_image_from_pixabay("education", quantidade, tentativas=1)

        imagens_escolhidas = []
        while candidatos and len(imagens_escolhidas) < quantidade:
            url = random.choice(candidatos)
            imagens_usadas.add(url)
            imagens_escolhidas.append(url)
            candidatos.remove(url)

        if imagens_escolhidas:
            print(f"[PIXABAY] ✅ {len(imagens_escolhidas)} imagem(ns) exclusiva(s) retornada(s).")
            return imagens_escolhidas

        raise Exception("Nenhuma imagem única válida encontrada.")

    except Exception as e:
        print(f"[PIXABAY] ❌ Erro ao buscar imagem: {str(e)}")
        return ["https://cdn.pixabay.com/photo/2020/12/09/20/07/education-5816931_1280.jpg"]
