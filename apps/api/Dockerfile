FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY apps/api /app/apps/api
RUN python -m pip install --no-cache-dir --upgrade pip && python -m pip install --no-cache-dir -e "/app/apps/api[postgres]"
WORKDIR /app/apps/api
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn aimn_api.main:app --host 0.0.0.0 --port 8000 --app-dir src"]
