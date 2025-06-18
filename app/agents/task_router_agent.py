import os
from openai import OpenAI

client = OpenAI()

def decide_agents(prompt: str, model: str = "gpt-4o-mini") -> list:
    system_prompt = """
Você é um orquestrador de tarefas de uma IA educacional.

Sua função é analisar o pedido do professor + o conteúdo de anexos (se houver) e decidir quais agentes abaixo devem ser usados, e em qual ordem:

- plan → Criar um planejamento de atividades.
- code → Gerar códigos, exercícios ou scripts educativos.
- write → Produzir textos de apoio, conteúdos, artigos.
- image → Gerar imagens educativas para usar nas atividades.
- report → Montar um relatório detalhado.

Regras:

- Se houver menção a "planejar", "plano", "sequência de atividades" → Inclua o agente **plan**.
- Se houver menção a "código", "script", "programação" → Inclua o agente **code**.
- Se houver pedido por imagens ou anexos com imagens → Inclua o agente **image**.
- Se for um pedido por texto longo, artigo ou explicação → Inclua **write**.
- Se o professor quiser uma análise final ou resumo → Inclua **report**.
- Você pode incluir vários agentes na ordem que fizer sentido.
- Responda APENAS com um array JSON simples, exemplo: ["plan", "image", "report"]

Agora analise o conteúdo abaixo:

{prompt}

Resposta final (somente JSON array):
"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )

        raw_output = response.choices[0].message.content.strip()

        # Garante que a IA respondeu um JSON array válido
        agents = json.loads(raw_output)
        return agents

    except Exception as e:
        print(f"Erro no task_router_agent: {str(e)}")
        return ["plan"]  # Fallback padrão
