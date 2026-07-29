"""Schemas para endpoints de Provas, Questões e Auth — reexporta de omr_schemas."""
from app.schemas.omr_schemas import (
    QuestaoSchema,
    ProvaCreateSchema,
    ProvaResponseSchema,
    PaginationSchema,
    LoginSchema,
    questao_schema,
    questoes_schema,
    prova_create_schema,
    prova_response_schema,
    provas_response_schema,
    pagination_schema,
    login_schema,
)

__all__ = [
    "QuestaoSchema",
    "ProvaCreateSchema",
    "ProvaResponseSchema",
    "PaginationSchema",
    "LoginSchema",
    "questao_schema",
    "questoes_schema",
    "prova_create_schema",
    "prova_response_schema",
    "provas_response_schema",
    "pagination_schema",
    "login_schema",
]
