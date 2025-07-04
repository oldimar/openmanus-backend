import random
from app.agents.image_agent import fetch_image_from_pixabay
from app.agents.text_agent import extract_activity_theme  # IA para extrair tema da atividade

def associate_images_to_activities(atividades: list[dict], max_com_imagem: int = 4, task_grade: str = "") -> list[dict]:
    """
    Escolhe até `max_com_imagem` atividades e associa UMA imagem temática a cada uma (se disponível).
    """
    if not atividades:
        return []

    total = len(atividades)
    escolhidas = random.sample(atividades, min(max_com_imagem, total))

    for atividade in atividades:
        atividade["imagens_url"] = []
        atividade.pop("imagem_url", None)

        if atividade in escolhidas:
            texto_base = atividade.get("texto", "")
            try:
                tema = extract_activity_theme(texto_base, task_grade=task_grade)
                urls = fetch_image_from_pixabay(tema, quantidade=1)  # busca só 1 imagem
                if urls and isinstance(urls, list) and urls[0].startswith("http"):
                    atividade["imagens_url"] = [urls[0]]  # adiciona só a primeira
                else:
                    print(f"[imagem] Nenhuma imagem válida encontrada para tema '{tema}'.")

            except Exception as e:
                atividade["imagens_url"] = []
                print(f"[imagem] Erro ao buscar imagem para atividade: {e}")

    return atividades
