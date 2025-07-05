import re
import json

def parse_task_output_into_structured_data(resultados, agentes, quantidade_esperada=5):
    atividades = []

    for resultado, agente in zip(resultados, agentes):
        # 🔍 Tenta detectar JSON estruturado
        json_match = re.search(r"\[\s*{.*?}\s*]", resultado, re.DOTALL)
        if json_match:
            try:
                json_data = json.loads(json_match.group())
                for idx, item in enumerate(json_data):
                    texto = ""
                    titulo = item.get("titulo", "").strip() or f"ATIVIDADE {idx+1}"
                    instrucao = item.get("instrucao", "").strip()
                    opcoes_raw = item.get("opcoes", [])

                    if not instrucao or not isinstance(opcoes_raw, list) or len(opcoes_raw) < 2:
                        continue  # ignora malformadas

                    texto += f"{titulo}\n{instrucao}"

                    atividade = {
                        "texto": texto.strip(),
                        "opcoes": [str(op).strip() for op in opcoes_raw],
                        "imagens_url": []
                    }
                    atividades.append(atividade)

                continue  # já processado
            except Exception as e:
                print(f"[parser] Erro ao interpretar JSON: {e}")

        # 🔁 Fallback: bloco por linha
        blocos = re.split(r"\n---+\n", resultado)
        for bloco in blocos:
            sub_blocos = re.split(r"\n?ATIVIDADE\s+\d+\n?", bloco, flags=re.IGNORECASE)
            for sub_bloco in sub_blocos:
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

                    markdown_imgs = re.findall(r"!\[.*?\]\((https?://.*?)\)", linha)
                    html_imgs = re.findall(r'<img\s+[^>]*src=["\'](https?://.*?)["\']', linha)
                    url_imgs = re.findall(r"^https?://.*\.(png|jpg|jpeg|gif|webp)$", linha, re.IGNORECASE)

                    for img in markdown_imgs + html_imgs + url_imgs:
                        atividade["imagens_url"].append(img)

                    try:
                        if re.match(r"^\(\s?\)", linha):
                            atividade["opcoes"].append(linha)
                        elif re.match(r"^\(\s?[A-Za-z0-9]+\)", linha):
                            atividade["opcoes"].append(linha)
                        elif re.match(r"^[A-Da-d]\)", linha):
                            atividade["opcoes"].append(linha)
                        elif re.match(r"^[0-9]+\.", linha):
                            atividade["opcoes"].append(linha)
                        elif re.match(r"^[-*•+]\s", linha):
                            atividade["opcoes"].append(linha)
                        else:
                            atividade["texto"] += linha + "\n"
                    except re.error as e:
                        print(f"[parser] Regex error: {linha} => {e}")
                        atividade["texto"] += linha + "\n"

                atividade["texto"] = atividade["texto"].strip()
                if not atividade["texto"].lower().startswith("atividade"):
                    atividade["texto"] = f"ATIVIDADE {len(atividades)+1}\n" + atividade["texto"]

                atividade["opcoes"] = [op.strip() for op in atividade["opcoes"]]
                atividade["imagens_url"] = list(set(atividade["imagens_url"]))

                if atividade["texto"] and atividade["opcoes"]:
                    atividades.append(atividade)

    # 🔒 Remove duplicadas e corta se passou
    unicos = []
    vistos = set()
    for a in atividades:
        chave = (a["texto"], tuple(a["opcoes"]))
        if chave not in vistos:
            unicos.append(a)
            vistos.add(chave)

    return unicos[:quantidade_esperada]
