
CREATE TABLE IF NOT EXISTS check_output (
        id SERIAL PRIMARY KEY,
        check_time TIMESTAMP NOT NULL,
        result TEXT NOT NULL,
        details TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS check_output_log (
        id SERIAL PRIMARY KEY,
        output_type VARCHAR(100) NOT NULL,
        result TEXT NOT NULL,
        state_time TIMESTAMP NOT NULL
);
