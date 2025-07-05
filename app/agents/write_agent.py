from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def generate_text(task_description: str, quantidade_atividades: int = 5):
    prompt = f"""
Você é um professor do 2º ano do ensino fundamental. Gere {quantidade_atividades} atividades pedagógicas curtas e claras para crianças de aproximadamente 7 anos, com base no seguinte pedido do usuário:

"{task_description}"

Cada atividade deve conter:

- Um título simples (opcional)
- Uma instrução clara precedida de "🔊"
- 3 a 4 alternativas (A, B, C...) formatadas como: "( ) texto da opção"
- Conteúdo adequado à faixa etária
- Temas de leitura, vocabulário, lógica ou observação
- Não use imagens, apenas texto

Formato esperado (sem explicações, apenas texto direto):

ATIVIDADE 1  
🔊 INSTRUÇÃO DA ATIVIDADE  
( ) ALTERNATIVA A  
( ) ALTERNATIVA B  
( ) ALTERNATIVA C  
( ) ALTERNATIVA D  

[Repita até ATIVIDADE {quantidade_atividades}]

Comece agora. Gere apenas as {quantidade_atividades} atividades, sem comentários nem introduções.
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um gerador de atividades pedagógicas compatíveis com impressão."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )

    return response.choices[0].message.content.strip()
