from app.agents.write_agent import generate_text_from_activity
from app.agents.image_agent import generate_image
from app.atividade_schema import Atividade

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
        atividade_json = generate_text_from_activity(linha, imagem_url, idx)

        # 🔒 Padronização
        atividade_padrao = {
            "titulo": atividade_json.get("titulo", f"ATIVIDADE {idx + 1}"),
            "instrucao": atividade_json.get("instrucao", "🔊 Responda a atividade."),
            "opcoes": atividade_json.get("opcoes", ["( ) Alternativa 1", "( ) Alternativa 2"]),
            "imagem_url": imagem_url if imagem_url else None
        }

        # ✅ Validação
        try:
            Atividade(**atividade_padrao)
            atividades.append(atividade_padrao)
        except Exception as e:
            print(f"[VALIDAÇÃO] Atividade {idx + 1} inválida: {e}")
            atividades.append({
                "titulo": f"ATIVIDADE {idx + 1}",
                "instrucao": "🔊 Erro ao gerar atividade. Favor revisar.",
                "opcoes": ["( ) Alternativa 1", "( ) Alternativa 2"],
                "imagem_url": None
            })

    return atividades
