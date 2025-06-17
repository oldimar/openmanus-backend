from app.agents.plan_agent import generate_plan
from app.agents.code_agent import generate_code
from app.agents.report_agent import generate_report
from app.agents.write_agent import generate_text
from app.agents.image_agent import generate_image

def orchestrate_task(task_text: str) -> str:
    result_log = []

    # Exemplo simples: Se o texto contém "planejar", executa uma sequência de agentes
    if "planejar" in task_text.lower():
        result_log.append("🔹 Detecção: Palavra-chave 'planejar' encontrada. Iniciando orquestração multi-agente...\n")

        # 1. Plan Agent
        plan_output = generate_plan(task_text)
        result_log.append("📝 Resultado do Plan Agent:\n" + plan_output + "\n")

        # 2. Code Agent (gerando código com base no resultado do plan)
        code_output = generate_code(plan_output)
        result_log.append("💻 Resultado do Code Agent:\n" + code_output + "\n")

        # 3. Report Agent
        report_output = generate_report(code_output)
        result_log.append("📊 Resultado do Report Agent:\n" + report_output + "\n")

        # 4. Write Agent
        final_text = generate_text(report_output)
        result_log.append("✍️ Resultado do Write Agent:\n" + final_text + "\n")

        return "\n".join(result_log)

    else:
        return "Nenhuma orquestração necessária para esta task. (Não contém palavra-chave 'planejar')"
