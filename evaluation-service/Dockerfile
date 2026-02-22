FROM python:3.9

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn pydantic

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]