"""QR code reader utilities."""

import logging
import re

import cv2


logger = logging.getLogger(__name__)


def extract_qr_info(image_path: str) -> str | None:
    """Tenta ler QR code via OpenCV; fallback para pyzbar."""
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Imagem não encontrada: {image_path}")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Tentativa 1: OpenCV QRCodeDetector
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(gray)
        if data:
            return data

        # Tentativa 2: pyzbar
        try:
            from pyzbar.pyzbar import decode

            for obj in decode(gray):
                text = obj.data.decode("utf-8")
                if "prova_id:" in text:
                    return text
        except ImportError:
            logger.warning("pyzbar não instalado; pulando fallback.")

        logger.error("QR code não encontrado na imagem.")
        return None

    except Exception as e:
        logger.error(f"extract_qr_info error: {e}")
        return None


def extract_prova_id(qr_info: str) -> int | None:
    """Extrai o inteiro após 'prova_id:' no texto do QR."""
    if not qr_info:
        return None
    try:
        match = re.search(r"prova_id[:\s]+(\d+)", qr_info, re.IGNORECASE)
        if match:
            return int(match.group(1))
        logger.warning(f"Formato QR inválido: {qr_info}")
        return None
    except Exception as e:
        logger.error(f"extract_prova_id error: {e}")
        return None


def decode_qr_codes(image) -> list:
    """
    Decodifica QR codes de uma imagem numpy array (BGR).
    Retorna lista de strings decodificadas.
    """
    import numpy as np

    if image is None or (isinstance(image, np.ndarray) and image.size == 0):
        logger.warning("Imagem inválida para decode_qr_codes")
        return []

    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    except Exception:
        gray = (
            image if len(image.shape) == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        )

    results = []

    # Tentativa 1: OpenCV QRCodeDetector
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(gray)
    if data:
        results.append(data)

    # Tentativa 2: pyzbar (detecta múltiplos QR codes)
    try:
        from pyzbar.pyzbar import decode

        for obj in decode(gray):
            text = obj.data.decode("utf-8")
            if text not in results:
                results.append(text)
    except ImportError:
        pass
    except Exception as e:
        logger.debug(f"pyzbar decode error: {e}")

    return results
