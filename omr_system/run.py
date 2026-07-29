"""Entry point WSGI do servidor OMR — usado pelo Dockerfile/Docker Compose."""
import os

from app import create_app
from app.tasks.image_tasks import make_celery, register_tasks

app = create_app()
celery = make_celery(app)
register_tasks(celery)

if __name__ == "__main__":
    debug = os.environ.get("FLASK_ENV", "development") != "production"
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug)
