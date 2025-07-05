from app.agents.plan_agent import generate_plan
from app.agents.image_agent import generate_image
from app.agents.write_agent import generate_text_from_activity
from app.parser import parse_task_output_into_structured_data


def gerar_atividades_diagnosticas(prompt: str, task_grade: str = "") -> list[dict]:
    # Passo 1: gerar o plano com base no prompt
    plano = generate_plan(prompt)
    if not isinstance(plano, list) or not plano:
        raise ValueError("❌ Plano de atividades retornou vazio ou inválido.")

    # Passo 2: gerar imagens, se necessário
    descricoes_para_imagem = [a["descricao"] for a in plano if a.get("com_imagem")]
    imagens = generate_image(descricoes_para_imagem) if descricoes_para_imagem else []
    if not isinstance(imagens, list):
        imagens = []

    # Passo 3: gerar as atividades com ou sem imagem
    atividades = []
    img_idx = 0
    for item in plano:
        descricao = item.get("descricao", "")
        com_imagem = item.get("com_imagem", False)
        imagem_url = imagens[img_idx] if com_imagem and img_idx < len(imagens) else None
        if com_imagem:
            img_idx += 1

        atividade_json = generate_text_from_activity(descricao, imagem_url)
        if isinstance(atividade_json, dict):
            atividade_parseada = parse_task_output_into_structured_data([atividade_json], ["write"])
            atividades.extend(atividade_parseada)

    return atividades
