# Distributed RAG Platform with Kubernetes Autoscaling

A distributed Retrieval-Augmented Generation (RAG) system built using a microservices architecture and deployed on Kubernetes with resource governance and Horizontal Pod Autoscaling (HPA).

This platform enables document ingestion, vector indexing, semantic retrieval, large language model inference, experiment tracking, and dynamic workload scaling under load.

---

## Overview

This project implements a production-style distributed RAG infrastructure composed of independent services:

- API Gateway (JWT authentication and orchestration)
- Ingestion Service (PDF processing and embedding generation)
- Retrieval Service (FAISS vector search and LLM inference)
- Evaluation Service (experiment logging and comparison)
- React Frontend (dashboard and experiment visualization)

The system is containerized using Docker and deployed locally on Kubernetes (kind), including:

- Persistent storage
- Resource requests and limits
- CPU-based Horizontal Pod Autoscaler
- Metrics Server integration
- Multi-replica scaling under load

---

## System Architecture

The platform follows a distributed microservices architecture:

```
                        ┌────────────────────┐
                        │      Frontend      │
                        │   (NodePort 3000)  │
                        └──────────┬─────────┘
                                   │
                                   ▼
                        ┌────────────────────┐
                        │    API Gateway     │
                        │   JWT Auth + RAG   │
                        └───────┬────────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
┌────────────────┐   ┌────────────────┐   ┌────────────────┐
│ Ingestion Svc  │   │ Retrieval Svc  │   │ Evaluation Svc │
│ PDF + Embeds   │   │ FAISS + LLM    │   │ Metrics DB     │
└────────────────┘   └────────────────┘   └────────────────┘
                              ▲
                              │
                  Horizontal Pod Autoscaler
                   (CPU-based scaling)
                              │
                              ▼
                    Multiple Retrieval Pods
```

---

## Core Components

### API Gateway
- JWT-based authentication
- Request validation
- Routing to downstream services
- Secure access to query endpoint

### Ingestion Service
- PDF parsing
- Text chunking
- SentenceTransformer embeddings
- FAISS index creation
- Persistent vector storage

### Retrieval Service
- Semantic similarity search using FAISS
- Context assembly
- LLM inference using FLAN-T5
- CPU-based autoscaling via Kubernetes HPA

### Evaluation Service
- Experiment tracking
- Latency logging
- Configuration comparison (chunk size, top-k)
- SQLite-backed persistence

### Frontend
- React dashboard
- Query interface
- Experiment filtering
- Latency visualization
- Dark mode UI
- Auth-gated access

---

## System Design Deep Dive

This section outlines the architectural decisions, trade-offs, scalability considerations, and operational characteristics of the Distributed RAG Platform.

---

### 1. Design Goals

The system was designed with the following goals:

- Decouple ingestion, retrieval, evaluation, and API layers
- Enable independent horizontal scaling of compute-heavy services
- Maintain persistent vector storage across restarts
- Provide experiment observability and performance tracking
- Simulate production-grade Kubernetes deployment patterns
- Support dynamic workload scaling under query load

---

### 2. High-Level Architecture

The system follows a microservices-based architecture deployed inside a Kubernetes cluster.

Each service has a single responsibility:

- API Gateway: authentication and orchestration
- Ingestion Service: document processing and embedding
- Retrieval Service: vector search and LLM inference
- Evaluation Service: experiment logging and comparison
- Frontend: user interface and experiment visualization

Services communicate over internal Kubernetes DNS using ClusterIP services.

---

### 3. Data Flow (Query Lifecycle)

1. User logs in via JWT-authenticated API.
2. Query is submitted to the API Gateway.
3. Gateway forwards request to Retrieval Service.
4. Retrieval Service:
   - Generates embedding for query
   - Performs FAISS similarity search
   - Retrieves top-k relevant chunks
   - Constructs prompt
   - Runs LLM inference (FLAN-T5)
5. Response is returned to Gateway.
6. Evaluation Service logs latency, configuration, and metadata.
7. Frontend visualizes response and experiment metrics.

This separation allows retrieval to scale independently from ingestion or evaluation.

---

### 4. Persistent Storage Strategy

FAISS index and metadata are stored in a Kubernetes PersistentVolumeClaim mounted at `/shared-data`.

This ensures:

