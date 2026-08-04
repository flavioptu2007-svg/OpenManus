"""Modelos do sistema OMR."""

from app.models.cp_report import CPReport
from app.models.prova import FolhaResposta, Prova, Questao
from app.models.user import User


__all__ = ["Prova", "Questao", "FolhaResposta", "CPReport", "User"]
