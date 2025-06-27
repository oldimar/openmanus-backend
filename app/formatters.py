def format_task_output_as_worksheet(task_id: str, all_results: list[str], agents_run: list[str]) -> str:
    trilha_index = 1
    atividade_index = 1
    output = []

    # Cabeçalho do documento
    output.append("ATIVIDADES DIAGNÓSTICAS - 2º ANO\n")
    output.append("ESTAS ATIVIDADES AJUDARÃO O PROFESSOR A CONHECER MELHOR COMO VOCÊ LÊ. FAÇA COM ATENÇÃO!\n")
    output.append(f"\nTask ID: {task_id}\n\n")

    headers = {
        "plan": "RECONHECER A ESTRUTURA DE FRASES",
        "write": "TER REPERTÓRIO DE VOCABULÁRIO",
        "report": "LER COM RITMO, ENTONAÇÃO E SEM GRANDES PAUSAS",
        "code": "ORALIZAR TEXTOS ESCRITOS QUE TENHAM DE MEMÓRIA",
        "image": "CAPACIDADE DE ATENÇÃO E CONCENTRAÇÃO"
    }

    for agent, raw in zip(agents_run, all_results):
        # Limpeza
        cleaned = raw.replace(f"Resultado do agente '{agent}':", "").replace("---", "").strip()

        # Título da trilha
        trilha_titulo = headers.get(agent, f"TRILHA {trilha_index}: RESULTADO DE {agent.upper()}")
        output.append(f"\nTRILHA {trilha_index}: {trilha_titulo}\n" + "_" * 80 + "\n")

        # Separar por atividades (usando 2 ou mais quebras de linha como delimitador)
        atividades = [a.strip() for a in cleaned.split("\n\n") if a.strip()]

        for atividade in atividades:
            output.append(f"\nATIVIDADE {atividade_index}\n")
            output.append("🔊 " + atividade + "\n")

            # Adiciona opções simuladas (4 opções padrão)
            output.append("\n(    ) OPÇÃO A\n(    ) OPÇÃO B\n(    ) OPÇÃO C\n(    ) OPÇÃO D\n")
            output.append("\n" + "_" * 80 + "\n")

            atividade_index += 1

        trilha_index += 1

    return "\n".join(output).strip()
