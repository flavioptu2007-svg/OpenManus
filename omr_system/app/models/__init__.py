"""Modelos do sistema OMR."""
from app.models.prova import Prova, Questao, FolhaResposta
from app.models.cp_report import CPReport
from app.models.user import User

__all__ = ["Prova", "Questao", "FolhaResposta", "CPReport", "User"]
