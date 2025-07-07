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
            # 1. Título com enumeração forçada
            raw_titulo = atividade.get("titulo", "").strip()
            if raw_titulo.upper().startswith("ATIVIDADE"):
                titulo = raw_titulo  # já tem prefixo
            elif raw_titulo:
                titulo = f"ATIVIDADE {atividade_index} - {raw_titulo}"
            else:
                titulo = f"ATIVIDADE {atividade_index}"
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


def format_atividades_para_app(atividades: list[dict]) -> list[dict]:
    """
    Formata uma lista de atividades no padrão usado pelo front:
    - texto: inclui "ATIVIDADE X" e a instrução (com emoji 🔊)
    - opcoes: lista de alternativas
    - imagens_url: lista com 1 URL (se houver)
    """
    if not isinstance(atividades, list) or not atividades:
        return []

    resultado_formatado = []

    for idx, atividade in enumerate(atividades, start=1):
        titulo = f"ATIVIDADE {idx}"

        instrucao = (
            atividade.get("instrucao") or
            atividade.get("texto") or
            atividade.get("titulo") or ""
        ).strip()

        texto = f"{titulo}\n🔊 {instrucao}" if instrucao else titulo

        opcoes = atividade.get("opcoes") or []
        if not isinstance(opcoes, list):
            opcoes = [str(opcoes)]

        imagem_url = atividade.get("imagem_url") or ""
        imagens_url = [imagem_url] if imagem_url and imagem_url.startswith("http") else []

        resultado_formatado.append({
            "texto": texto,
            "opcoes": opcoes,
            "imagens_url": imagens_url
        })

    return resultado_formatado