- Vector index durability across pod restarts
- Shared access between ingestion and retrieval services
- No in-memory state loss on container recreation

Trade-off:
- ReadWriteOnce PVC limits horizontal scaling to a single node.
- For production scale, a distributed vector database (e.g., Milvus or Pinecone) would replace local FAISS.

---

### 5. Scalability Model

The Retrieval Service is the most compute-intensive component due to:

- Embedding generation
- Vector search
- LLM inference

To support load spikes:

- CPU requests and limits are defined
- Horizontal Pod Autoscaler (HPA) monitors CPU utilization
- When utilization exceeds 60%, new replicas are provisioned
- Load is distributed across pods via Kubernetes Service

This enables dynamic scaling based on real-time workload.

---

### 6. Resource Governance

Each service defines:

- CPU requests
- CPU limits
- Memory requests
- Memory limits

This ensures:

- Fair scheduling
- Controlled resource allocation
- Predictable scaling behavior
- Prevention of noisy neighbor issues

Resource governance is critical for realistic production simulation.

---

### 7. Failure Isolation

Microservices are isolated by deployment.

If one service fails:

- Other services remain operational
- Kubernetes restarts failed pods automatically
- Readiness and liveness probes (if enabled) ensure traffic only reaches healthy pods

This improves system resilience compared to a monolithic design.

---

### 8. Authentication and Security

Authentication is handled at the API Gateway layer using JWT.

- Login endpoint issues time-bound tokens
- Protected routes require Bearer tokens
- Retrieval endpoint is not publicly accessible

This ensures:
- Controlled access
- Clear security boundary
- Separation of concerns

---

### 9. Bottlenecks and Limitations

Current limitations include:

- Local FAISS index limits distributed vector scaling
- LLM inference is CPU-bound
- No caching layer for repeated queries
- No distributed queue for ingestion

Future improvements may include:

- Redis-based response caching
- Distributed vector database
- GPU-backed inference
- Rate limiting at gateway
- Ingress controller for production routing

---

### 10. Design Trade-offs

Chosen Approach:
- Simple microservices + PVC + HPA

Alternatives:
- Monolithic RAG service (simpler but less scalable)
- Managed vector DB (simpler but less educational)
- Serverless architecture (more abstracted)

This design prioritizes learning distributed systems concepts over production simplification.

---

### 11. Production Extensions

To evolve this system toward production scale:

- Replace FAISS with distributed vector DB
- Introduce message queue for ingestion
- Add Prometheus + Grafana monitoring
- Add centralized logging (ELK stack)
- Implement CI/CD for automated deployments
- Add multi-user isolation and experiment tracking per user

---

### 12. Why Kubernetes Was Used

Kubernetes enables:

- Declarative infrastructure
- Self-healing pods
- Horizontal scaling
- Resource governance
- Service discovery
- Realistic distributed deployment

Using Kubernetes transforms this from a prototype into a platform-oriented system.

---

## Application + Infrastructure Proof

### Login-
Credentials-
- Username- admin
- Password- admin

<img width="1667" height="881" alt="Screenshot 2026-02-22 at 3 20 14 PM" src="https://github.com/user-attachments/assets/439d10db-174c-4afd-91ab-5d66428b404d" />


### Dashboard (Query + Retrieved Context + Charts)-
- Successfull file upload
<img width="1667" height="881" alt="Screenshot 2026-02-22 at 3 22 03 PM" src="https://github.com/user-attachments/assets/dd57201e-d9b5-4cab-9773-4277d31410bf" />

- Asking a question
<img width="1667" height="881" alt="Screenshot 2026-02-22 at 3 23 17 PM" src="https://github.com/user-attachments/assets/7a1f2dec-7958-4093-a84d-d46480d5857d" />

- Results
<img width="1667" height="881" alt="image" src="https://github.com/user-attachments/assets/43c78ad3-749c-493f-9519-ea14f1d8e835" />

<img width="1667" height="881" alt="image" src="https://github.com/user-attachments/assets/8822e28b-494e-481c-b4c2-e4106fa471e6" />

### Services-
<img width="1667" height="881" alt="Screenshot 2026-02-22 at 4 45 41 PM" src="https://github.com/user-attachments/assets/c634860c-45e1-453a-85f9-995205699aca" />

