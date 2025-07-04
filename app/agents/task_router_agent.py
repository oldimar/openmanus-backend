import os
import json
from openai import OpenAI

client = OpenAI()

def decide_agents(prompt: str, model: str = "gpt-4o-mini") -> list:
    system_prompt = f"""
Você é um orquestrador de tarefas para um sistema de IA educacional.

Sua função é analisar a descrição da tarefa + o conteúdo de anexos (se houver) e decidir, de forma inteligente, quais agentes abaixo devem ser executados, e em qual ordem:

- plan → Criar um planejamento de aula ou de atividades.
- code → Gerar códigos, exercícios de programação ou scripts educativos.
- write → Produzir textos de apoio, atividades ou explicações.
- image → Gerar imagens educativas baseadas nos temas.
- report → Criar um relatório final de fechamento.

Regras:

- Se o pedido mencionar "atividade", "atividades", "atividade pedagógica", "vocabulário", "leitura", "2º ano", "diagnóstica" → use write, report e image.
- Se houver termos como "planejar", "plano", "sequência de atividades" → use plan.
- Se o usuário pedir exercícios de programação, scripts ou códigos → use code.
- Se houver pedido por imagens ou se o conteúdo anexado for um PDF com imagens → inclua image.
- Se o pedido for um texto longo, artigo ou conteúdo descritivo → inclua write.
- Se o professor pedir um resumo final ou uma análise → inclua report.

⚠️ Importante: Você pode incluir múltiplos agentes, em qualquer ordem lógica.

Formato de resposta esperado (JSON Array apenas, sem textos explicativos):

Exemplos válidos:
["plan"]
["write", "image", "report"]
["code", "report"]

Agora analise o conteúdo da tarefa + anexos:

{prompt}

Responda apenas com o JSON Array final.
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt or "Tarefa vazia."}
            ]
        )

        raw_output = response.choices[0].message.content.strip()

        # Valida se o retorno é um JSON Array
        agents = json.loads(raw_output)

        if not isinstance(agents, list):
            raise ValueError("Resposta da IA não é uma lista JSON válida.")

        return agents

    except Exception as e:
        print(f"Erro no task_router_agent: {str(e)}")
        return ["write", "report", "image"]  # fallback seguro
