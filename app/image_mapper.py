import random
from app.agents.image_agent import fetch_image_from_pixabay
from app.agents.text_agent import extract_activity_theme  # função auxiliar com IA

def associate_images_to_activities(atividades: list[dict], max_com_imagem: int = 4) -> list[dict]:
    """
    Escolhe até `max_com_imagem` atividades e associa imagens temáticas a elas.
    Se a imagem for um fallback (ex: question-mark ou education genérica), não atribui.
    """
    if not atividades:
        return []

    total = len(atividades)
    escolhidas = random.sample(atividades, min(max_com_imagem, total))

    for atividade in atividades:
        atividade["imagem_url"] = None  # padrão

        if atividade in escolhidas:
            texto_base = atividade.get("texto", "")
            try:
                tema = extract_activity_theme(texto_base)
                url = fetch_image_from_pixabay(tema)

                # ✅ Ignora imagem se for fallback
                if "question-mark" in url or "education-5816931" in url:
                    print(f"[imagem] Fallback detectado para tema '{tema}', ignorando imagem.")
                    atividade["imagem_url"] = None
                else:
                    atividade["imagem_url"] = url

            except Exception as e:
                atividade["imagem_url"] = None
                print(f"[imagem] Erro ao buscar imagem para atividade: {e}")

    return atividades
