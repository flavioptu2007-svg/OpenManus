"""Re-export de app.models.prova — compatibilidade com código do usuário."""

from app.models.prova import (  # noqa: F401
    FolhaResposta,
    Prova,
    Questao,
    SoftDeleteMixin,
    seed_questoes,
)


__all__ = [
    "SoftDeleteMixin",
    "Prova",
    "Questao",
    "FolhaResposta",
    "seed_questoes",
]
