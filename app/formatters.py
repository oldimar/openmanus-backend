def format_task_output_as_worksheet(task_id: str, all_results: list[dict], agents_run: list[str]) -> str:
    """
    Gera um texto formatado no estilo Manus AI, com trilhas, atividades e imagens (se houver).
    Espera que `all_results` seja uma lista de dicionários com:
    - titulo: str (opcional)
    - texto/instrucao: str
    - opcoes: list[str]
    - imagens_url: list[str] ou imagem_url: str
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
        output.append(f"TRILHA {idx + 1}\n" + "=" * 80 + "\n")

        for atividade in atividades_por_trilha[idx]:
            # 1. Título
            titulo = atividade.get("titulo") or f"ATIVIDADE {atividade_index}"
            output.append(titulo)
            atividade_index += 1

            # 2. Texto ou instrução
            texto = atividade.get("texto") or atividade.get("instrucao") or ""
            if texto:
                output.append("🔊 " + texto.strip())

            # 3. Imagem (URL única ou lista)
            imagem = atividade.get("imagem_url") or None
            imagens = atividade.get("imagens_url") or []
            if imagem and isinstance(imagem, str) and imagem.startswith("http"):
                output.append(f"🖼️ IMAGEM: {imagem}")
            elif imagens and isinstance(imagens, list) and imagens[0].startswith("http"):
                output.append(f"🖼️ IMAGEM: {imagens[0]}")

            # 4. Opções
            opcoes = atividade.get("opcoes", [])
            for opcao in opcoes:
                output.append(opcao)

            # 5. Separador
            output.append("\n" + "-" * 80 + "\n")

    return "\n".join(output).strip()
