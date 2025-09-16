# Detalles técnicos (src)

Este directorio contiene el código fuente del proyecto.  

---

## 📂 Archivos

### `init_db.py`
- Crea un rol (`monit_user`), la base de datos (`monitoreo`) y la tabla `radiacion`.
- Se conecta primero con el usuario administrador (`postgres`) usando las credenciales del `.env`.
- Luego aplica el esquema definido en `db_init.sql`.

### `db_init.sql`
- Define la tabla `radiacion` con estas columnas principales:
  - `timestamp_utc` (clave primaria, tipo `TIMESTAMPTZ`)
  - `record`
  - `batt_volt_min`
  - `ptemp`
  - `azimutal`
  - `zenith`
  - `v_ig_avg`
  - `ig_avg`
- Incluye comentarios e índices para optimizar consultas.

### `ingest.py`
- Lee archivos `.dat` o `.txt` en formato **TOA5** (propio de Campbell Scientific).
- Limpia valores no válidos (`NAN`, ±7999).
- Convierte la columna `TIMESTAMP` a UTC.
- Inserta los datos en la tabla `radiacion`, **evitando duplicados** (`ON CONFLICT DO NOTHING`).

### `check_dates.py`
- Ejecuta una consulta para mostrar:
  - Fecha mínima (`MIN(timestamp_utc)`).
  - Fecha máxima (`MAX(timestamp_utc)`).
  - Total de registros (`COUNT(*)`).

---

##  Variables de entorno

El archivo `.env` (a partir de `.env.example`) debe contener:

```env
PGHOST=localhost
PGPORT=5432
PGDATABASE=monitoreo
PGUSER=monit_user
PGPASSWORD=cambia-esta-contraseña
```

**IMPORTANTE:**  Cambiar `PGPASSWORD` por la contraseña real configurada en `init_db.py`.

---

##  Consultas de ejemplo

### Contar registros
```sql
SELECT COUNT(*) FROM radiacion;
```

### Obtener rango de fechas
```sql
SELECT MIN(timestamp_utc), MAX(timestamp_utc) FROM radiacion;
```

### Promedio diario de irradiancia
```sql
SELECT date(timestamp_utc) AS dia, AVG(ig_avg) AS irradiancia_promedio
FROM radiacion
GROUP BY dia
ORDER BY dia;
```

---

## ⚙ Flujo típico

1. `python src/init_db.py` → prepara la base.  
2. `python src/ingest.py data\archivo.dat` → carga los datos.  
3. `python src/check_dates.py` → valida fechas y cantidad de registros.  
