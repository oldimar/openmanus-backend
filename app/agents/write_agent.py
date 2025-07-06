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
  }},
  ...
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
    Gera uma única atividade baseada em descrição e imagem (se houver).
    Retorna um dicionário com os campos da atividade.
    """
    prompt = f"""
Você é um gerador de atividades interativas para alunos de 6 a 9 anos.

Gere **uma única atividade** com base na seguinte descrição:
"{descricao}"
"""

    if imagem_url:
        prompt += f'\nA atividade deve considerar e fazer referência à seguinte imagem ilustrativa: {imagem_url}'

    prompt += """

A atividade gerada deve ser estruturada como JSON com os seguintes campos:

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

❗ Gere apenas o JSON bruto, sem explicações extras.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você gera atividades educativas para crianças e responde apenas em JSON."},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0.5
    )

    content = response.choices[0].message.content.strip()

    # ⚠️ Corrige blocos ```json
    if content.startswith("```json"):
        content = content.removeprefix("```json").removesuffix("```").strip()
    elif content.startswith("```"):
        content = content.removeprefix("```").removesuffix("```").strip()

    if not content:
        print("[WRITE_AGENT] ⚠️ Resposta vazia da IA.")
        return {
            "titulo": "ATIVIDADE GERADA",
            "instrucao": "🔊 A IA não retornou nenhuma atividade.",
            "opcoes": ["( ) Alternativa 1", "( ) Alternativa 2"],
            "imagem_url": imagem_url
        }

    try:
        atividade = json.loads(content)

        # 🔒 Corrige imagem_url inválida gerada pela IA
        if "imagem_url" in atividade and not str(atividade["imagem_url"]).startswith("http"):
            del atividade["imagem_url"]

        # ✅ Aplica imagem_url correta, se houver
        if imagem_url:
            atividade["imagem_url"] = imagem_url

        return atividade

    except Exception as e:
        print(f"[WRITE_AGENT] ❌ Erro ao interpretar JSON: {e}")
        print("[WRITE_AGENT] Conteúdo da IA:", content)
        return {
            "titulo": "ATIVIDADE MALFORMADA",
            "instrucao": "🔊 A IA gerou uma resposta, mas ela não pôde ser interpretada como JSON.",
            "opcoes": [content],
            "imagem_url": imagem_url
        }
