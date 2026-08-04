"""Script para popular o banco com dados de exemplo."""

import json
import os
import sys
from datetime import date


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from app.models.cp_report import CPReport
from app.models.prova import Prova, Questao
from app.models.user import User


def seed():
    app = create_app()
    with app.app_context():
        # Criar usuário admin
        admin = User(
            username="admin",
            email="admin@escola.edu",
            is_admin=True,
            is_active=True,
        )
        admin.password = "admin123"
        db.session.add(admin)

        # Criar prova de exemplo
        prova = Prova(
            nome="Prova Diagnóstica - História 6º Ano",
            data=date.today(),
            status="done",
        )
        db.session.add(prova)
        db.session.flush()

        # Criar questões associadas
        questoes_data = [
            ("Qual era o deus Sol no Egito Antigo?", "EF06HI01", "Fácil"),
            ("O que foi a Revolução Industrial?", "EF08HI01", "Difícil"),
            ("Explique o conceito de democracia ateniense.", "EF06HI01", "Médio"),
            ("Qual a importância do Rio Nilo para o Egito?", "EF06HI02", "Médio"),
            ("O que significa 'pré-história'?", "EF06HI03", "Fácil"),
        ]
        for texto, hab, dif in questoes_data:
            q = Questao(texto=texto, habilidade=hab, dificuldade=dif, prova_id=prova.id)
            db.session.add(q)

        prova.marked_answers = len(questoes_data)

        # Criar CP reports de exemplo
        for i in range(5):
            report = CPReport(
                aluno=f"Aluno {i+1}",
                turma="6º Ano A",
                tema="Egito Antigo",
                dificuldade="medio",
                palavras_total=8,
                palavras_encontradas=8 - i,
                tempo_segundos=60 + i * 30,
                is_record=i == 0,
                conquistas=json.dumps(["🏆 Vencedor"] if i == 0 else []),
            )
            db.session.add(report)

        db.session.commit()
        print(
            f"✅ Dados criados: admin (admin:admin123), 1 prova com 5 questões, 5 CP reports."
        )


if __name__ == "__main__":
    seed()
