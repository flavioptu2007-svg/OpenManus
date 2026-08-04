"""Extensões Flask — instâncias únicas para evitar imports circulares."""

from flask_caching import Cache
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address, default_limits=["500/day", "100/hour"])
jwt = JWTManager()
cache = Cache()
