import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "dall-e-3")


def generate_image(description: str) -> str:
    """
    Gera uma imagem no estilo 'coloring book' (infantil P&B) com base em uma descrição.
    """
    escaped_description = json.dumps(description, ensure_ascii=False)
    prompt = f"""
Generate a black and white cartoon-style line drawing about the following description, suitable for children's coloring books. 
Use bold outlines, no color or shading, clean white background.

Description:
{escaped_description}
""".strip()

    try:
        response = client.images.generate(
            model=model,
            prompt=prompt,
            n=1,
            size="1024x1024",
            style="natural"
        )
        url = response.data[0].url
        print(f"[IMAGE_AGENT] ✅ Imagem gerada para descrição: {description} → {url}")
        return url
    except Exception as e:
        print(f"[IMAGE_AGENT] ❌ Erro ao gerar imagem para descrição '{description}': {e}")
        return ""


def generate_images_from_list(lista_descricoes: list) -> list:
    """
    Gera imagens para uma lista de atividades. Cada item da lista deve ter 'descricao'.
    Retorna uma lista de URLs na mesma ordem.
    """
    urls = []

    for atividade in lista_descricoes:
        descricao = atividade.get("descricao", "")
        if descricao:
            url = generate_image(descricao)
            urls.append(url)
        else:
            urls.append("")

    return urls
