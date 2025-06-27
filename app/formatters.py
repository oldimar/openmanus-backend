def format_task_output_as_worksheet(task_id: str, all_results: list[dict], agents_run: list[str]) -> str:
    """
    Gera um texto formatado no estilo Manus AI, com trilhas, atividades, e imagens (se houver).
    Espera que `all_results` seja uma lista de dicionários com:
    - texto: str
    - opcoes: list[str]
    - imagem_url: str | None
    """
    trilha_index = 1
    atividade_index = 1
    output = []

    output.append("ATIVIDADES DIAGNÓSTICAS - 2º ANO\n")
    output.append("ESTAS ATIVIDADES AJUDARÃO O PROFESSOR A CONHECER MELHOR COMO VOCÊ LÊ. FAÇA COM ATENÇÃO!\n")
    output.append(f"\nTask ID: {task_id}\n\n")

    # Cabeçalhos fixos ou rotativos (simplificados por ordem de agentes)
    trilha_nomes = {
        "plan": "RECONHECER A ESTRUTURA DE FRASES",
        "write": "TER REPERTÓRIO DE VOCABULÁRIO",
        "report": "LER COM RITMO, ENTONAÇÃO E SEM GRANDES PAUSAS",
        "code": "ORALIZAR TEXTOS ESCRITOS QUE TENHAM DE MEMÓRIA",
        "image": "CAPACIDADE DE ATENÇÃO E CONCENTRAÇÃO"
    }

    # Divide blocos em trilhas com base nos agentes executados
    atividades_por_trilha = [[] for _ in agents_run]

    i = 0
    for atividade in all_results:
        trilha_idx = i % len(agents_run)
        atividades_por_trilha[trilha_idx].append(atividade)
        i += 1

    for idx, agente in enumerate(agents_run):
        nome_trilha = trilha_nomes.get(agente, f"TRILHA {idx+1}")
        output.append(f"TRILHA {idx+1}: {nome_trilha}\n" + "_" * 80 + "\n")

        for atividade in atividades_por_trilha[idx]:
            output.append(f"\nATIVIDADE {atividade_index}\n")
            output.append("🔊 " + atividade["texto"] + "\n")

            if atividade.get("imagem_url"):
                output.append(f"\n🖼️ IMAGEM: {atividade['imagem_url']}\n")

            for opcao in atividade.get("opcoes", []):
                output.append(opcao)

            output.append("\n" + "_" * 80 + "\n")
            atividade_index += 1

    return "\n".join(output).strip()
