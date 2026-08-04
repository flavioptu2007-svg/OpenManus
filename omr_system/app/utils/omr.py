"""
OMR — Optical Mark Recognition avançado.
Detecta marcações em gabaritos com correção de perspectiva e análise de bolhas.
"""

import logging
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np

from app.exceptions import ImageProcessingError


logger = logging.getLogger(__name__)


def detect_answer_sheet(image: np.ndarray) -> Dict[str, Any]:
    """
    Pipeline completo de OMR:
    1. Pré-processamento
    2. Detecção de contornos candidatos
    3. Correção de perspectiva (se possível)
    4. Detecção de bolhas marcadas
    5. Retorno de resultado estruturado

    Args:
        image: Imagem BGR como numpy array.

    Returns:
        Dict com marked_count, confidence, regions e imagem processada.
    """
    if image is None or image.size == 0:
        raise ImageProcessingError("Imagem inválida para OMR.")

    try:
        preprocessed = _preprocess(image)
        sheet_region = _find_answer_sheet(preprocessed, image)
        bubbles = _detect_bubbles(
            sheet_region if sheet_region is not None else preprocessed
        )
        marked = _classify_marked(
            sheet_region if sheet_region is not None else preprocessed, bubbles
        )
        confidence = _compute_confidence(bubbles, marked)

        logger.info(
            f"OMR: {len(marked)} marcações detectadas | {len(bubbles)} bolhas | conf={confidence:.2f}"
        )

        return {
            "marked_count": len(marked),
            "total_bubbles": len(bubbles),
            "confidence": round(confidence, 3),
            "marked_indices": marked,
        }
    except ImageProcessingError:
        raise
    except Exception as e:
        logger.error(f"Erro no pipeline OMR: {e}")
        raise ImageProcessingError(f"Falha no OMR: {str(e)}")


def _preprocess(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11,
        2,
    )
    return thresh


def _find_answer_sheet(thresh: np.ndarray, original: np.ndarray):
    """Tenta detectar e corrigir perspectiva da folha de gabarito."""
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    for c in candidates:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            return _four_point_transform(original, approx.reshape(4, 2))
    return None


def _four_point_transform(image: np.ndarray, pts: np.ndarray) -> np.ndarray:
    """Aplica correção de perspectiva com 4 pontos."""
    rect = _order_points(pts)
    tl, tr, br, bl = rect

    width = max(int(np.linalg.norm(br - bl)), int(np.linalg.norm(tr - tl)))
    height = max(int(np.linalg.norm(tr - br)), int(np.linalg.norm(tl - bl)))

    dst = np.array(
        [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]],
        dtype="float32",
    )
    M = cv2.getPerspectiveTransform(rect.astype("float32"), dst)
    return cv2.warpPerspective(image, M, (width, height))


def _order_points(pts: np.ndarray) -> np.ndarray:
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def _detect_bubbles(image: np.ndarray) -> List[Tuple]:
    """Detecta bolhas circulares na imagem."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            11,
            2,
        )
    else:
        thresh = image

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bubbles = []
    for c in contours:
        area = cv2.contourArea(c)
        if 30 < area < 800:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.03 * peri, True)
            if len(approx) >= 4:
                (x, y), r = cv2.minEnclosingCircle(c)
                circularity = area / (np.pi * r * r) if r > 0 else 0
                if circularity > 0.5:
                    bubbles.append((int(x), int(y), int(r), c))
    return bubbles


def _classify_marked(image: np.ndarray, bubbles: List[Tuple]) -> List[int]:
    """Classifica quais bolhas estão marcadas (mais pixels preenchidos)."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        img = image

    fill_ratios = []
    for _x, _y, _r, contour in bubbles:
        mask = np.zeros(img.shape, dtype="uint8")
        cv2.drawContours(mask, [contour], -1, 255, -1)
        total = cv2.countNonZero(mask)
        filled = cv2.countNonZero(cv2.bitwise_and(img, img, mask=mask))
        ratio = filled / total if total > 0 else 0
        fill_ratios.append(ratio)

    if not fill_ratios:
        return []

    threshold = np.mean(fill_ratios) + 0.1
    return [i for i, r in enumerate(fill_ratios) if r >= threshold]


def calcular_nota(respostas: dict, gabarito: dict, escala: float = 10.0) -> tuple:
    """
    Compara respostas com gabarito e retorna (nota, acertos).
    Respostas ANULADA são ignoradas (não contam como erro nem acerto).
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


def _compute_confidence(bubbles: List, marked: List[int]) -> float:
    """Estima confiança com base na quantidade de bolhas e marcações."""
    if not bubbles:
        return 0.0
    ratio = len(marked) / len(bubbles)
    if 0.05 <= ratio <= 0.5:
        return min(0.95, 0.5 + ratio)
    return 0.4
