-- Crea tabla de mediciones de radiación

CREATE TABLE IF NOT EXISTS radiacion (
    timestamp_utc TIMESTAMPTZ PRIMARY KEY,
    record INTEGER,
    batt_volt_min DOUBLE PRECISION,
    ptemp DOUBLE PRECISION,
    azimutal DOUBLE PRECISION,
    zenith DOUBLE PRECISION,
    v_ig_avg DOUBLE PRECISION,
    ig_avg DOUBLE PRECISION
);

COMMENT ON TABLE radiacion IS 'Mediciones de radiación (UTC) desde archivos TOA5';
COMMENT ON COLUMN radiacion.timestamp_utc IS 'Marca de tiempo (UTC)';


