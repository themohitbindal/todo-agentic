"""App settings, read from environment variables (or backend/.env)."""

import os

from dotenv import load_dotenv

# Reads backend/.env into os.environ (does nothing if the file is missing).
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://todo_user:todo_pass@localhost:5432/todo_db",
)

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
]
