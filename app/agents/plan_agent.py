from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

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
