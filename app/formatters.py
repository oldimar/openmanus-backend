def format_task_output_as_worksheet(task_id: str, all_results: list[str], agents_run: list[str]) -> str:
    # Essa é uma versão simplificada, só organizando os blocos
    headers = {
        "plan": "PLANO DE AULA",
        "write": "TEXTO PRODUZIDO",
        "report": "RELATÓRIO FINAL",
        "code": "CÓDIGO GERADO",
        "image": "IMAGEM GERADA"
    }

    formatted_sections = []

    for agent, raw in zip(agents_run, all_results):
        titulo = headers.get(agent, f"RESULTADO - {agent.upper()}")
        cleaned = raw.replace(f"Resultado do agente '{agent}':", "").strip()
        cleaned = cleaned.replace("---", "").strip()

        section = f"### {titulo}\n\n{cleaned}"
        formatted_sections.append(section)

    final_output = f"ATIVIDADES DIAGNÓSTICAS - 2º ANO\n\nTask ID: {task_id}\n\n"
    final_output += "\n\n".join(formatted_sections)

    return final_output.strip()
