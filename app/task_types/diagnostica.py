import re
from app.agents.plan_agent import generate_activity_plan
from app.agents.image_agent import generate_images_from_list
from app.agents.write_agent import generate_text
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
    plano = generate_activity_plan(prompt_reforcado, task_grade)

    if not isinstance(plano, list) or len(plano) == 0:
        raise Exception("❌ Plano de atividades retornou vazio ou inválido.")

    plano = plano[:quantidade]

    # 🔍 Coleta imagens para atividades que solicitam
    descricoes_com_imagem = [a.get("descricao", "") for a in plano if a.get("com_imagem")]
    imagens = generate_images_from_list(descricoes_com_imagem) if descricoes_com_imagem else []
    imagem_map = dict(zip(descricoes_com_imagem, imagens))

    # 🧠 Gera as instruções completas via agente de escrita
    descricoes = [a.get("descricao", "") for a in plano]
    atividades_geradas = generate_text("\n".join(descricoes), quantidade_atividades=quantidade)

    atividades_final = []
    for idx, atividade in enumerate(atividades_geradas):
        atividade["titulo"] = f"ATIVIDADE {idx + 1}"

        # Associa imagem, se houver
        descricao_original = plano[idx].get("descricao", "")
        if plano[idx].get("com_imagem"):
            atividade["imagem_url"] = imagem_map.get(descricao_original)

        # Verificação preventiva
        if not (
            isinstance(atividade, dict)
            and atividade.get("titulo")
            and atividade.get("instrucao")
            and isinstance(atividade.get("opcoes", []), list)
            and len(atividade["opcoes"]) >= 2
        ):
            print(f"[VALIDAÇÃO PREVENTIVA] Atividade {idx + 1} ignorada (estrutura incompleta).")
            continue

        try:
            Atividade(**atividade)
            atividades_final.append(atividade)
        except Exception as e:
            print(f"[VALIDAÇÃO] Atividade {idx + 1} inválida:", e)

    return atividades_final
