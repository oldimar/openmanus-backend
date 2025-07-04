import re

def parse_task_output_into_structured_data(resultados, agentes):
    atividades = []

    for resultado in resultados:
        blocos = re.split(r"\n---+\n", resultado)

        for bloco in blocos:
            linhas = bloco.strip().split("\n")
            atividade = {"texto": "", "opcoes": [], "imagens_url": []}

            for linha in linhas:
                linha = linha.strip()
                if not linha:
                    continue

                # Detectar URLs de imagem
                if re.match(r"^https?://.*\\.(png|jpg|jpeg)$", linha, re.IGNORECASE):
                    atividade["imagens_url"].append(linha)
                    continue

                # Detectar alternativas
                try:
                    if re.match(r"^(\(\ )|[-*•])", linha):
                        atividade["opcoes"].append(linha)
                    elif re.match(r"^\([a-dA-D]\)|^\([0-9]+\)|^[a-dA-D]\)|^[0-9]+\.", linha):
                        atividade["opcoes"].append(linha)
                    else:
                        if atividade["texto"]:
                            atividade["texto"] += "\n" + linha
                        else:
                            atividade["texto"] = linha
                except re.error as e:
                    print(f"[parser] Erro ao processar linha com regex: {linha} | Erro: {str(e)}")
                    atividade["texto"] += "\n" + linha

            if atividade["texto"] or atividade["opcoes"] or atividade["imagens_url"]:
                atividades.append(atividade)

    return atividades
