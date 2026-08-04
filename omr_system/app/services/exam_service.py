"""Lógica de negócio para Provas e Questões."""

import logging
from datetime import datetime
from typing import List, Optional

from app.exceptions import NotFoundError, ValidationError
from app.extensions import db
from app.models.exam import Prova, Questao
from app.repositories.exam_repo import prova_repo, questao_repo


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
    def create_with_questions(
        nome: Optional[str] = None, question_ids: Optional[List[int]] = None
    ) -> Prova:
        """Cria prova a partir de IDs de questões (ou das não atribuídas)."""
        if question_ids:
            questoes = questao_repo.get_by_ids(question_ids)
            if not questoes:
                raise ValidationError(
                    "Nenhuma questão válida encontrada para os IDs informados. "
                    "Use GET /api/v1/questoes para listar IDs válidos."
                )
        else:
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
    def list_paginated(
        page: int = 1, per_page: int = 10, limit: int = None, offset: int = None
    ) -> dict:
        """Lista provas com paginação page/per_page ou limit/offset.

        O modo limit/offset devolve total, has_more e next_offset
        (formato exigido pela API v1).
        """
        if limit is not None or offset is not None:
            lim = limit or 50
            off = offset or 0
            query = Prova.query.filter(Prova.deleted_at.is_(None)).order_by(Prova.id)
            total = query.count()
            items = query.offset(off).limit(lim).all()
            next_off = off + len(items) if off + len(items) < total else None
            return {
                "provas": [p.to_dict() for p in items],
                "total": total,
                "limit": lim,
                "offset": off,
                "has_more": off + len(items) < total,
                "next_offset": next_off,
            }

        pg = prova_repo.paginate(page, per_page)
        return {
            "provas": [p.to_dict() for p in pg.items],
            "total": pg.total,
            "pages": pg.pages,
            "current_page": page,
            "per_page": per_page,
            "has_more": page < pg.pages,
            "next_offset": page * per_page if page < pg.pages else None,
        }

    @staticmethod
    def list_questoes_paginated(
        page: int = 1,
        per_page: int = 10,
        limit: int = None,
        offset: int = None,
        materia: str = None,
        serie: str = None,
        dificuldade: str = None,
    ) -> dict:
        """Lista questões com filtros e paginação page/per_page ou limit/offset."""
        if limit is not None or offset is not None:
            lim = limit or 50
            off = offset or 0
            items, total = questao_repo.query_filtered(
                materia=materia,
                serie=serie,
                dificuldade=dificuldade,
                limit=lim,
                offset=off,
            )
            next_off = off + len(items) if off + len(items) < total else None
            return {
                "questoes": [q.to_dict() for q in items],
                "total": total,
                "limit": lim,
                "offset": off,
                "has_more": off + len(items) < total,
                "next_offset": next_off,
            }

        items, total = questao_repo.query_filtered(
            materia=materia,
            serie=serie,
            dificuldade=dificuldade,
            limit=per_page,
            offset=(page - 1) * per_page,
        )
        return {
            "questoes": [q.to_dict() for q in items],
            "total": total,
            "pages": (total + per_page - 1) // per_page if per_page else 0,
            "current_page": page,
            "per_page": per_page,
            "has_more": page * per_page < total,
            "next_offset": page * per_page if page * per_page < total else None,
        }

    @staticmethod
    def add_questao(
        texto: str,
        habilidade: str = None,
        dificuldade: str = None,
        materia: str = None,
        serie: str = None,
    ) -> Questao:
        if not texto or not texto.strip():
            raise ValidationError("Texto da questão não pode ser vazio.")
        if dificuldade and dificuldade not in Questao.DIFICULDADES:
            raise ValidationError(
                f"Dificuldade inválida. Use: {', '.join(Questao.DIFICULDADES)}."
            )
        q = Questao(
            texto=texto.strip(),
            habilidade=habilidade,
            dificuldade=dificuldade,
            materia=materia,
            serie=serie,
        )
        return questao_repo.save(q)
