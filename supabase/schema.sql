-- FlyFree Database Schema
-- Run this in Supabase SQL Editor

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Airports reference table
CREATE TABLE airports (
    iata_code CHAR(3) PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT,
    latitude NUMERIC(9,6),
    longitude NUMERIC(9,6)
);

-- Flights table
CREATE TABLE flights (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    origin CHAR(3) NOT NULL REFERENCES airports(iata_code),
    destination CHAR(3) NOT NULL REFERENCES airports(iata_code),
    airline_code CHAR(2) NOT NULL,
    airline_name TEXT,
    flight_number TEXT,
    departure_time TIMESTAMPTZ NOT NULL,
    arrival_time TIMESTAMPTZ NOT NULL,
    price_myr NUMERIC(8,2) NOT NULL,
    price_original_currency CHAR(3),
    price_original_amount NUMERIC(8,2),
    booking_url TEXT,
    source_api TEXT NOT NULL DEFAULT 'amadeus',
    flight_date DATE NOT NULL,
    fetch_batch_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (flight_number, flight_date, origin, destination, price_myr)
);

-- Indexes for common queries
CREATE INDEX idx_flights_origin ON flights(origin);
CREATE INDEX idx_flights_destination ON flights(destination);
CREATE INDEX idx_flights_date ON flights(flight_date);
CREATE INDEX idx_flights_price ON flights(price_myr);
CREATE INDEX idx_flights_origin_dest_date ON flights(origin, destination, flight_date);
CREATE INDEX idx_flights_created_at ON flights(created_at);

-- Fetch runs log
CREATE TABLE fetch_runs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'running',
    routes_fetched INTEGER DEFAULT 0,
    flights_found INTEGER DEFAULT 0,
    errors TEXT[],
    api_calls_used INTEGER DEFAULT 0
);

-- View: cheapest current flights (one per route/date)
CREATE OR REPLACE VIEW cheapest_flights AS
SELECT DISTINCT ON (origin, destination, flight_date)
    id, origin, destination, airline_code, airline_name, flight_number,
    departure_time, arrival_time, price_myr, booking_url, flight_date, created_at
FROM flights
WHERE created_at > NOW() - INTERVAL '24 hours'
ORDER BY origin, destination, flight_date, price_myr ASC;

-- Row Level Security
ALTER TABLE flights ENABLE ROW LEVEL SECURITY;
ALTER TABLE airports ENABLE ROW LEVEL SECURITY;
ALTER TABLE fetch_runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read flights" ON flights FOR SELECT USING (true);
CREATE POLICY "Public read airports" ON airports FOR SELECT USING (true);
CREATE POLICY "Public read fetch_runs" ON fetch_runs FOR SELECT USING (true);
