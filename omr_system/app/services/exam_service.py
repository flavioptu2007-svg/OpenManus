"""Lógica de negócio para Provas e Questões."""
import logging
from datetime import datetime
from typing import List, Optional

from app.extensions import db
from app.models.exam import Prova, Questao
from app.repositories.exam_repo import prova_repo, questao_repo
from app.exceptions import ValidationError, NotFoundError

logger = logging.getLogger(__name__)


class ExamService:

    @staticmethod
    def create_pending(nome: str = None, webhook_url: str = None) -> Prova:
        """Cria prova com status 'pending' para processamento async."""
        prova = Prova(
            nome=nome or f"Prova {datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            data=datetime.utcnow().date(),
            status="pending",
            webhook_url=webhook_url,
        )
        return prova_repo.save(prova)

    @staticmethod
    def finalize_from_image(prova: Prova, qr_data: List[str], marked: int) -> Prova:
        prova.qr_code_info = ", ".join(qr_data)
        prova.marked_answers = marked
        prova.status = "done"
        db.session.commit()
        return prova

    @staticmethod
    def create_from_image(qr_data: List[str], marked_count: int) -> Prova:
        prova = Prova(
            nome=f"Prova {datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            data=datetime.utcnow().date(),
            qr_code_info=", ".join(qr_data),
            marked_answers=marked_count,
            status="done",
        )
        return prova_repo.save(prova)

    @staticmethod
    def create_with_questions(nome: Optional[str] = None) -> Prova:
        questoes = questao_repo.get_unassigned()
        if not questoes:
            raise ValidationError("Não há questões disponíveis.")

        prova = Prova(
            nome=nome or f"Prova Criada {datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            data=datetime.utcnow().date(),
            status="done",
        )
        db.session.add(prova)
        db.session.flush()
        questao_repo.assign_to_prova(questoes, prova.id)
        db.session.commit()
        logger.info(f"Prova {prova.id} criada com {len(questoes)} questões.")
        return prova

    @staticmethod
    def get_by_id(prova_id: int) -> Prova:
        prova = prova_repo.get_by_id(prova_id)
        if not prova:
            raise NotFoundError(f"Prova {prova_id} não encontrada.")
        return prova

    @staticmethod
    def list_paginated(page: int, per_page: int) -> dict:
        pg = prova_repo.paginate(page, per_page)
        return {
            "provas": [p.to_dict() for p in pg.items],
            "total": pg.total,
            "pages": pg.pages,
            "current_page": page,
            "per_page": per_page,
        }

    @staticmethod
    def list_questoes_paginated(page: int, per_page: int) -> dict:
        pg = questao_repo.paginate(page, per_page)
        return {
            "questoes": [q.to_dict() for q in pg.items],
            "total": pg.total,
            "pages": pg.pages,
            "current_page": page,
            "per_page": per_page,
        }

    @staticmethod
    def add_questao(texto: str, habilidade: str = None, dificuldade: str = None) -> Questao:
        if not texto or not texto.strip():
            raise ValidationError("Texto da questão não pode ser vazio.")
        if dificuldade and dificuldade not in Questao.DIFICULDADES:
            raise ValidationError(f"Dificuldade inválida. Use: {', '.join(Questao.DIFICULDADES)}.")
        q = Questao(texto=texto.strip(), habilidade=habilidade, dificuldade=dificuldade)
        return questao_repo.save(q)
