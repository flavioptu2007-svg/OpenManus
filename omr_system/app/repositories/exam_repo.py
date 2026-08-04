"""Alias para exam_repositories — compatibilidade com código do usuário."""

from app.repositories.exam_repositories import ProvaRepository as ProvaRepositoryNew
from app.repositories.exam_repositories import (
    QuestaoRepository,
    prova_repo,
    questao_repo,
)


__all__ = ["ProvaRepositoryNew", "QuestaoRepository", "prova_repo", "questao_repo"]
