from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


# FUNÇÃO ORIGINAL — MANTIDA
def generate_plan(task_description: str, task_grade: str = "2º ano do ensino fundamental"):
    prompt = f"""
Você é um planejador pedagógico com experiência em educação infantil e ensino fundamental.

Gere um plano de aula completo com base na descrição da tarefa abaixo. O plano deve ser adequado para uma turma do {task_grade}.

Inclua os seguintes tópicos no seu plano de aula:

1. **Objetivos de aprendizagem**
2. **Conteúdo/tema da aula**
3. **Metodologia** (atividades práticas, uso de jogos, leitura, etc.)
4. **Avaliação** (como verificar se os alunos aprenderam)
5. **Recursos didáticos** (materiais, mídias, etc.)
6. **Duração estimada da aula**

A descrição da tarefa está logo abaixo:

{task_description}

Gere o plano em formato de texto claro e estruturado.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um planejador educacional que cria planos de aula estruturados para professores."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )
    return response.choices[0].message.content.strip()


# ✅ FUNÇÃO CORRIGIDA — para lista de atividades com JSON válido e campo tema

def generate_activity_plan(task_description: str, task_grade: str = "2º ano do ensino fundamental"):
    prompt = f"""
Você é um planejador pedagógico com experiência em educação infantil e ensino fundamental.

Com base na tarefa a seguir, gere uma **lista de atividades** que possam ser desenvolvidas com os alunos. Para cada atividade, forneça:

- uma breve descrição (campo `descricao`)
- uma indicação se a atividade deve ter imagem (campo `com_imagem: true` ou `false`)
- um termo curto e objetivo que represente o que deve ser desenhado caso a atividade tenha imagem (campo `tema`). Ex: "onça", "aluno brincando", "carta de memória". Caso não tenha imagem, use `null` ou "" como tema.

A lista deve ser retornada **no formato JSON**, como no exemplo:

[
  {
    "descricao": "atividade sobre o animal onça-pintada",
    "com_imagem": true,
    "tema": "onça-pintada"
  },
  {
    "descricao": "atividade de leitura de palavras",
    "com_imagem": false,
    "tema": ""
  }
]

Considere que a turma é do {task_grade}.

Tarefa base:
{task_description}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um especialista em planejamento de atividades escolares. Sempre responda com um JSON válido e coerente."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6
    )

    content = response.choices[0].message.content.strip()

    # ✅ Remove blocos de markdown (```json ... ```)
    if content.startswith("```json"):
        content = content.removeprefix("```json").strip()
    if content.startswith("```"):
        content = content.removeprefix("```").strip()
    if content.endswith("```"):
        content = content.removesuffix("```").strip()

    from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


# FUNÇÃO ORIGINAL — MANTIDA
def generate_plan(task_description: str, task_grade: str = "2º ano do ensino fundamental"):
    prompt = f"""
Você é um planejador pedagógico com experiência em educação infantil e ensino fundamental.

Gere um plano de aula completo com base na descrição da tarefa abaixo. O plano deve ser adequado para uma turma do {task_grade}.

Inclua os seguintes tópicos no seu plano de aula:

1. **Objetivos de aprendizagem**
2. **Conteúdo/tema da aula**
3. **Metodologia** (atividades práticas, uso de jogos, leitura, etc.)
4. **Avaliação** (como verificar se os alunos aprenderam)
5. **Recursos didáticos** (materiais, mídias, etc.)
6. **Duração estimada da aula**

A descrição da tarefa está logo abaixo:

{task_description}

Gere o plano em formato de texto claro e estruturado.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um planejador educacional que cria planos de aula estruturados para professores."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )
    return response.choices[0].message.content.strip()


# ✅ FUNÇÃO CORRIGIDA — para lista de atividades com JSON válido e campo tema

def generate_activity_plan(task_description: str, task_grade: str = "2º ano do ensino fundamental"):
    prompt = f"""
Você é um planejador pedagógico com experiência em educação infantil e ensino fundamental.

Com base na tarefa a seguir, gere uma **lista de atividades** que possam ser desenvolvidas com os alunos. Para cada atividade, forneça:

- uma breve descrição (campo `descricao`)
- uma indicação se a atividade deve ter imagem (campo `com_imagem: true` ou `false`)
- um termo curto e objetivo que represente o que deve ser desenhado caso a atividade tenha imagem (campo `tema`). Ex: "onça", "aluno brincando", "carta de memória". Caso não tenha imagem, use `null` ou "" como tema.

A lista deve ser retornada **no formato JSON**, como no exemplo:

[
  {
    "descricao": "atividade sobre o animal onça-pintada",
    "com_imagem": true,
    "tema": "onça-pintada"
  },
  {
    "descricao": "atividade de leitura de palavras",
    "com_imagem": false,
    "tema": ""
  }
]

Considere que a turma é do {task_grade}.

Tarefa base:
{task_description}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um especialista em planejamento de atividades escolares. Sempre responda com um JSON válido e coerente."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6
    )

    content = response.choices[0].message.content.strip()

    # ✅ Remove blocos de markdown (```json ... ```)
    if content.startswith("```json"):
        content = content.removeprefix("```json").strip()
    if content.startswith("```"):
        content = content.removeprefix("```").strip()
    if content.endswith("```"):
        content = content.removesuffix("```").strip()

    try:
        atividades = json.loads(content)

        # ✅ Garantir que todas tenham o campo 'tema'
        for a in atividades:
            if not a.get("com_imagem"):
                a["tema"] = ""
            elif "tema" not in a or not isinstance(a["tema"], str):
                a["tema"] = ""

        return atividades
    except Exception as e:
        print(f"[PLAN_AGENT] ❌ Erro ao interpretar JSON: {e}")
        print("[PLAN_AGENT] Conteúdo retornado pela IA:\n", content)
        return []
    except Exception as e:
        print(f"[PLAN_AGENT] ❌ Erro ao interpretar JSON: {e}")
        print("[PLAN_AGENT] Conteúdo retornado pela IA:\n", content)
        return []
