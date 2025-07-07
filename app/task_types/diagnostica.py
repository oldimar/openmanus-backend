import re
from app.agents.plan_agent import generate_activity_plan
from app.agents.image_agent import generate_images_from_list
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

    atividades = []

    for idx, atividade in enumerate(plan[:quantidade]):
        descricao = atividade.get("descricao", "")
        com_imagem = atividade.get("com_imagem", False)

        # 🔍 Busca imagem imediatamente se necessário
        imagem_url = None
        if com_imagem:
            urls = generate_images_from_list([descricao])
            imagem_url = urls[0] if urls else None

        # ✅ Passa o índice corretamente para manter a enumeração
        atividade_gerada = generate_text_from_activity(descricao, imagem_url, atividade_index=idx)

        # ✅ Garante título com enumeração
        atividade_gerada["titulo"] = f"ATIVIDADE {idx + 1}"

        # 🚨 Verificação preventiva antes de validar com schema
        if not (
            isinstance(atividade_gerada, dict)
            and atividade_gerada.get("titulo")
            and atividade_gerada.get("instrucao")
            and isinstance(atividade_gerada.get("opcoes", []), list)
            and len(atividade_gerada["opcoes"]) >= 2
        ):
            print(f"[VALIDAÇÃO PREVENTIVA] Atividade {idx + 1} ignorada (estrutura incompleta).")
            continue

        try:
            # 🧪 Validação final com pydantic
            Atividade(**atividade_gerada)
            atividades.append(atividade_gerada)
        except Exception as e:
            print(f"[VALIDAÇÃO] Atividade {idx + 1} inválida:", e)

    return atividades
