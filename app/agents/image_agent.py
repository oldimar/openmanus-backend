from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_image(task_description: str) -> str:
    try:
        response = client.images.generate(
            model="dall-e-2",  # ✅ Corrigido
            prompt=task_description,
            size="1024x1024",
            quality="standard",
            n=1
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        return f"Erro ao gerar imagem: {str(e)}"
