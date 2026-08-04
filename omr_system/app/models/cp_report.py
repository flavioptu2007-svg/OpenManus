"""Modelo CPReport — relatório de desempenho do Caça-Palavras."""

import json
from datetime import datetime

from app.extensions import db


class CPReport(db.Model):
    """Relatório de desempenho do Caça-Palavras."""

    __tablename__ = "cp_report"
    id = db.Column(db.Integer, primary_key=True)
    aluno = db.Column(db.String(255), default="")
    turma = db.Column(db.String(100), default="")
    tema = db.Column(db.String(100), default="")
    dificuldade = db.Column(db.String(50), default="medio")
    palavras_total = db.Column(db.Integer, default=0)
    palavras_encontradas = db.Column(db.Integer, default=0)
    tempo_segundos = db.Column(db.Integer, default=0)
    score_percentual = db.Column(db.Float, default=0.0)
    is_record = db.Column(db.Boolean, default=False)
    conquistas = db.Column(db.Text, default="[]")  # JSON array
    modo = db.Column(db.String(50), default="tema")  # theme | disc
    disciplina = db.Column(db.String(100), default="")
    periodo = db.Column(db.Integer, default=0)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    def conquistas_list(self):
        return json.loads(self.conquistas) if self.conquistas else []

    def to_dict(self):
        return {
            "id": self.id,
            "aluno": self.aluno,
            "turma": self.turma,
            "tema": self.tema,
            "dificuldade": self.dificuldade,
            "palavras_total": self.palavras_total,
            "palavras_encontradas": self.palavras_encontradas,
            "tempo_segundos": self.tempo_segundos,
            "score_percentual": self.score_percentual,
            "is_record": self.is_record,
            "conquistas": self.conquistas_list(),
            "modo": self.modo,
            "disciplina": self.disciplina,
            "periodo": self.periodo,
            "data_criacao": self.data_criacao.isoformat(),
        }
