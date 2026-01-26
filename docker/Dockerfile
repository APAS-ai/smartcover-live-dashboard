FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app
COPY app/fastapi_app ./fastapi_app
COPY docker/entrypoint.sh .

EXPOSE 8501 8080

ENTRYPOINT ["bash", "entrypoint.sh"]
