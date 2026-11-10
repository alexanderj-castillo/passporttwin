ALTER TABLE instrument_unit
    ADD COLUMN IF NOT EXISTS technical_name TEXT,
    ADD COLUMN IF NOT EXISTS plant_tag TEXT;
