def format_task_output_as_worksheet(task_id: str, all_results: list[dict], agents_run: list[str]) -> str:
    """
    Gera um texto formatado no estilo Manus AI, com trilhas, atividades e imagens (se houver).
    Espera que `all_results` seja uma lista de dicionários com:
    - texto: str
    - opcoes: list[str]
    - imagens_url: list[str]
    """
    trilha_index = 1
    atividade_index = 1
    output = []

    output.append("ATIVIDADES DIAGNÓSTICAS\n")
    output.append("Estas atividades ajudarão o professor a conhecer melhor como você lê, interpreta e compreende.\n")
    output.append(f"\nTask ID: {task_id}\n\n")

    atividades_por_trilha = [[] for _ in agents_run]
    i = 0
    for atividade in all_results:
        trilha_idx = i % len(agents_run)
        atividades_por_trilha[trilha_idx].append(atividade)
        i += 1

    for idx, agente in enumerate(agents_run):
        output.append(f"TRILHA {idx+1}\n" + "=" * 80 + "\n")

        for atividade in atividades_por_trilha[idx]:
            output.append(f"ATIVIDADE {atividade_index}\n")
            output.append("🔊 " + atividade.get("texto", "") + "\n")

            for opcao in atividade.get("opcoes", []):
                output.append(opcao)

            imagens = atividade.get("imagens_url", [])
            for imagem in imagens:
                output.append(f"🖼️ IMAGEM: {imagem}")

            output.append("\n" + "-" * 80 + "\n")
            atividade_index += 1

    return "\n".join(output).strip()
