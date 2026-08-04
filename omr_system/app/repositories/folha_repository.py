"""Repository para operações com FolhaResposta."""

import json
from datetime import datetime
from typing import Optional

from app.extensions import db
from app.models.prova import FolhaResposta


class FolhaRepository:
    """Abstração de acesso a dados para FolhaResposta."""

    @staticmethod
    def get_by_id(folha_id: int) -> Optional[FolhaResposta]:
        return FolhaResposta.query.get(folha_id)

    @staticmethod
    def get_by_prova(prova_id: int) -> list[FolhaResposta]:
        return FolhaResposta.query.filter_by(prova_id=prova_id).all()

    @staticmethod
    def create(
        prova_id: int,
        respostas: dict,
        aluno_info: str = "",
        imagem_path: str = "",
        nota: float = 0.0,
        acertos: int = 0,
    ) -> FolhaResposta:
        folha = FolhaResposta(
            prova_id=prova_id,
            aluno_info=aluno_info,
            imagem_path=imagem_path,
            respostas=json.dumps(respostas),
            nota=nota,
            acertos=acertos,
            data_processamento=datetime.utcnow(),
            status="processado",
        )
        db.session.add(folha)
        db.session.commit()
        return folha

    @staticmethod
    def resultados_prova(prova_id: int) -> dict:
        folhas = FolhaResposta.query.filter_by(prova_id=prova_id).all()
        notas = [f.nota for f in folhas if f.nota is not None]
        return {
            "total_folhas": len(folhas),
            "media": round(sum(notas) / len(notas), 2) if notas else 0,
            "maior_nota": max(notas) if notas else 0,
            "menor_nota": min(notas) if notas else 0,
            "folhas": [f.to_dict() for f in folhas],
        }

    @staticmethod
    def count() -> int:
        return FolhaResposta.query.count()
