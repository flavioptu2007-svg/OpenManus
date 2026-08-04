"""Schemas Pydantic de entrada das tools — descrições claras e exemplos.

Cada tool aceita também ``response_format`` ("json" ou "markdown",
padrão "markdown") para controlar a serialização da resposta.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field


RESPONSE_FORMATS = Literal["json", "markdown"]


class _Base(BaseModel):
    response_format: RESPONSE_FORMATS = Field(
        "markdown",
        description="Formato da resposta: 'json' (estruturado) ou 'markdown' (legível).",
        examples=["markdown"],
    )


class CriarProvaInput(_Base):
    """Cria uma prova a partir de IDs de questões (ou das não atribuídas)."""

    nome: Optional[str] = Field(
        None, description="Nome da prova.", examples=["Prova de História — 8º Ano"]
    )
    question_ids: Optional[list[int]] = Field(
        None,
        description="IDs das questões que comporão a prova. Se omitido, usa as questões não atribuídas.",
        examples=[[1, 2, 3]],
    )


class ListarProvasInput(_Base):
    """Lista provas com paginação limit/offset."""

    limit: int = Field(
        20, ge=1, le=100, description="Quantidade máxima de itens.", examples=[20]
    )
    offset: int = Field(
        0, ge=0, description="Quantos registros pular do início.", examples=[0]
    )


class ConsultarProvaInput(_Base):
    """Detalhes de uma prova específica (com suas questões)."""

    prova_id: int = Field(..., description="ID da prova.", examples=[1])


class ConsultarQuestoesInput(_Base):
    """Busca no banco de questões com filtros e paginação."""

    materia: Optional[str] = Field(
        None, description="Filtra por matéria (ex.: História).", examples=["História"]
    )
    serie: Optional[str] = Field(
        None, description="Filtra por série (ex.: 8º Ano).", examples=["8º Ano"]
    )
    dificuldade: Optional[str] = Field(
        None,
        description="Filtra por dificuldade (Fácil, Médio, Difícil).",
        examples=["Médio"],
    )
    limit: int = Field(
        20, ge=1, le=100, description="Quantidade máxima de itens.", examples=[20]
    )
    offset: int = Field(
        0, ge=0, description="Quantos registros pular do início.", examples=[0]
    )


class CadastrarQuestaoInput(_Base):
    """Cadastra uma nova questão no banco."""

    texto: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Enunciado da questão.",
        examples=["Qual a função do Parlamento inglês?"],
    )
    habilidade: Optional[str] = Field(
        None,
        max_length=50,
        description="Código da habilidade curricular (ex.: EF08HI06).",
        examples=["EF08HI06"],
    )
    dificuldade: Optional[str] = Field(
        None, description="Dificuldade: Fácil, Médio ou Difícil.", examples=["Médio"]
    )
    materia: Optional[str] = Field(
        None,
        max_length=60,
        description="Matéria (ex.: História).",
        examples=["História"],
    )
    serie: Optional[str] = Field(
        None, max_length=30, description="Série (ex.: 8º Ano).", examples=["8º Ano"]
    )


class ProcessarGabaritoInput(_Base):
    """Processa a imagem de um gabarito e retorna a leitura estruturada.

    Informe ``image_path`` (caminho local) ou ``image_base64`` (conteúdo
    codificado em base64). Opcionalmente informe ``prova_id`` para persistir
    o resultado como FolhaResposta.
    """

    image_path: Optional[str] = Field(
        None,
        description="Caminho local da imagem (JPEG/PNG).",
        examples=["/tmp/gabarito.png"],
    )
    image_base64: Optional[str] = Field(
        None,
        description="Imagem em base64 (JPEG/PNG). Alternativa a image_path.",
        examples=["iVBORw0KGgo..."],
    )
    filename: Optional[str] = Field(
        None,
        description="Nome do arquivo (usado quando só image_base64 é informado).",
        examples=["gabarito.png"],
    )
    prova_id: Optional[int] = Field(
        None,
        description="Se informado, persiste o resultado como FolhaResposta da prova.",
        examples=[1],
    )


class ConsultarResultadosInput(_Base):
    """Lista resultados/notas já processados, com filtro por prova."""

    prova_id: Optional[int] = Field(None, description="Filtra por prova.", examples=[1])
    limit: int = Field(
        20, ge=1, le=100, description="Quantidade máxima de itens.", examples=[20]
    )
    offset: int = Field(
        0, ge=0, description="Quantos registros pular do início.", examples=[0]
    )
