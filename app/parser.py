import re

def parse_task_output_into_structured_data(resultados, agentes):
    atividades = []

    for resultado, agente in zip(resultados, agentes):
        # Quebra por delimitador entre agentes (---)
        blocos = re.split(r"\n---+\n", resultado)

        for bloco in blocos:
            if not bloco.strip():
                continue

            # Divide blocos que contenham várias atividades em uma só (ex: ATIVIDADE 1, ATIVIDADE 2)
            sub_blocos = re.split(r"(?:^|\n)(ATIVIDADE\s+\d+|TRILHA\s+\d+)", bloco, flags=re.IGNORECASE)

            # Recompõe os pares (título + conteúdo)
            if len(sub_blocos) > 1:
                iterador = iter(sub_blocos)
                temp_bloco = []
                for item in iterador:
                    if re.match(r"(ATIVIDADE\s+\d+|TRILHA\s+\d+)", item, re.IGNORECASE):
                        titulo = item.strip()
                        conteudo = next(iterador, "")
                        temp_bloco.append((titulo, conteudo))
            else:
                temp_bloco = [(None, bloco)]

            for titulo, conteudo in temp_bloco:
                atividade = {"texto": "", "opcoes": [], "imagens_url": []}

                linhas = conteudo.strip().split("\n")

                if titulo:
                    atividade["texto"] = titulo

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
                        if re.match(r"^\(\s?[A-Za-z0-9]+\)", linha):  # (A), (1), etc
                            atividade["opcoes"].append(linha)
                        elif re.match(r"^[-*•+]\s", linha):  # listas markdown
                            atividade["opcoes"].append(linha)
                        elif re.match(r"^[A-Da-d]\)", linha):  # A), B)...
                            atividade["opcoes"].append(linha)
                        elif re.match(r"^[0-9]+\.", linha):  # 1. 2. ...
                            atividade["opcoes"].append(linha)
                        else:
                            atividade["texto"] += ("\n" if atividade["texto"] else "") + linha
                    except re.error as e:
                        print(f"[parser] Erro ao processar linha com regex: {linha} | Erro: {str(e)}")
                        atividade["texto"] += "\n" + linha

                if atividade["texto"] or atividade["opcoes"] or atividade["imagens_url"]:
                    atividades.append(atividade)

    return atividades
