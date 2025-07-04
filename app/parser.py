import re

def parse_task_output_into_structured_data(resultados, agentes):
    atividades = []

    for resultado, agente in zip(resultados, agentes):
        # Quebra por delimitador padrão dos agentes
        blocos = re.split(r"\n---+\n", resultado)

        for bloco in blocos:
            atividade = {"texto": "", "opcoes": [], "imagens_url": []}
            linhas = bloco.strip().split("\n")

            for linha in linhas:
                linha = linha.strip()
                if not linha:
                    continue

                # 🔍 Detecta imagem Markdown: ![desc](url)
                markdown_img = re.findall(r"!\[.*?\]\((https?://.*?)\)", linha)
                if markdown_img:
                    atividade["imagens_url"].extend(markdown_img)
                    continue

                # 🔍 Detecta imagem HTML: <img src="url">
                html_img = re.findall(r'<img\s+[^>]*src=["\'](https?://.*?)["\']', linha)
                if html_img:
                    atividade["imagens_url"].extend(html_img)
                    continue

                # 🔍 Detecta imagem por URL direta
                if re.match(r"^https?://.*\.(png|jpg|jpeg|gif|webp)$", linha, re.IGNORECASE):
                    atividade["imagens_url"].append(linha)
                    continue

                # ✅ Detecta alternativas de forma segura
                try:
                    if re.match(r"^\(\s?[A-Za-z0-9]+\)", linha):  # (A), (B), (1), etc
                        atividade["opcoes"].append(linha)
                    elif re.match(r"^[-*•+]\s", linha):  # listas markdown ou bullets
                        atividade["opcoes"].append(linha)
                    elif re.match(r"^[A-Da-d]\)", linha):  # A), B)...
                        atividade["opcoes"].append(linha)
                    elif re.match(r"^[0-9]+\.", linha):  # 1. 2. ...
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
