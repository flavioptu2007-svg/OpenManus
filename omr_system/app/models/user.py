"""Modelos de Usuário e AuditLog."""
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(db.Model):
    """Usuário do sistema com autenticação."""
    __tablename__ = "users"

    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email      = db.Column(db.String(120), unique=True, nullable=False, index=True)
    _password  = db.Column("password", db.String(256), nullable=False)
    is_active  = db.Column(db.Boolean, default=True, nullable=False)
    is_admin   = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def password(self):
        raise AttributeError("Senha não é legível.")

    @password.setter
    def password(self, raw: str):
        self._password = generate_password_hash(raw)

    def verify_password(self, raw: str) -> bool:
        return check_password_hash(self._password, raw)

    def to_dict(self) -> dict:
        return {
            "id":         self.id,
            "username":   self.username,
            "email":      self.email,
            "is_admin":   self.is_admin,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self):
        return f"<User {self.username}>"


class AuditLog(db.Model):
    """Rastreia todas as ações relevantes do sistema."""
    __tablename__ = "audit_logs"

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action     = db.Column(db.String(80), nullable=False)   # ex: CREATE_PROVA
    entity     = db.Column(db.String(50), nullable=False)   # ex: Prova
    entity_id  = db.Column(db.Integer, nullable=True)
    details    = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", backref=db.backref("audit_logs", lazy="dynamic"))

    def to_dict(self) -> dict:
        return {
            "id":        self.id,
            "user_id":   self.user_id,
            "action":    self.action,
            "entity":    self.entity,
            "entity_id": self.entity_id,
            "details":   self.details,
            "ip":        self.ip_address,
            "created_at":self.created_at.isoformat(),
        }
