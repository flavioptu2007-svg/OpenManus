"""Schemas Marshmallow para validação e serialização."""
from marshmallow import Schema, fields, validate, validates, ValidationError


class QuestaoSchema(Schema):
    id          = fields.Int(dump_only=True)
    texto       = fields.Str(required=True, validate=validate.Length(min=5, max=2000))
    habilidade  = fields.Str(validate=validate.Length(max=50))
    dificuldade = fields.Str(validate=validate.OneOf(["Fácil", "Médio", "Difícil"]))
    prova_id    = fields.Int(dump_only=True, allow_none=True)
    created_at  = fields.DateTime(dump_only=True)

    @validates("texto")
    def validate_texto(self, value):
        if not value.strip():
            raise ValidationError("O texto da questão não pode ser vazio ou apenas espaços.")


class ProvaCreateSchema(Schema):
    nome        = fields.Str(validate=validate.Length(max=100))
    data        = fields.Date(allow_none=True, load_default=None)
    webhook_url = fields.Url(allow_none=True, load_default=None)


class ProvaResponseSchema(Schema):
    id             = fields.Int()
    nome           = fields.Str()
    data           = fields.Date()
    qr_code_info   = fields.Str()
    marked_answers = fields.Int()
    status         = fields.Str()
    task_id        = fields.Str(allow_none=True)
    created_at     = fields.DateTime()
    updated_at     = fields.DateTime()
    questoes       = fields.List(fields.Nested(QuestaoSchema), load_default=None)


class PaginationSchema(Schema):
    page     = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(load_default=10, validate=validate.Range(min=1, max=100))


class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


questao_schema         = QuestaoSchema()
questoes_schema        = QuestaoSchema(many=True)
prova_create_schema    = ProvaCreateSchema()
prova_response_schema  = ProvaResponseSchema()
provas_response_schema = ProvaResponseSchema(many=True)
pagination_schema      = PaginationSchema()
login_schema           = LoginSchema()