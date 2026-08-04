"""Exceções personalizadas do sistema OMR."""


class ImageProcessingError(Exception):
    """Erro durante o processamento de imagem ou OMR."""


class ValidationError(Exception):
    """Erro de validação de dados de entrada."""


class NotFoundError(Exception):
    """Recurso não encontrado."""


class StorageError(Exception):
    """Erro ao salvar/ler arquivos em disco."""
