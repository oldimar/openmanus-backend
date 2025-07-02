import re

def parse_task_output_into_structured_data(all_results: list[str], agents_run: list[str]) -> list[dict]:
    """
    Converte a saída dos agentes em uma lista estruturada de atividades:
    [
        {
            "texto": "Pergunta ou instrução da atividade",
            "opcoes": ["( ) A", "( ) B", "( ) C"],
            "imagem_url": None
        },
        ...
    ]
    """
    atividades = []

    agentes_validos = {"plan", "write", "code", "report"}

    for agent, raw in zip(agents_run, all_results):
        if agent not in agentes_validos:
            continue

        # Remove separadores ou marcadores do tipo "Resultado do agente"
        blocos = re.split(r"\n\s*ATIVIDADE\s+\d+\s*\n", raw, flags=re.IGNORECASE)
        blocos = [b.strip() for b in blocos if b.strip()]

        for bloco in blocos:
            # ⚠️ Ignora linhas-resumo como "Resultado do agente 'xxx':"
            if re.match(r"^resultado do agente", bloco.strip().lower()):
                continue

            # Extrai texto principal da atividade
            match_texto = re.search(r"🔊\s*(.+)", bloco)
            texto = match_texto.group(1).strip() if match_texto else bloco.split("\n")[0].strip()

            if not texto or texto.lower() in ["atividade", "exercício", "null", "none"]:
                continue

            # Extrai opções (formato "( ) X" ou "- X")
            opcoes = re.findall(r"(\( ?\)|- )\s*(.+)", bloco)
            lista_opcoes = [f"( ) {texto_opcao.strip()}" for _, texto_opcao in opcoes] if opcoes else []

            atividades.append({
                "texto": texto,
                "opcoes": lista_opcoes,
                "imagem_url": None
            })

    return atividades
