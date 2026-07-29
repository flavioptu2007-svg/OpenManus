"""Exceções personalizadas do sistema OMR."""


class ImageProcessingError(Exception):
    """Erro durante o processamento de imagem ou OMR."""
    pass


class ValidationError(Exception):
    """Erro de validação de dados de entrada."""
    pass


class NotFoundError(Exception):
    """Recurso não encontrado."""
    pass


class StorageError(Exception):
    """Erro ao salvar/ler arquivos em disco."""
    pass
