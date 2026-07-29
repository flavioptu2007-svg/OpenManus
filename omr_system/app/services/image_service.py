"""Serviço de imagem — salva e processa usando OMR avançado."""
import os
import logging

import cv2
from werkzeug.datastructures import FileStorage

from app.exceptions import ValidationError, ImageProcessingError, StorageError
from app.utils.validators import validate_image_file, make_secure_filename
from app.utils.omr import detect_answer_sheet
from app.utils.qr_reader import decode_qr_codes

logger = logging.getLogger(__name__)


class ImageService:
    def __init__(self, upload_folder: str, config: dict = None):
        self.upload_folder = upload_folder
        self.config = config or {}
        os.makedirs(upload_folder, exist_ok=True)

    def save_only(self, file: FileStorage) -> dict:
        """Valida e salva o arquivo sem processar. Retorna filepath."""
        validate_image_file(file)
        filename = make_secure_filename(file.filename)
        filepath = os.path.join(self.upload_folder, filename)
        try:
            file.save(filepath)
            return {"filename": filename, "filepath": filepath}
        except OSError as e:
            raise StorageError(f"Falha ao salvar arquivo: {e}")

    def process_image(self, filepath: str) -> dict:
        """Processa a imagem já salva em disco com OMR avançado."""
        image = cv2.imread(filepath)
        if image is None:
            raise ImageProcessingError(f"Não foi possível ler '{filepath}'.")

        qr_data = decode_qr_codes(image)
        result = detect_answer_sheet(image)
        logger.info(f"Imagem processada: {result['marked_count']} marcações | conf={result['confidence']}")

        return {
            "qr_data": qr_data,
            "marked_answers_count": result["marked_count"],
            "total_bubbles": result["total_bubbles"],
            "confidence": result["confidence"],
        }

    def process(self, file: FileStorage) -> dict:
        """Pipeline completo: valida → salva → processa."""
        saved = self.save_only(file)
        return self.process_image(saved["filepath"])
