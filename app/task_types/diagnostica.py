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

def gerar_atividades_diagnosticas(task_prompt: str, task_grade: str = "2º ano") -> list[dict]:
    quantidade = extrair_numero_atividades(task_prompt)
    prompt_reforcado = f"{task_prompt.strip()}\n\nQuantidade esperada de atividades: {quantidade}"
    plano = generate_activity_plan(prompt_reforcado, task_grade)

    if not isinstance(plano, list) or len(plano) == 0:
        raise Exception("❌ Plano de atividades retornou vazio ou inválido.")

    atividades = []
    for idx, atividade in enumerate(plano[:quantidade]):
        descricao = atividade.get("descricao", "")
        com_imagem = atividade.get("com_imagem", False)
        imagem_url = None

        if com_imagem:
            imagens = generate_images_from_list([descricao])
            imagem_url = imagens[0] if imagens else None

        # 🧠 Gera atividade com imagem
        atividade_gerada = generate_text_from_activity(descricao, imagem_url, idx)

        # 🔒 Garantia de padronização e robustez:
        atividade_padrao = {
            "titulo": atividade_gerada.get("titulo", f"ATIVIDADE {idx + 1}"),
            "instrucao": atividade_gerada.get("instrucao", "🔊 Responda a atividade."),
            "opcoes": atividade_gerada.get("opcoes", ["( ) Alternativa 1", "( ) Alternativa 2"]),
            "imagem_url": imagem_url if imagem_url else None
        }

        # ✅ Validação final pelo Pydantic:
        try:
            Atividade(**atividade_padrao)
            atividades.append(atividade_padrao)
        except Exception as e:
            print(f"[VALIDAÇÃO] Atividade {idx + 1} inválida: {e}")
            # Insere placeholder caso não valide
            atividades.append({
                "titulo": f"ATIVIDADE {idx + 1}",
                "instrucao": "🔊 Erro ao gerar atividade. Favor revisar.",
                "opcoes": ["( ) Alternativa 1", "( ) Alternativa 2"],
                "imagem_url": None
            })

    # 🔒 Garantia: sempre retorna exatamente a quantidade pedida
    while len(atividades) < quantidade:
        atividades.append({
            "titulo": f"ATIVIDADE {len(atividades) + 1}",
            "instrucao": "🔊 Atividade não gerada corretamente.",
            "opcoes": ["( ) Alternativa 1", "( ) Alternativa 2"],
            "imagem_url": None
        })

    return atividades
