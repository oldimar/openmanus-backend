import random
from app.agents.image_agent import fetch_image_from_pixabay
from app.agents.text_agent import extract_activity_theme  # IA para extrair tema da atividade

def associate_images_to_activities(atividades: list[dict], max_com_imagem: int = 4, task_grade: str = "") -> list[dict]:
    """
    Escolhe até `max_com_imagem` atividades e associa imagens temáticas a elas.
    Agora suporta múltiplas imagens por atividade.
    """
    if not atividades:
        return []

    total = len(atividades)
    escolhidas = random.sample(atividades, min(max_com_imagem, total))

    for atividade in atividades:
        # Nova estrutura com suporte a múltiplas imagens
        atividade["imagens_url"] = []
        atividade.pop("imagem_url", None)  # remove campo antigo se existir

        if atividade in escolhidas:
            texto_base = atividade.get("texto", "")
            try:
                # Agora passando também o grau/série da turma
                tema = extract_activity_theme(texto_base, task_grade=task_grade)
                urls = fetch_image_from_pixabay(tema, quantidade=2)  # busca até 2 imagens
                if urls:
                    atividade["imagens_url"] = urls
                else:
                    print(f"[imagem] Nenhuma imagem válida encontrada para tema '{tema}'.")

            except Exception as e:
                atividade["imagens_url"] = []
                print(f"[imagem] Erro ao buscar imagem para atividade: {e}")

    return atividades
