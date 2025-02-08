-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Create tables first
CREATE TABLE IF NOT EXISTS battery_instances (
    id SERIAL PRIMARY KEY,
    battery_type VARCHAR NOT NULL,
    model_name VARCHAR NOT NULL,
    capacity FLOAT NOT NULL,
    max_charge_rate FLOAT,
    max_discharge_rate FLOAT,
    manufactured_date VARCHAR,
    installation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS battery_metrics (
    time TIMESTAMP NOT NULL,
    battery_id INTEGER NOT NULL,
    current_charge FLOAT DEFAULT 0.0,
    voltage FLOAT,
    temperature FLOAT,
    cycle_count INTEGER,
    health FLOAT,
    status VARCHAR,
    last_eoc TIMESTAMP,
    next_eoc TIMESTAMP
);

-- Create hypertables after tables are created
CREATE OR REPLACE FUNCTION create_hypertable_if_not_exists() 
RETURNS void AS $$
BEGIN
    PERFORM create_hypertable('battery_metrics', 'time', 
        if_not_exists => TRUE,
        chunk_time_interval => INTERVAL '1 day'
    );
END;
$$ LANGUAGE plpgsql;

-- Execute after tables are created
SELECT create_hypertable_if_not_exists();

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_battery_metrics_battery_id 
    ON battery_metrics(battery_id);

CREATE INDEX IF NOT EXISTS idx_battery_metrics_time_battery_id 
    ON battery_metrics(time DESC, battery_id);

-- Add foreign key constraint
ALTER TABLE battery_metrics 
    ADD CONSTRAINT fk_battery_metrics_instance 
    FOREIGN KEY (battery_id) 
    REFERENCES battery_instances(id);