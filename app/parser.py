import re
import json

def parse_task_output_into_structured_data(resultados, agentes):
    atividades = []

    for resultado, agente in zip(resultados, agentes):
        # 🔍 Primeiro, tenta detectar e extrair JSON estruturado (com campos 'titulo', 'instrucao', 'opcoes')
        json_match = re.search(r"\[\s*{.*?}\s*]", resultado, re.DOTALL)
        if json_match:
            try:
                json_data = json.loads(json_match.group())
                for item in json_data:
                    texto = ""
                    if "titulo" in item:
                        texto += f"{item['titulo']}\n"
                    if "instrucao" in item:
                        texto += item["instrucao"]

                    atividade = {
                        "texto": texto.strip(),
                        "opcoes": item.get("opcoes", []),
                        "imagens_url": []
                    }
                    atividades.append(atividade)
                continue  # ✅ Já processado como JSON, pula para próximo resultado
            except Exception as e:
                print(f"[parser] Erro ao tentar interpretar JSON estruturado: {e}")

        # 🔁 Fallback: parsing linha a linha (mantém seu código original exatamente)
        blocos = re.split(r"\n---+\n", resultado)
        for bloco in blocos:
            sub_blocos = re.split(r"\n?ATIVIDADE\s+\d+\n?", bloco, flags=re.IGNORECASE)
            for sub_bloco in sub_blocos:
                linhas = sub_bloco.strip().split("\n")
                if not linhas or all(not linha.strip() for linha in linhas):
                    continue

                atividade = {
                    "texto": "",
                    "opcoes": [],
                    "imagens_url": []
                }

                for linha in linhas:
                    linha = linha.strip()
                    if not linha:
                        continue

                    # Ignora cabeçalho de agente
                    if re.match(r"^Resultado do agente '.*?':$", linha):
                        continue

                    # Imagens Markdown
                    markdown_imgs = re.findall(r"!\[.*?\]\((https?://.*?)\)", linha)
                    if markdown_imgs:
                        atividade["imagens_url"].extend(markdown_imgs)
                        continue

                    # Imagens HTML
                    html_imgs = re.findall(r'<img\s+[^>]*src=["\'](https?://.*?)["\']', linha)
                    if html_imgs:
                        atividade["imagens_url"].extend(html_imgs)
                        continue

                    # URL direta de imagem
                    if re.match(r"^https?://.*\.(png|jpg|jpeg|gif|webp)$", linha, re.IGNORECASE):
                        atividade["imagens_url"].append(linha)
                        continue

                    # Alternativas
                    try:
                        if re.match(r"^\(\s?\)", linha):                      # ( )
                            atividade["opcoes"].append(linha)
                        elif re.match(r"^\(\s?[A-Za-z0-9]+\)", linha):        # (A), (1)
                            atividade["opcoes"].append(linha)
                        elif re.match(r"^[A-Da-d]\)", linha):                 # A)
                            atividade["opcoes"].append(linha)
                        elif re.match(r"^[0-9]+\.", linha):                   # 1.
                            atividade["opcoes"].append(linha)
                        elif re.match(r"^[-*•+]\s", linha):                   # - texto
                            atividade["opcoes"].append(linha)
                        else:
                            atividade["texto"] += linha + "\n"
                    except re.error as e:
                        print(f"[parser] Erro de regex: {linha} => {e}")
                        atividade["texto"] += linha + "\n"

                # Limpeza
                atividade["texto"] = atividade["texto"].strip()
                atividade["opcoes"] = [op.strip() for op in atividade["opcoes"]]
                atividade["imagens_url"] = list(set(atividade["imagens_url"]))

                if atividade["texto"] or atividade["opcoes"] or atividade["imagens_url"]:
                    atividades.append(atividade)

    return atividades
