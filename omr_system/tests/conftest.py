"""Fixtures do pytest para o sistema OMR."""
import os
import tempfile

import pytest

from app import create_app


@pytest.fixture(scope="module")
def app():
    """Create a Flask app configured for testing."""
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        UPLOAD_FOLDER=tempfile.mkdtemp(),
        WTF_CSRF_ENABLED=False,
    )

    with app.app_context():
        from app.extensions import db
        db.create_all()

    yield app


@pytest.fixture(scope="module")
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
