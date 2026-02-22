FROM python:3.9

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    sentence-transformers \
    transformers \
    torch \
    faiss-cpu \
    numpy

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]