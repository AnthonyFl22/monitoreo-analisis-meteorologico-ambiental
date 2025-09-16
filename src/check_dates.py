#!/usr/bin/env python3
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def build_db_url():
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    db   = os.getenv("PGDATABASE", "monitoreo")
    user = os.getenv("PGUSER", "monit_user")
    pwd  = os.getenv("PGPASSWORD", "")
    return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"

def main():
    load_dotenv()
    engine = create_engine(build_db_url(), future=True)

    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                MIN(timestamp_utc) AS fecha_minima,
                MAX(timestamp_utc) AS fecha_maxima,
                COUNT(*) AS total_registros
            FROM radiacion;
        """))
        row = result.fetchone()
        print("📊 Estado de la tabla radiacion")
        print("-------------------------------")
        print("Fecha mínima: ", row.fecha_minima)
        print("Fecha máxima: ", row.fecha_maxima)
        print("Total de registros: ", row.total_registros)

if __name__ == "__main__":
    main()
