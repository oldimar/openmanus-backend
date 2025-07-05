from app.agents.write_agent import generate_text_from_activity
from app.agents.image_agent import generate_image
from app.parser import parse_task_output_into_structured_data


def gerar_atividades_trilha(prompt: str, task_grade: str = "") -> list[dict]:
    """
    Gera um conjunto de atividades com imagem obrigatória, ideal para trilhas.
    """
    # Divide por linha para gerar uma atividade por linha
    linhas = [l.strip() for l in prompt.strip().split("\n") if l.strip()]
    if not linhas:
        raise ValueError("❌ Prompt da trilha está vazio.")

    # Gerar imagens para todas as linhas
    imagens = generate_image(linhas)
    if not isinstance(imagens, list):
        imagens = []

    atividades = []
    for idx, linha in enumerate(linhas):
        imagem_url = imagens[idx] if idx < len(imagens) else None
        atividade_json = generate_text_from_activity(linha, imagem_url)
        if isinstance(atividade_json, dict):
            atividades.extend(parse_task_output_into_structured_data([atividade_json], ["write"]))

    return atividades
