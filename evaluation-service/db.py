import sqlite3
import os
from datetime import datetime

DB_PATH = "/shared-data/metrics.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS experiments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT,
        chunk_size INTEGER,
        top_k INTEGER,
        retrieval_latency REAL,
        generation_latency REAL,
        total_latency REAL,
        context_length INTEGER,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

def log_experiment(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO experiments (
        query,
        chunk_size,
        top_k,
        retrieval_latency,
        generation_latency,
        total_latency,
        context_length,
        timestamp
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["query"],
        data["chunk_size"],
        data["top_k"],
        data["retrieval_latency"],
        data["generation_latency"],
        data["total_latency"],
        data["context_length"],
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()

def fetch_all():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM experiments")
    rows = cursor.fetchall()

    conn.close()
    return rows

def compare_configs(chunk_size=None, top_k=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT chunk_size, top_k, AVG(total_latency) FROM experiments WHERE 1=1"
    params = []

    if chunk_size:
        query += " AND chunk_size=?"
        params.append(chunk_size)

    if top_k:
        query += " AND top_k=?"
        params.append(top_k)

    query += " GROUP BY chunk_size, top_k"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    conn.close()
    return rows