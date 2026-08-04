"""Utilitários do sistema OMR."""

from app.utils.export import export_csv, export_json, export_pdf
from app.utils.image_processing import deskew_image, detect_grid, preprocess_image
from app.utils.omr import detect_answer_sheet
from app.utils.qr_reader import extract_prova_id, extract_qr_info
from app.utils.scoring import (
    calcular_nota,
    find_marked_answers,
    find_marked_answers_with_confidence,
)


__all__ = [
    "preprocess_image",
    "deskew_image",
    "detect_grid",
    "extract_qr_info",
    "extract_prova_id",
    "find_marked_answers",
    "find_marked_answers_with_confidence",
    "calcular_nota",
    "export_csv",
    "export_json",
    "export_pdf",
    "detect_answer_sheet",
]
