# app/agents/image_agent.py

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_image(prompt_text):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt_text,
            size="1024x1024",
            quality="standard",
            n=1
        )

        # A API retorna uma URL temporária da imagem
        image_url = response.data[0].url
        return image_url

    except Exception as e:
        return f"Erro ao gerar imagem: {str(e)}"
