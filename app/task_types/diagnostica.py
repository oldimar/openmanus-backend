import re
from app.agents.plan_agent import generate_activity_plan
from app.agents.image_agent import fetch_image_from_pixabay
from app.agents.write_agent import generate_text_from_activity
from app.atividade_schema import Atividade


def extrair_numero_atividades(descricao: str, default: int = 5) -> int:
    match = re.search(r"\b(\d+)\s+(atividades|questões|perguntas|exercícios)", descricao.lower())
    if match:
        return int(match.group(1))
    return default


def gerar_atividades_diagnosticas(task_prompt: str, task_grade: str = "2º ano") -> list:
    quantidade = extrair_numero_atividades(task_prompt)

    # ✍️ Força a IA a planejar exatamente 'quantidade' atividades
    prompt_reforcado = f"{task_prompt.strip()}\n\nQuantidade esperada de atividades: {quantidade}"

    plan = generate_activity_plan(prompt_reforcado, task_grade)

    if not isinstance(plan, list) or len(plan) == 0:
        raise Exception("❌ Plano de atividades retornou vazio ou inválido.")

    # 🔍 Gera imagens via Pixabay para atividades com imagem
    descricoes_com_imagem = [a["descricao"] for a in plan if a.get("com_imagem")]
    imagens_geradas = []

    for desc in descricoes_com_imagem:
        urls = fetch_image_from_pixabay(desc, quantidade=1)
        imagens_geradas.append(urls[0] if urls else None)

    atividades = []
    imagem_index = 0

    for idx, atividade in enumerate(plan[:quantidade]):
        descricao = atividade.get("descricao", "")
        com_imagem = atividade.get("com_imagem", False)
        imagem_url = imagens_geradas[imagem_index] if com_imagem and imagem_index < len(imagens_geradas) else None

        if com_imagem:
            imagem_index += 1

        atividade_gerada = generate_text_from_activity(descricao, imagem_url)

        # ✅ Corrige título sequencial
        atividade_gerada["titulo"] = f"ATIVIDADE {idx + 1}"

        atividades.append(atividade_gerada)

    # 🧪 Validação final
    for idx, atividade in enumerate(atividades):
        try:
            Atividade(**atividade)
        except Exception as e:
            print(f"[VALIDAÇÃO] Atividade {idx + 1} inválida:", e)

    return atividades
