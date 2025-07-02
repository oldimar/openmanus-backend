import re
from typing import List

def parse_task_output_into_structured_data(results: List[str], agents_run: List[str]) -> List[dict]:
    """
    Converte a saída bruta dos agentes (write, report, code) em uma estrutura com:
    - texto: str
    - opcoes: list[str]
    - imagens_url: list[str]
    """
    atividades = []

    for result in results:
        blocos = re.split(r"\n---+\n", result)

        for bloco in blocos:
            texto_principal = []
            opcoes = []
            imagens = []

            linhas = bloco.strip().splitlines()
            for linha in linhas:
                linha = linha.strip()

                # Ignora cabeçalhos repetitivos
                if re.match(r"^Resultado do agente '.*?':", linha):
                    continue

                # Detecta opções ( ) ou listas com - a) / b)
                if re.match(r"^\( ?[a-dA-D1-4]?[\)]|[-•*] ?[a-dA-D1-4]\)|\(\d+\))", linha):
                    opcoes.append(f"( ) {linha.strip('-•* ').strip()}")
                    continue

                # Detecta links de imagem
                if re.search(r"https?://.*\.(jpg|jpeg|png|gif)", linha):
                    urls = re.findall(r"https?://[^\s]+\.(?:jpg|jpeg|png|gif)", linha)
                    imagens.extend(urls)
                    continue

                texto_principal.append(linha)

            if texto_principal:
                atividades.append({
                    "texto": " ".join(texto_principal).strip(),
                    "opcoes": opcoes,
                    "imagens_url": imagens
                })

    return atividades
