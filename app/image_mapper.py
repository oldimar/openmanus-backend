import random
from app.agents.image_agent import fetch_image_from_pixabay
from app.agents.text_agent import extract_activity_theme  # IA que extrai o tema da atividade

def associate_images_to_activities(atividades: list[dict], max_com_imagem: int = 4) -> list[dict]:
    """
    Escolhe até `max_com_imagem` atividades e associa imagens temáticas a elas.
    Cada atividade selecionada poderá receber múltiplas imagens (caso o tema seja bem definido).
    """
    if not atividades:
        return []

    total = len(atividades)
    escolhidas = random.sample(atividades, min(max_com_imagem, total))

    for atividade in atividades:
        atividade["imagens_url"] = []  # nova estrutura
        atividade.pop("imagem_url", None)  # remove legado se existir

        if atividade in escolhidas:
            texto_base = atividade.get("texto", "")
            try:
                tema = extract_activity_theme(texto_base)
                urls = fetch_image_from_pixabay(tema, quantidade=2)  # ⚠️ agora busca múltiplas
                atividade["imagens_url"] = urls or []

            except Exception as e:
                atividade["imagens_url"] = []
                print(f"[imagem] Erro ao buscar imagem para atividade: {e}")

    return atividades
