"""Repository para operações com Prova."""
from datetime import date
from typing import Optional

from app.extensions import db
from app.models.prova import Prova, Questao


class ProvaRepository:
    """Abstração de acesso a dados para Prova."""

    @staticmethod
    def get_by_id(prova_id: int) -> Optional[Prova]:
        return Prova.query.get(prova_id)

    @staticmethod
    def get_by_id_or_404(prova_id: int) -> Prova:
        return Prova.query.get_or_404(prova_id)

    @staticmethod
    def list_all() -> list[Prova]:
        return Prova.query.order_by(Prova.created_at.desc()).all()

    @staticmethod
    def list_by_nome(query: str) -> list[Prova]:
        return Prova.query.filter(Prova.nome.ilike(f"%{query}%")).order_by(
            Prova.created_at.desc()
        ).all()

    @staticmethod
    def create(nome: str, data_prova: Optional[str] = None) -> Prova:
        try:
            data_parsed = date.fromisoformat(data_prova) if data_prova else date.today()
        except (ValueError, TypeError):
            data_parsed = date.today()
        prova = Prova(nome=nome, data=data_parsed, status="pending")
        db.session.add(prova)
        db.session.commit()
        return prova

    @staticmethod
    def update(prova: Prova, **kwargs) -> Prova:
        if "nome" in kwargs:
            prova.nome = kwargs["nome"]
        if "status" in kwargs:
            prova.status = kwargs["status"]
        if "qr_code_info" in kwargs:
            prova.qr_code_info = kwargs["qr_code_info"]
        if "task_id" in kwargs:
            prova.task_id = kwargs["task_id"]
        if "webhook_url" in kwargs:
            prova.webhook_url = kwargs["webhook_url"]
        db.session.commit()
        return prova

    @staticmethod
    def soft_delete(prova_id: int) -> bool:
        prova = Prova.query.get(prova_id)
        if not prova:
            return False
        prova.soft_delete()
        db.session.commit()
        return True

    @staticmethod
    def add_questao(prova_id: int, texto: str,
                    habilidade: str = "", dificuldade: str = "") -> Questao:
        prova = Prova.query.get_or_404(prova_id)
        questao = Questao(
            texto=texto,
            habilidade=habilidade,
            dificuldade=dificuldade,
            prova_id=prova.id,
        )
        db.session.add(questao)
        prova.marked_answers = prova.questoes.count()
        db.session.commit()
        return questao

    @staticmethod
    def count() -> int:
        return Prova.query.count()
