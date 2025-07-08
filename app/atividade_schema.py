from typing import List, Optional
from pydantic import BaseModel, HttpUrl, validator

class Atividade(BaseModel):
    titulo: str
    instrucao: str
    opcoes: List[str]
    imagem_url: Optional[HttpUrl] = None  # string (link) ou None/ausente

    @validator("titulo", "instrucao")
    def nao_vazio(cls, valor):
        if not valor or not valor.strip():
            raise ValueError("Campo obrigatório não pode estar vazio.")
        return valor.strip()

    @validator("opcoes")
    def validar_opcoes(cls, lista):
        if not isinstance(lista, list) or len(lista) < 2:
            raise ValueError("A atividade deve conter pelo menos duas opções.")
        return [opcao.strip() for opcao in lista]

    @validator("imagem_url", pre=True, always=True)
    def imagem_url_vazia_para_none(cls, valor):
        # Garante que campo vazio/None seja realmente None, nunca string vazia
        if not valor:
            return None
        return valor
