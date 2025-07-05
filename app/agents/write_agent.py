import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def generate_text(task_description: str, quantidade_atividades: int = 5) -> str:
    """
    Função original — gera várias atividades com base em um prompt genérico.
    """
    prompt = f"""
Você é um gerador de atividades pedagógicas interativas para alunos do 2º ao 3º ano do ensino fundamental (6 a 9 anos).
Com base no pedido abaixo, gere exatamente {quantidade_atividades} atividades no formato JSON válido.

Requisito do usuário:
"{task_description}"

Cada atividade deve conter:
- Um campo "titulo" com texto como "ATIVIDADE 1", "ATIVIDADE 2" etc.
- Um campo "instrucao" iniciando com 🔊 (ex: "🔊 Leia o texto e escolha a resposta correta.")
- Um campo "opcoes" com uma lista de 3 ou 4 alternativas, cada uma no formato "( ) texto da opção"

Formato de saída JSON esperado:
[
  {{
    "titulo": "ATIVIDADE 1",
    "instrucao": "🔊 [texto da instrução]",
    "opcoes": [
      "( ) alternativa A",
      "( ) alternativa B",
      "( ) alternativa C",
      "( ) alternativa D"
    ]
  }}
]

❗ Gere apenas o JSON bruto, sem explicações, sem texto fora do JSON.
    """.strip()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um gerador de conteúdo educacional que responde somente em JSON estruturado."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )

    return response.choices[0].message.content.strip()


def generate_text_from_activity(descricao: str, imagem_url: str = None) -> dict:
    """
    Gera uma única atividade com base na descrição e, se houver, na imagem.
    Retorna um dicionário estruturado ou fallback.
    """
    prompt = f"""
Você é um gerador de atividades interativas para alunos de 6 a 9 anos.

Gere uma única atividade com base na seguinte descrição:
"{descricao}"
"""

    if imagem_url:
        prompt += f'\nA atividade deve fazer referência à imagem: {imagem_url}'

    prompt += """

Formato de saída:
{
  "titulo": "ATIVIDADE 1",
  "instrucao": "🔊 [instrução curta e clara]",
  "opcoes": [
    "( ) alternativa A",
    "( ) alternativa B",
    "( ) alternativa C",
    "( ) alternativa D"
  ]
}

❗ Gere apenas o JSON puro. Sem explicações ou comentários.
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Você gera atividades educativas para crianças e responde apenas em JSON."},
                {"role": "user", "content": prompt.strip()}
            ],
            temperature=0.5
        )

        content = response.choices[0].message.content.strip()
        print("[WRITE_AGENT] Conteúdo da IA:", content)

        if not content:
            print("[WRITE_AGENT] ⚠️ Resposta vazia.")
            return {
                "titulo": "ATIVIDADE VAZIA",
                "instrucao": "🔊 A IA não retornou nenhuma instrução.",
                "opcoes": ["( ) A", "( ) B"]
            }

        return json.loads(content)

    except Exception as e:
        print(f"[WRITE_AGENT] ❌ Erro ao interpretar JSON: {e}")
        return {
            "titulo": "ATIVIDADE MALFORMADA",
            "instrucao": "🔊 A IA gerou uma resposta que não pôde ser interpretada como JSON.",
            "opcoes": ["( ) alternativa malformada", "( ) conteúdo bruto"]
        }
