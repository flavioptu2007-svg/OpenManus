"""Modelos Prova, Questao e FolhaResposta com soft-delete e timestamps."""

from datetime import datetime

from app.extensions import db


class SoftDeleteMixin:
    """Soft-delete: registros não são removidos fisicamente."""

    deleted_at = db.Column(db.DateTime, nullable=True)

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class Prova(SoftDeleteMixin, db.Model):
    __tablename__ = "provas"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, index=True)
    data = db.Column(db.Date, nullable=False)
    qr_code_info = db.Column(db.String(500), default="")
    marked_answers = db.Column(db.Integer, default=0, nullable=False)
    task_id = db.Column(db.String(36), nullable=True)  # Celery task
    status = db.Column(db.String(20), default="pending")  # pending/done/error
    webhook_url = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    questoes = db.relationship(
        "Questao",
        backref=db.backref("prova", lazy="joined"),
        lazy="dynamic",
        primaryjoin="and_(Prova.id==Questao.prova_id, Questao.deleted_at==None)",
    )

    folhas = db.relationship("FolhaResposta", backref="prova", lazy=True)

    def __repr__(self):
        return f"<Prova id={self.id} nome='{self.nome}'>"

    def to_dict(self, include_questoes: bool = False) -> dict:
        data = {
            "id": self.id,
            "nome": self.nome,
            "data": self.data.isoformat() if self.data else None,
            "qr_code_info": self.qr_code_info,
            "marked_answers": self.marked_answers,
            "status": self.status,
            "task_id": self.task_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "num_questoes": self.questoes.count(),
        }
        if include_questoes:
            data["questoes"] = [q.to_dict() for q in self.questoes]
        return data


class Questao(SoftDeleteMixin, db.Model):
    __tablename__ = "questoes"

    DIFICULDADES = ("Fácil", "Médio", "Difícil")

    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    habilidade = db.Column(db.String(50), index=True)
    dificuldade = db.Column(db.String(20))
    materia = db.Column(db.String(60), nullable=True, index=True)  # ex: História
    serie = db.Column(db.String(30), nullable=True, index=True)  # ex: 8º Ano
    prova_id = db.Column(
        db.Integer, db.ForeignKey("provas.id", ondelete="SET NULL"), nullable=True
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Questao id={self.id}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "texto": self.texto,
            "habilidade": self.habilidade,
            "dificuldade": self.dificuldade,
            "materia": self.materia,
            "serie": self.serie,
            "prova_id": self.prova_id,
            "created_at": self.created_at.isoformat(),
        }


class FolhaResposta(db.Model):
    __tablename__ = "folhas_resposta"
    id = db.Column(db.Integer, primary_key=True)
    prova_id = db.Column(db.Integer, db.ForeignKey("provas.id"), nullable=False)
    aluno_info = db.Column(db.String(255))
    imagem_path = db.Column(db.String(500), nullable=False)
    respostas = db.Column(db.Text)  # JSON
    nota = db.Column(db.Float)
    acertos = db.Column(db.Integer)
    data_processamento = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="processado")
    erro_msg = db.Column(db.Text)

    def respostas_dict(self):
        import json

        return json.loads(self.respostas) if self.respostas else {}

    def to_dict(self):
        return {
            "id": self.id,
            "prova_id": self.prova_id,
            "aluno_info": self.aluno_info,
            "respostas": self.respostas_dict(),
            "nota": self.nota,
            "acertos": self.acertos,
            "status": self.status,
            "data_processamento": self.data_processamento.isoformat(),
        }


def seed_questoes():
    """Cria questões de exemplo."""
    exemplos = [
        Questao(
            texto="Qual é a capital do Brasil?",
            habilidade="EF06GE01",
            dificuldade="Fácil",
            materia="Geografia",
            serie="6º Ano",
        ),
        Questao(
            texto="Resolva: 2 + 2 = ?",
            habilidade="EF06MA01",
            dificuldade="Fácil",
            materia="Matemática",
            serie="6º Ano",
        ),
        Questao(
            texto="Defina o conceito de democracia.",
            habilidade="EF06HI01",
            dificuldade="Médio",
            materia="História",
            serie="6º Ano",
        ),
        Questao(
            texto="Explique a Revolução Industrial.",
            habilidade="EF08HI01",
            dificuldade="Difícil",
            materia="História",
            serie="8º Ano",
        ),
        Questao(
            texto="O que é fotossíntese?",
            habilidade="EF06CI01",
            dificuldade="Médio",
            materia="Ciências",
            serie="6º Ano",
        ),
    ]
    db.session.add_all(exemplos)
    db.session.commit()