### Kubernetes Deployment Evidence: Running Pods- 
<img width="1247" height="223" alt="image" src="https://github.com/user-attachments/assets/429d251d-6826-4b8d-8d62-9e592dfe975a" />

### Horizontal Pod Autoscaler-
<img width="1246" height="442" alt="image" src="https://github.com/user-attachments/assets/2bdda216-4f75-4b03-a739-f022e4f416ba" />


### Resource Metrics-
<img width="1021" height="161" alt="image" src="https://github.com/user-attachments/assets/247325c7-f0b9-4386-b785-6d2fba1e6426" />

<img width="1016" height="99" alt="image" src="https://github.com/user-attachments/assets/0d11f57b-e5ea-423c-a85a-33d0093134b3" />



## Summary

This project demonstrates:

- Distributed microservice design
- Retrieval-Augmented Generation infrastructure
- Vector search integration
- LLM orchestration
- Kubernetes deployment
- Horizontal autoscaling
- Resource management
- Authentication and security boundaries
- System-level performance considerations

It is designed to reflect production-grade system architecture rather than a single-process RAG prototype.

---

## Key Features

- Distributed RAG microservices architecture
- FAISS-based vector indexing
- Local LLM inference (FLAN-T5)
- JWT-secured API gateway
- Experiment tracking and filtering
- Latency comparison dashboard
- Persistent storage via Kubernetes PVC
- Resource requests and limits
- CPU-based Horizontal Pod Autoscaler
- Dynamic scaling under query load
- Kubernetes-based service discovery

---

## Autoscaling Configuration

The Retrieval Service is horizontally autoscaled using Kubernetes HPA:

- Minimum replicas: 1
- Maximum replicas: 4
- Target CPU utilization: 60%

When CPU usage exceeds the defined threshold, Kubernetes dynamically provisions additional retrieval pods.

Example scaling behavior:

```
retrieval-service-xxxxx
retrieval-service-yyyyy
retrieval-service-zzzzz
```

Below is a screenshot for the same-

---

## Resource Governance

Each service defines:

- CPU requests
- CPU limits
- Memory requests
- Memory limits

This ensures controlled resource allocation and production-grade scheduling behavior within the cluster.

---

## Local Development (Docker Compose)

Build and run all services locally:

```bash
docker-compose up --build
```

Frontend:
```
http://localhost:3000
```

API Gateway:
```
http://localhost:8000
```

---

## Kubernetes Deployment (kind)

### 1. Create Cluster

```bash
kind create cluster --name rag-cluster
```

### 2. Build Images

```bash
docker-compose build
```

### 3. Load Images into kind

```bash
kind load docker-image distributed-rag-platform-api-gateway --name rag-cluster
kind load docker-image distributed-rag-platform-ingestion-service --name rag-cluster
kind load docker-image distributed-rag-platform-retrieval-service --name rag-cluster
kind load docker-image distributed-rag-platform-evaluation-service --name rag-cluster
kind load docker-image distributed-rag-platform-frontend --name rag-cluster
```

### 4. Deploy Kubernetes Resources

```bash
kubectl apply -f k8s/
```

### 5. Port Forward (kind networking)

```bash
kubectl port-forward service/api-gateway 8000:8000 -n rag-system
kubectl port-forward service/frontend 3000:3000 -n rag-system
```

Access:

Frontend:
```
http://localhost:3000
```

API Gateway:
```
http://localhost:8000
```

---

## Observability and Metrics

Install Metrics Server:

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

Verify CPU metrics:

```bash
kubectl top pods -n rag-system
```

Check autoscaling behavior:

```bash
kubectl get hpa -n rag-system
```

---

## Project Structure

```
distributed-rag-platform/
│
├── api-gateway/
├── ingestion-service/
├── retrieval-service/
├── evaluation-service/
├── frontend/
├── k8s/
├── docker-compose.yml
└── README.md
```

---

## Future Improvements

- Ingress controller instead of NodePort
- Redis caching layer
- Advanced retrieval metrics (Precision@k, Recall@k)
- CI/CD pipeline for automated image builds
- Prometheus and Grafana integration
- Multi-user experiment isolation
- Load testing benchmarks

---

## Technical Highlights

- Distributed system design
- Microservices architecture
- Vector search infrastructure
- LLM inference pipeline
- Kubernetes resource management
- Horizontal scaling under load
- JWT-based authentication
- Production-style deployment patterns

---
