"""Repository Pattern — camada de abstração do banco."""

from app.repositories.base import BaseRepository
from app.repositories.exam_repositories import ProvaRepository as ProvaRepositoryNew
from app.repositories.exam_repositories import (
    QuestaoRepository,
    prova_repo,
    questao_repo,
)
from app.repositories.folha_repository import FolhaRepository
from app.repositories.prova_repository import ProvaRepository


__all__ = [
    "BaseRepository",
    "ProvaRepository",  # old (static)
    "ProvaRepositoryNew",  # new (BaseRepository[T])
    "QuestaoRepository",
    "prova_repo",  # singleton
    "questao_repo",  # singleton
    "FolhaRepository",
]
