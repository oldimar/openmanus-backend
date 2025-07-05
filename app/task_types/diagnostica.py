# app/task_types/diagnostica.py

from app.agents.plan_agent import generate_activity_plan
from app.agents.image_agent import generate_images_from_list
from app.agents.write_agent import generate_text_from_activity

def gerar_atividades_diagnosticas(task_description: str, task_grade: str = "2º ano do ensino fundamental"):
    """
    Executa o fluxo completo para gerar atividades diagnósticas:
    1. Gera o plano com descrições e flag com_imagem.
    2. Gera imagens apenas para atividades que precisam.
    3. Gera as atividades completas com ou sem imagem.
    4. Retorna lista de atividades estruturadas.
    """

    plano = generate_activity_plan(task_description, task_grade)

    if not isinstance(plano, list):
        raise Exception("Erro: plano retornado não está em formato de lista.")

    descricoes_com_imagem = [a["descricao"] for a in plano if a.get("com_imagem")]
    urls_imagens = generate_images_from_list(descricoes_com_imagem) if descricoes_com_imagem else []

    atividades_cruas = []
    imagem_idx = 0

    for atividade in plano:
        descricao = atividade.get("descricao", "")
        com_imagem = atividade.get("com_imagem", False)
        imagem_url = urls_imagens[imagem_idx] if com_imagem and imagem_idx < len(urls_imagens) else None

        if com_imagem:
            imagem_idx += 1

        atividade_gerada = generate_text_from_activity(descricao, imagem_url)
        atividades_cruas.append(atividade_gerada)

    return atividades_cruas
