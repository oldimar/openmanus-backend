from app.agents.plan_agent import generate_activity_plan
from app.agents.image_agent import generate_image
from app.agents.write_agent import generate_text_from_activity
from app.atividade_schema import Atividade

def gerar_atividades_diagnosticas(task_prompt: str, task_grade: str = "2º ano") -> list:
    plan = generate_activity_plan(task_prompt, task_grade)

    if not isinstance(plan, list) or len(plan) == 0:
        raise Exception("❌ Plano de atividades retornou vazio ou inválido.")

    descricoes_com_imagem = [a["descricao"] for a in plan if a.get("com_imagem")]
    imagens_geradas = generate_image(descricoes_com_imagem) if descricoes_com_imagem else []

    atividades = []
    imagem_index = 0

    for atividade in plan:
        descricao = atividade.get("descricao", "")
        com_imagem = atividade.get("com_imagem", False)
        imagem_url = imagens_geradas[imagem_index] if com_imagem and imagem_index < len(imagens_geradas) else None

        if com_imagem:
            imagem_index += 1

        atividade_gerada = generate_text_from_activity(descricao, imagem_url)
        atividades.append(atividade_gerada)

    # (opcional) validação usando schema
    for idx, atividade in enumerate(atividades):
        try:
            Atividade(**atividade)
        except Exception as e:
            print(f"[VALIDAÇÃO] Atividade {idx + 1} inválida:", e)

    return atividades
