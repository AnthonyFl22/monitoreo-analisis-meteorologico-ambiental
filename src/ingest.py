#!/usr/bin/env python3
import argparse
import os
import logging
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

def build_db_url():
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    db   = os.getenv("PGDATABASE", "monitoreo")
    user = os.getenv("PGUSER", "monit_user")
    pwd  = os.getenv("PGPASSWORD", "")
    ssl  = os.getenv("PGSSLMODE", "")
    dsn = f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"
    if ssl:
        dsn += f"?sslmode={ssl}"
    return dsn

def read_toa5(path: str) -> pd.DataFrame:
    """Lee archivos TOA5 (.dat/.txt) y devuelve DataFrame limpio"""
    df = pd.read_csv(
        path,
        header=1,            # usa la fila 1 como cabecera
        skiprows=[2, 3],     # salta unidades y tipos
        na_values=["NAN"],   # convierte "NAN" en NaN
        quotechar='"'
    )

    # Normalizar nombres de columnas
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(r"[^0-9a-zA-Z]+", "_", regex=True)
        .str.strip("_")
        .str.lower()
    )

    # Parsear timestamps
    df["timestamp_utc"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)

    # Reemplazar centinelas ±7999 por NaN
    for col in ["v_ig_avg", "ig_avg"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df.loc[df[col].abs() >= 7999, col] = pd.NA

    # Columnas que nos interesan
    keep = ["timestamp_utc", "record", "batt_volt_min", "ptemp", "azimutal", "zenith", "v_ig_avg", "ig_avg"]
    return df[keep]

def ingest_file(engine, path: str):
    df = read_toa5(path)
    if df.empty:
        logging.warning("Archivo %s sin filas válidas", path)
        return 0

    # Insertar en la tabla (ON CONFLICT DO NOTHING evita duplicados)
    inserted = 0
    with engine.begin() as conn:
        for _, row in df.iterrows():
            conn.execute(
                text("""
                    INSERT INTO radiacion (timestamp_utc, record, batt_volt_min, ptemp, azimutal, zenith, v_ig_avg, ig_avg)
                    VALUES (:t, :r, :bv, :pt, :az, :ze, :vig, :ig)
                    ON CONFLICT (timestamp_utc) DO NOTHING;
                """),
                {
                    "t": row["timestamp_utc"],
                    "r": row["record"],
                    "bv": row["batt_volt_min"],
                    "pt": row["ptemp"],
                    "az": row["azimutal"],
                    "ze": row["zenith"],
                    "vig": row["v_ig_avg"],
                    "ig": row["ig_avg"],
                }
            )
            inserted += 1
    logging.info("Archivo %s → %d registros procesados", path, inserted)
    return inserted

def main():
    print(">>> Iniciando ingest.py")
    parser = argparse.ArgumentParser(description="Ingesta de archivos TOA5 (.dat/.txt) en PostgreSQL")
    parser.add_argument("files", nargs="+", help="Rutas a los archivos")
    args = parser.parse_args()

    load_dotenv()
    engine = create_engine(build_db_url(), future=True)

    total = 0
    for f in args.files:
        if not os.path.exists(f):
            logging.error("No existe el archivo: %s", f)
            continue
        total += ingest_file(engine, f)
    logging.info("TOTAL → %d registros procesados", total)

if __name__ == "__main__":
    main()
