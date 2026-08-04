"""Scoring utilities — answer detection and grade calculation."""

import logging

import cv2
import numpy as np


logger = logging.getLogger(__name__)


def find_marked_answers(
    image_path: str, grid_definition: dict, threshold: float = 0.65
) -> dict:
    """
    Detecta respostas marcadas usando densidade de pixels escuros na célula.
    Delegates to find_marked_answers_with_confidence for backward compat.
    """
    answers, _ = find_marked_answers_with_confidence(
        image_path, grid_definition, threshold
    )
    return answers


def find_marked_answers_with_confidence(
    image_path: str,
    grid_definition: dict,
    threshold: float = 0.65,
) -> tuple[dict, dict]:
    """
    Detecta respostas marcadas e calcula confiança por questão.

    Returns:
        (answers_dict, confidences_dict)
        - answers_dict: {q_num: 'A'|'B'|...|'ANULADA'|''}
        - confidences_dict: {q_num: confidence_int_0_99}
    """
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Imagem não encontrada: {image_path}")

        _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        answers = {}
        confidences = {}

        for q_num, alts in grid_definition["questoes"].items():
            best_alt, best_density = None, 0.0
            second_best_density = 0.0
            densities = {}

            for alt, coords in alts.items():
                roi = binary[
                    coords["top"] : coords["bottom"], coords["left"] : coords["right"]
                ]
                if roi.size == 0:
                    continue
                density = np.sum(roi > 0) / roi.size
                densities[alt] = density

                if density > best_density:
                    second_best_density = best_density
                    best_density = density
                    best_alt = alt
                elif density > second_best_density:
                    second_best_density = density

            if best_density >= threshold and best_alt:
                # Verificar múltiplas marcações
                valid_marks = [a for a, d in densities.items() if d >= threshold * 0.7]
                if len(valid_marks) > 1:
                    answers[str(q_num)] = "ANULADA"
                    confidences[str(q_num)] = round(best_density * 50)
                else:
                    answers[str(q_num)] = best_alt
                    # Confiança: densidade * margem sobre threshold
                    margin = best_density - second_best_density
                    confidence = (
                        best_density
                        * 100
                        * (0.6 + 0.4 * min(margin / max(threshold, 0.01), 1.0))
                    )
                    confidences[str(q_num)] = min(round(confidence), 99)
            else:
                answers[str(q_num)] = ""
                confidences[str(q_num)] = 0

        return answers, confidences

    except Exception as e:
        logger.error(f"find_marked_answers_with_confidence error: {e}")
        return {}, {}


def calcular_nota(
    respostas: dict, gabarito: dict, escala: float = 10.0
) -> tuple[float, int]:
    """
    Compara respostas com gabarito.
    Retorna (nota, acertos).
    """
    if not gabarito:
        return 0.0, 0
    if not respostas:
        return 0.0, 0
    acertos = sum(
        1
        for q, r in respostas.items()
        if r != "ANULADA" and gabarito.get(q, "").upper() == r.upper()
    )
    nota = round((acertos / len(gabarito)) * escala, 2)
    return nota, acertos
