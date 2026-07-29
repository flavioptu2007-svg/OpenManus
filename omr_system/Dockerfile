FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libzbar0 libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV FLASK_ENV=production
EXPOSE 5000

CMD ["gunicorn","--bind","0.0.0.0:5000","--workers","4","run:app"]
