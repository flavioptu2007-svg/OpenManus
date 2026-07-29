"""Image processing utilities — preprocess, deskew, detect_grid."""
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


def preprocess_image(image_path: str, output_path: str = None):
    """Pré-processa a imagem: grayscale + CLAHE + threshold adaptativo."""
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Imagem não encontrada: {image_path}")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
        binary = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        result = binary
        if output_path:
            cv2.imwrite(output_path, result)
        return result
    except Exception as e:
        logger.error(f"preprocess_image error: {e}")
        return None


def deskew_image(image_path: str, output_path: str = None):
    """Corrige inclinação da folha."""
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Imagem não encontrada: {image_path}")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255,
                                  cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            logger.warning("Nenhum contorno encontrado; imagem mantida.")
            if output_path:
                cv2.imwrite(output_path, img)
            return img

        best = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(best)
        ar = w / float(h)

        if not (0.5 < ar < 2.0):
            logger.warning(f"Aspect ratio fora do esperado ({ar:.2f}); deskew ignorado.")
            if output_path:
                cv2.imwrite(output_path, img)
            return img

        rect = cv2.minAreaRect(best)
        angle = rect[2]
        if angle < -45:
            angle += 90

        if abs(angle) < 0.5 or abs(angle) > 30:
            if output_path:
                cv2.imwrite(output_path, img)
            return img

        (H, W) = img.shape[:2]
        M = cv2.getRotationMatrix2D((W // 2, H // 2), angle, 1.0)
        rotated = cv2.warpAffine(img, M, (W, H),
                                  flags=cv2.INTER_CUBIC,
                                  borderMode=cv2.BORDER_REPLICATE)
        if output_path:
            cv2.imwrite(output_path, rotated)
        return rotated

    except Exception as e:
        logger.error(f"deskew_image error: {e}")
        return None


def detect_grid(image_path: str, min_lines: int = 5) -> dict | None:
    """Detecta a grade de questões via HoughLines."""
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Imagem não encontrada: {image_path}")

        edges = cv2.Canny(img, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 80,
                                  minLineLength=img.shape[1] * 0.4,
                                  maxLineGap=20)
        if lines is None:
            logger.error("Nenhuma linha detectada.")
            return None

        h_lines, v_lines = [], []
        # Normalizar shape: OpenCV pode retornar (N,1,4) ou (N,4)
        lines = lines.reshape(-1, 4)
        for x1, y1, x2, y2 in lines:
            angle = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            if angle < 10 or angle > 170:
                h_lines.append(y1)
            elif 80 < angle < 100:
                v_lines.append(x1)

        h_lines = sorted(set(_cluster(h_lines)))
        v_lines = sorted(set(_cluster(v_lines)))

        if len(h_lines) < min_lines or len(v_lines) < min_lines:
            logger.error(
                f"Linhas insuficientes: H={len(h_lines)}, V={len(v_lines)}")
            return None

        questoes = {}
        alternativas = [chr(65 + j) for j in range(len(v_lines) - 1)]
        for i in range(len(h_lines) - 1):
            q_num = i + 1
            questoes[q_num] = {}
            for j, alt in enumerate(alternativas):
                questoes[q_num][alt] = {
                    'top':    h_lines[i],
                    'bottom': h_lines[i + 1],
                    'left':   v_lines[j],
                    'right':  v_lines[j + 1]
                }

        return {'questoes': questoes,
                'h_lines': h_lines,
                'v_lines': v_lines}

    except Exception as e:
        logger.error(f"detect_grid error: {e}")
        return None


def _cluster(values: list, gap: int = 15) -> list:
    """Agrupa valores próximos, retornando a mediana de cada cluster."""
    if not values:
        return []
    values = sorted(values)
    clusters, group = [], [values[0]]
    for v in values[1:]:
        if v - group[-1] <= gap:
            group.append(v)
        else:
            clusters.append(int(np.median(group)))
            group = [v]
    clusters.append(int(np.median(group)))
    return clusters
