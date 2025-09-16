# Monitoreo y análisis meteorológico-ambiental

Este proyecto busca **guardar y organizar los datos de radiación solar** que se guardan en paneles solares ubicados en el Estado de México. 
La finalidad de este proyecto es:
- Diseño de una base de datos. 
- Conformación de la base de datos.
- Matenimiento de la base de datos. 
- Extracción de datos para su análisis.

En vez de manejar archivos `.dat` o `.txt` manualmente, aquí se centraliza todo en una **base de datos PostgreSQL** que:
- Evita duplicados.
- Permite consultas rápidas (ej. fechas mínimas y máximas, promedios).
- Facilita que cualquier persona (aunque no sepa de programación) pueda acceder a los datos.

---

## 📂 Estructura del repositorio

```
monitoreo-analisis-meteorologico-ambiental/
├── data/                 # Aquí van los archivos .dat o .txt del sensor
├── src/                  # Código fuente
│   ├── init_db.py        # Crea usuario, base y tabla en PostgreSQL
│   ├── ingest.py         # Carga archivos a la tabla (sin duplicar)
│   ├── check_dates.py    # Verifica fechas mínimas, máximas y total de registros
│   └── db_init.sql       # Script SQL con definición de la tabla
├── .env.example          # Variables de conexión (copiar a .env)
├── requirements.txt      # Librerías necesarias de Python
└── README.md             # Este archivo (guía general)
```

---

##  Cómo usarlo (resumen)

### 1. Instalar requisitos
- **PostgreSQL 17** (con pgAdmin).  
- **Python 3.10+**.

### 2. Clonar este repo
```bash
git clone https://github.com/<usuario>/monitoreo-analisis-meteorologico-ambiental.git
cd monitoreo-analisis-meteorologico-ambiental
```

### 3. Crear entorno Python
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 4. Configurar credenciales
Copiar `.env.example` a `.env` y rellenar con tu contraseña de PostgreSQL.

### 5. Crear base y tabla
```powershell
python src/init_db.py
```

Esto hace 3 cosas automáticamente:
1. Crea el usuario de aplicación.  
2. Crea la base `monitoreo`.  
3. Crea la tabla `radiacion`.  

### 6. Cargar archivos
Ejemplo:
```powershell
python src/ingest.py data\CR310Series_Radiacion.dat
python src/ingest.py data\CR310Series_Radiacion.txt
```

 Puedes cargar varios archivos a la vez:
```powershell
python src/ingest.py data\*.dat data\*.txt
```

### 7. Revisar estado de la tabla
```powershell
python src/check_dates.py
```

Esto imprime:
- Fecha mínima.  
- Fecha máxima.  
- Total de registros.  


---

## 📖 Más detalles técnicos
Consulta el archivo [`src/README.md`](src/README.md).
