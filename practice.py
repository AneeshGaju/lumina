from fastapi import FastAPI #importting fastAPI library
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI() #creating server application
@app.get("/plans")
def get_plans():
    conn = get_db():
    cursor = conn.cursor(cursor_factory = RealDictCursor)