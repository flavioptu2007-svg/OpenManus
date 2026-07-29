"""Validadores para arquivos de imagem."""
import os
import logging
from datetime import datetime

from werkzeug.utils import secure_filename

from app.exceptions import ValidationError

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB

# Magic bytes para detecção de tipo (sem depender de imghdr, removido no Python 3.14)
MAGIC_BYTES = {
    b"\xff\xd8": "jpeg",
    b"\x89PNG": "png",
}


def validate_image_file(file) -> None:
    """
    Valida um arquivo de imagem enviado por upload.

    Args:
        file: Flask FileStorage ou similar (com .filename)

    Raises:
        ValidationError: se o arquivo for inválido.
    """
    if not file:
        raise ValidationError("Nenhum arquivo enviado.")

    if not file.filename:
        raise ValidationError("Nome de arquivo vazio.")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"Formato '{ext}' não suportado. Use: {', '.join(sorted(ALLOWED_EXTENSIONS))}."
        )

    # Validar tamanho
    if hasattr(file, "content_length") and file.content_length and file.content_length > MAX_FILE_SIZE:
        raise ValidationError(
            f"Arquivo excede o limite de {MAX_FILE_SIZE // 1024 // 1024} MB."
        )

    # Validar conteúdo via magic bytes
    file.seek(0)
    header = file.read(8)
    file.seek(0)

    if not header:
        raise ValidationError("Arquivo vazio.")

    detected = False
    for magic, name in MAGIC_BYTES.items():
        if header.startswith(magic):
            detected = True
            break

    if not detected:
        raise ValidationError(
            f"Tipo de arquivo não reconhecido. Apenas JPEG e PNG são aceitos."
        )

    logger.info(f"Arquivo validado: {file.filename} ({ext})")


def make_secure_filename(original_filename: str) -> str:
    """Gera nome de arquivo seguro com timestamp para evitar colisões."""
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    return secure_filename(f"{ts}_{original_filename}")
