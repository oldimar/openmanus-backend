import re
import json

def parse_task_output_into_structured_data(resultados, agentes, quantidade_esperada=5):
    atividades = []

    for resultado, agente in zip(resultados, agentes):
        # 🧠 Caso já seja um dicionário ou lista de dicionários (via generate_text_from_activity)
        if isinstance(resultado, dict):
            resultado = [resultado]

        if isinstance(resultado, list):
            for idx, item in enumerate(resultado):
                titulo = item.get("titulo", "").strip() or f"ATIVIDADE {idx+1}"
                instrucao = item.get("instrucao", "").strip()
                opcoes_raw = item.get("opcoes", [])

                if not instrucao or not isinstance(opcoes_raw, list) or len(opcoes_raw) < 2:
                    continue

                # Só captura imagem_url (string ou None)
                imagem_url = item.get("imagem_url", None)
                if imagem_url and not (isinstance(imagem_url, str) and imagem_url.startswith("http")):
                    imagem_url = None

                atividade = {
                    "titulo": titulo,
                    "instrucao": instrucao,
                    "opcoes": [str(op).strip() for op in opcoes_raw],
                    "imagem_url": imagem_url
                }

                atividades.append(atividade)
            continue

        # 🔍 Tenta detectar JSON estruturado dentro de string
        if isinstance(resultado, str):
            json_match = re.search(r"\[\s*{.*?}\s*]", resultado, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group())
                    for idx, item in enumerate(json_data):
                        titulo = item.get("titulo", "").strip() or f"ATIVIDADE {idx+1}"
                        instrucao = item.get("instrucao", "").strip()
                        opcoes_raw = item.get("opcoes", [])

                        if not instrucao or not isinstance(opcoes_raw, list) or len(opcoes_raw) < 2:
                            continue

                        imagem_url = item.get("imagem_url", None)
                        if imagem_url and not (isinstance(imagem_url, str) and imagem_url.startswith("http")):
                            imagem_url = None

                        atividade = {
                            "titulo": titulo,
                            "instrucao": instrucao,
                            "opcoes": [str(op).strip() for op in opcoes_raw],
                            "imagem_url": imagem_url
                        }

                        atividades.append(atividade)
                    continue
                except Exception as e:
                    print(f"[parser] Erro ao interpretar JSON: {e}")

            # 🔁 Fallback: bloco por linha (modo texto solto)
            blocos = re.split(r"\n---+\n", resultado)
            for bloco in blocos:
                sub_blocos = re.split(r"\n?ATIVIDADE\s+\d+\n?", bloco, flags=re.IGNORECASE)
                for sub_bloco in sub_blocos:
                    linhas = sub_bloco.strip().split("\n")
                    if not linhas or all(not l.strip() for l in linhas):
                        continue

                    titulo = None
                    instrucao = None
                    opcoes = []
                    imagem_url = None

                    for linha in linhas:
                        linha = linha.strip()
                        if not linha:
                            continue

                        if re.match(r"^Resultado do agente '.*?':$", linha):
                            continue

                        # Captura imagem como string apenas
                        markdown_imgs = re.findall(r"!\[.*?\]\((https?://.*?)\)", linha)
                        html_imgs = re.findall(r'<img\s+[^>]*src=["\'](https?://.*?)["\']', linha)
                        url_imgs = re.findall(r"^https?://.*\.(png|jpg|jpeg|gif|webp)$", linha, re.IGNORECASE)

                        # Só usa a primeira URL válida, se houver
                        all_imgs = markdown_imgs + html_imgs + url_imgs
                        if all_imgs and not imagem_url:
                            imagem_url = all_imgs[0]

                        try:
                            if re.match(r"^\(\s?\)", linha):
                                opcoes.append(linha)
                            elif re.match(r"^\(\s?[A-Za-z0-9]+\)", linha):
                                opcoes.append(linha)
                            elif re.match(r"^[A-Da-d]\)", linha):
                                opcoes.append(linha)
                            elif re.match(r"^[0-9]+\.", linha):
                                opcoes.append(linha)
                            elif re.match(r"^[-*•+]\s", linha):
                                opcoes.append(linha)
                            elif not titulo:
                                titulo = linha if "atividade" in linha.lower() else None
                            elif not instrucao:
                                instrucao = linha
                        except re.error as e:
                            print(f"[parser] Regex error: {linha} => {e}")
                            if not instrucao:
                                instrucao = linha

                    # Fallbacks básicos
                    titulo = titulo or f"ATIVIDADE {len(atividades)+1}"
                    instrucao = instrucao or "🔊 Responda a atividade."

                    if titulo and instrucao and opcoes:
                        atividades.append({
                            "titulo": titulo,
                            "instrucao": instrucao,
                            "opcoes": [op.strip() for op in opcoes],
                            "imagem_url": imagem_url if imagem_url and isinstance(imagem_url, str) and imagem_url.startswith("http") else None
                        })

    # 🔒 Remove duplicadas e corta se exceder
    unicos = []
    vistos = set()
    for a in atividades:
        chave = (a["titulo"], a["instrucao"], tuple(a["opcoes"]))
        if chave not in vistos:
            unicos.append(a)
            vistos.add(chave)

    return unicos[:quantidade_esperada]
