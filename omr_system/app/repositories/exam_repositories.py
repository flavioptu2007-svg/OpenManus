"""Repositórios específicos para Prova e Questao."""
from typing import List, Optional

from app.extensions import db
from app.models.prova import Prova, Questao
from app.repositories.base import BaseRepository


class ProvaRepository(BaseRepository[Prova]):
    def __init__(self):
        super().__init__(Prova)

    def get_by_status(self, status: str) -> List[Prova]:
        return Prova.query.filter_by(status=status, deleted_at=None).all()

    def update_status(self, prova_id: int, status: str, task_id: str = None) -> Optional[Prova]:
        prova = self.get_by_id(prova_id)
        if prova:
            prova.status = status
            if task_id:
                prova.task_id = task_id
            db.session.commit()
        return prova


class QuestaoRepository(BaseRepository[Questao]):
    def __init__(self):
        super().__init__(Questao)

    def get_unassigned(self) -> List[Questao]:
        """Questões que ainda não foram atribuídas a nenhuma prova."""
        return (
            Questao.query
            .filter(Questao.prova_id.is_(None), Questao.deleted_at.is_(None))
            .all()
        )

    def get_by_habilidade(self, habilidade: str) -> List[Questao]:
        return (
            Questao.query
            .filter_by(habilidade=habilidade, deleted_at=None)
            .all()
        )

    def assign_to_prova(self, questoes: List[Questao], prova_id: int) -> None:
        for q in questoes:
            q.prova_id = prova_id
        db.session.commit()


prova_repo   = ProvaRepository()
questao_repo = QuestaoRepository()
