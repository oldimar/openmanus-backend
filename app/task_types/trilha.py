from app.agents.write_agent import generate_text_from_activity
from app.agents.image_agent import generate_image


def gerar_atividades_trilha(prompt: str, task_grade: str = "") -> list[dict]:
    """
    Gera um conjunto de atividades com imagem obrigatória, ideal para trilhas.
    Cada linha do prompt será usada como base para uma atividade.
    """
    linhas = [l.strip() for l in prompt.strip().split("\n") if l.strip()]
    if not linhas:
        raise ValueError("❌ Prompt da trilha está vazio.")

    imagens = generate_image(linhas)
    if not isinstance(imagens, list):
        imagens = []

    atividades = []

    for idx, linha in enumerate(linhas):
        imagem_url = imagens[idx] if idx < len(imagens) else None
        atividade_json = generate_text_from_activity(linha, imagem_url)

        # Garante que a estrutura esteja no padrão básico
        if isinstance(atividade_json, dict):
            atividades.append(atividade_json)

    return atividades
