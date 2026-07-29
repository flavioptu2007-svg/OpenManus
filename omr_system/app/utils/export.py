"""Utilitários de exportação: CSV, JSON, PDF."""
import csv
import io
import json
import logging
from datetime import datetime
from typing import List

from app.models.exam import Prova

logger = logging.getLogger(__name__)


def export_csv(folhas: list) -> str:
    """
    Gera CSV a partir de lista de FolhaResposta.
    Retorna string CSV.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "ID", "Prova ID", "Aluno", "Data",
        "Nota", "Acertos", "Total", "Status",
    ])

    for folha in folhas:
        respostas = folha.respostas_dict() if hasattr(folha, 'respostas_dict') else {}
        writer.writerow([
            folha.id,
            folha.prova_id,
            folha.aluno_info or "",
            folha.data_processamento.strftime("%Y-%m-%d %H:%M") if folha.data_processamento else "",
            folha.nota or 0,
            folha.acertos or 0,
            len(respostas),
            folha.status or "",
        ])

    return output.getvalue()


def export_json(folhas: list) -> str:
    """Gera JSON formatado a partir de lista de FolhaResposta."""
    data = {
        "exportado_em": datetime.utcnow().isoformat(),
        "total": len(folhas),
        "folhas": [f.to_dict() for f in folhas],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def export_pdf(folhas: list, titulo: str = "Relatório de Provas") -> bytes:
    """
    Gera um PDF simples com relatório de resultados.
    Requer a biblioteca `reportlab`.
    Retorna bytes do PDF.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        )
        from reportlab.lib.units import mm
        from reportlab.lib.enums import TA_CENTER
    except ImportError:
        raise ImportError(
            "reportlab não instalado. Execute: pip install reportlab"
        )

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)

    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'CustomTitle', parent=styles['Title'],
        fontSize=18, spaceAfter=12, alignment=TA_CENTER,
    )
    style_h2 = ParagraphStyle(
        'H2', parent=styles['Heading2'], fontSize=14, spaceAfter=8,
    )

    elements = []
    elements.append(Paragraph(titulo, style_title))
    elements.append(Spacer(1, 12))

    if not folhas:
        elements.append(Paragraph("Nenhum resultado disponível.", styles['Normal']))
    else:
        total_notas = [f.nota for f in folhas if f.nota is not None]

        # Stats
        media = sum(total_notas) / len(total_notas) if total_notas else 0
        elements.append(Paragraph(
            f"Total de provas: {len(folhas)} | "
            f"Média: {media:.1f} | "
            f"Maior: {max(total_notas) if total_notas else 0:.1f} | "
            f"Menor: {min(total_notas) if total_notas else 0:.1f}",
            styles['Normal']
        ))
        elements.append(Spacer(1, 12))

        # Tabela
        table_data = [["ID", "Aluno", "Nota", "Acertos", "Data"]]
        for f in folhas:
            table_data.append([
                str(f.id),
                (f.aluno_info or "")[:30],
                f"{f.nota:.1f}" if f.nota is not None else "-",
                str(f.acertos or 0),
                f.data_processamento.strftime("%d/%m/%Y") if f.data_processamento else "",
            ])

        col_widths = [30, 120, 50, 50, 80]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (2, 0), (3, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F3F4")]),
        ]))
        elements.append(table)

    doc.build(elements)
    return buf.getvalue()


# ── Export para Prova ────────────────────────────────────


def export_to_csv(provas: List[Prova]) -> str:
    """
    Exporta lista de provas para CSV.

    Returns:
        String com conteúdo CSV.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "nome", "data", "qr_code_info", "marked_answers", "status", "created_at"])

    for p in provas:
        writer.writerow([
            p.id, p.nome,
            p.data.isoformat() if p.data else "",
            p.qr_code_info or "",
            p.marked_answers,
            p.status,
            p.created_at.isoformat(),
        ])

    logger.info(f"CSV gerado para {len(provas)} provas.")
    return output.getvalue()


def export_to_json(provas: List[Prova]) -> str:
    """Exporta lista de provas para JSON formatado."""
    data = [p.to_dict(include_questoes=True) for p in provas]
    return json.dumps(data, ensure_ascii=False, indent=2)


def export_questoes_csv(prova: Prova) -> str:
    """Exporta as questões de uma prova para CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "texto", "habilidade", "dificuldade"])

    for q in prova.questoes:
        writer.writerow([q.id, q.texto, q.habilidade or "", q.dificuldade or ""])

    return output.getvalue()
