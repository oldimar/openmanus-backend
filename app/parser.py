import re
import json

def parse_task_output_into_structured_data(resultados, agentes, quantidade_esperada=5):
    atividades = []

    for resultado, agente in zip(resultados, agentes):
        # 🔍 Tenta extrair JSON diretamente
        json_match = re.search(r"\[\s*{.*?}\s*]", resultado, re.DOTALL)
        if json_match:
            try:
                json_data = json.loads(json_match.group())
                if isinstance(json_data, list):
                    for idx, item in enumerate(json_data):
                        instrucao = item.get("instrucao", "").strip()
                        opcoes = item.get("opcoes", [])
                        if not instrucao or not isinstance(opcoes, list) or len(opcoes) < 2:
                            continue
                        titulo = item.get("titulo", "").strip() or f"ATIVIDADE {idx+1}"
                        texto = f"{titulo}\n{instrucao}"

                        atividades.append({
                            "texto": texto,
                            "opcoes": [op.strip() for op in opcoes],
                            "imagens_url": []
                        })

                    if len(atividades) == quantidade_esperada:
                        continue  # ✅ JSON válido e completo, pula o fallback
            except Exception as e:
                print(f"[parser] Erro ao interpretar JSON: {e}")

        # 🔁 Fallback: parsing linha a linha
        blocos = re.split(r"\n---+\n", resultado)
        for bloco in blocos:
            sub_blocos = re.split(r"\n?ATIVIDADE\s+\d+\n?", bloco, flags=re.IGNORECASE)
            for idx, sub_bloco in enumerate(sub_blocos):
                linhas = sub_bloco.strip().split("\n")
                if not linhas or all(not l.strip() for l in linhas):
                    continue

                atividade = {"texto": "", "opcoes": [], "imagens_url": []}

                for linha in linhas:
                    linha = linha.strip()
                    if not linha:
                        continue

                    if re.match(r"^Resultado do agente '.*?':$", linha):
                        continue

                    # Imagens
                    markdown_imgs = re.findall(r"!\[.*?\]\((https?://.*?)\)", linha)
                    html_imgs = re.findall(r'<img\s+[^>]*src=["\'](https?://.*?)["\']', linha)
                    url_imgs = re.findall(r"^https?://.*\.(png|jpg|jpeg|gif|webp)$", linha, re.IGNORECASE)

                    for img in markdown_imgs + html_imgs + url_imgs:
                        atividade["imagens_url"].append(img)

                    # Alternativas
                    elif re.match(r"^\(\s?\)", linha) or \
                         re.match(r"^\(\s?[A-Za-z0-9]+\)", linha) or \
                         re.match(r"^[A-Da-d]\)", linha) or \
                         re.match(r"^[0-9]+\.", linha) or \
                         re.match(r"^[-*•+]\s", linha):
                        atividade["opcoes"].append(linha)
                    else:
                        atividade["texto"] += linha + "\n"

                # Limpeza e título automático
                atividade["texto"] = atividade["texto"].strip()
                if not atividade["texto"].lower().startswith("atividade"):
                    atividade["texto"] = f"ATIVIDADE {len(atividades)+1}\n" + atividade["texto"]

                atividade["opcoes"] = [op.strip() for op in atividade["opcoes"]]
                atividade["imagens_url"] = list(set(atividade["imagens_url"]))

                if atividade["texto"] and atividade["opcoes"]:
                    atividades.append(atividade)

    return atividades[:quantidade_esperada]  # 🔒 Corta se passar do limite
