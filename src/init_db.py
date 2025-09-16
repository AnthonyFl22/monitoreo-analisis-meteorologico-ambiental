#!/usr/bin/env python3
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

# -----------------------------
# Helpers para construir DSNs
# -----------------------------
def build_admin_url():
    host = os.getenv("PGADMIN_HOST", "localhost")
    port = os.getenv("PGADMIN_PORT", "5432")
    db   = os.getenv("PGADMIN_DB", "postgres")
    user = os.getenv("PGADMIN_USER", "postgres")
    pwd  = os.getenv("PGADMIN_PASSWORD", "")
    ssl  = os.getenv("PGSSLMODE", "")  # opcional
    dsn = f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"
    if ssl:
        dsn += f"?sslmode={ssl}"
    return dsn

def build_app_url():
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    db   = os.getenv("PGDATABASE", "monitoreo")
    user = os.getenv("PGUSER", "monit_user")
    pwd  = os.getenv("PGPASSWORD", "")
    ssl  = os.getenv("PGSSLMODE", "")  # opcional
    dsn = f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"
    if ssl:
        dsn += f"?sslmode={ssl}"
    return dsn

# -----------------------------
# Funciones de provisión
# -----------------------------
def ensure_role(engine_admin, role_name: str, role_password: str):
    with engine_admin.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_roles WHERE rolname = :r"),
            {"r": role_name}
        ).first()
        if exists:
            logging.info("Rol '%s' ya existe. OK.", role_name)
        else:
            logging.info("Creando rol '%s'...", role_name)
            conn.execute(text(f"CREATE ROLE {role_name} WITH LOGIN PASSWORD :p NOSUPERUSER NOCREATEDB NOCREATEROLE"),
                         {"p": role_password})
            conn.commit()
            logging.info("Rol creado.")

def ensure_database(engine_admin, db_name: str, owner: str):
    # CREATE DATABASE no puede ejecutarse dentro de transacción -> AUTOCOMMIT
    with engine_admin.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :d"),
            {"d": db_name}
        ).first()
        if exists:
            logging.info("Base de datos '%s' ya existe. OK.", db_name)
        else:
            logging.info("Creando base de datos '%s' (owner: %s)...", db_name, owner)
            conn.exec_driver_sql(f"CREATE DATABASE {db_name} OWNER {owner}")
            logging.info("Base de datos creada.")

def run_sql_file(engine_app, sql_path: Path):
    sql_text = sql_path.read_text(encoding="utf-8")
    with engine_app.connect() as conn:
        # Ejecuta todo el archivo (puede tener varios statements)
        conn.exec_driver_sql(sql_text)
        conn.commit()
    logging.info("Esquema aplicado desde %s", sql_path)

# -----------------------------
# Main
# -----------------------------
def main():
    load_dotenv()  # lee .env
    # Variables de app
    app_db     = os.getenv("PGDATABASE", "monitoreo")
    app_user   = os.getenv("PGUSER", "monit_user")
    app_pass   = os.getenv("PGPASSWORD", "")

    # 1) Conectar como ADMIN
    admin_url = build_admin_url()
    engine_admin = create_engine(admin_url, future=True)
    logging.info("Conectado como ADMIN a: %s", admin_url.rsplit("@", 1)[-1])

    # 2) Crear rol de aplicación si no existe
    ensure_role(engine_admin, app_user, app_pass)

    # 3) Crear base de datos si no existe (dueño: rol de aplicación)
    ensure_database(engine_admin, app_db, app_user)

    # 4) Conectar como APLICACIÓN a la base nueva
    app_url = build_app_url()
    engine_app = create_engine(app_url, future=True)
    logging.info("Conectado como APP a: %s", app_url.rsplit("@", 1)[-1])

    # 5) Ejecutar SQL de esquema
    sql_path = Path(__file__).parent / "db_init.sql"
    if not sql_path.exists():
        logging.error("No se encontró %s", sql_path)
        sys.exit(1)
    run_sql_file(engine_app, sql_path)

    logging.info("✅ Listo: rol, base y tabla(s) creadas.")

if __name__ == "__main__":
    sys.exit(main())
