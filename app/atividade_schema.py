from typing import List, Optional
from pydantic import BaseModel, HttpUrl, validator

class Atividade(BaseModel):
    titulo: str
    instrucao: str
    opcoes: List[str]
    imagem_url: Optional[HttpUrl] = None

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
