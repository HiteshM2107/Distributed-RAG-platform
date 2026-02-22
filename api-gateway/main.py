from fastapi import Depends, HTTPException, status, FastAPI, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
import requests
import time

SECRET_KEY = "super-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI(title="API Gateway")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INGESTION_URL = "http://ingestion-service:8001/upload"
RETRIEVAL_URL = "http://retrieval-service:8002/query"
EVALUATION_URL = "http://evaluation-service:8003"

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3
    chunk_size: int = 300

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Hardcoded user for demo
    if form_data.username != "admin" or form_data.password != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = create_access_token(
        data={"sub": form_data.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/upload")
async def upload(file: UploadFile = File(...), chunk_size: int = Form(300)):
    files = {"file": (file.filename, await file.read())}
    data = {"chunk_size": chunk_size}

    response = requests.post(INGESTION_URL, files=files, data=data)
    return response.json()


@app.post("/query")
def query(
    request: QueryRequest,
    token: str = Depends(oauth2_scheme)
):
    start_time = time.time()

    # Call retrieval service
    retrieval_response = requests.post(
        RETRIEVAL_URL,
        json={
            "query": request.query,
            "top_k": request.top_k
        }
    )

    retrieval_data = retrieval_response.json()

    total_latency = time.time() - start_time

    # Log experiment in evaluation service
    requests.post(
        f"{EVALUATION_URL}/log",
        json={
            "query": request.query,
            "chunk_size": request.chunk_size,
            "top_k": request.top_k,
            "retrieval_latency": retrieval_data["retrieval_latency"],
            "generation_latency": retrieval_data["generation_latency"],
            "total_latency": round(total_latency, 3),
            "context_length": retrieval_data["context_length"]
        }
    )

    retrieval_data["total_latency"] = round(total_latency, 3)

    return retrieval_data


@app.get("/metrics")
def metrics():
    response = requests.get(f"{EVALUATION_URL}/metrics")
    return response.json()


@app.get("/compare")
def compare(chunk_size: int = None, top_k: int = None):
    response = requests.get(
        f"{EVALUATION_URL}/compare",
        params={"chunk_size": chunk_size, "top_k": top_k}
    )
    return response.json()