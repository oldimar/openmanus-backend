import re

def parse_task_output_into_structured_data(all_results: list[str], agents_run: list[str]) -> list[dict]:
    """
    Converte a saída bruta dos agentes (all_results) em uma lista estruturada de atividades:
    [
        {
            "texto": "Pergunta da atividade",
            "opcoes": ["( ) A", "( ) B", "( ) C"],
            "imagem_url": None
        },
        ...
    ]
    """
    atividades = []

    for agent, raw in zip(agents_run, all_results):
        blocos = re.split(r"\n\s*ATIVIDADE\s+\d+\s*\n", raw, flags=re.IGNORECASE)
        blocos = [b.strip() for b in blocos if b.strip()]
        
        for bloco in blocos:
            # Extrai o enunciado (linha com 🔊 ou primeira linha do bloco)
            match_texto = re.search(r"🔊\s*(.+)", bloco)
            texto = match_texto.group(1).strip() if match_texto else bloco.split("\n")[0].strip()

            # Extrai as opções (linhas com "( )" ou "- ")
            opcoes = re.findall(r"(\( ?\)|- )\s*(.+)", bloco)
            lista_opcoes = [f"( ) {texto_opcao.strip()}" for _, texto_opcao in opcoes] if opcoes else []

            atividades.append({
                "texto": texto,
                "opcoes": lista_opcoes,
                "imagem_url": None  # será preenchida depois
            })

    return atividades
