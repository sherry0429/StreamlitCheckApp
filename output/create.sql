
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

CREATE TABLE IF NOT EXISTS users_table (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) NOT NULL,
        passwd VARCHAR(100) NOT NULL,
        cookie VARCHAR(100) NOT NULL        
);

CREATE TABLE IF NOT EXISTS users_status (
        id SERIAL PRIMARY KEY,
        check_type VARCHAR(100) NOT NULL,
        cookie VARCHAR(100) NOT NULL,
        state_time TIMESTAMP NOT NULL
);

-- 登录
-- psql -h pg-postgresql -p 5432 -U postgres
-- 7PIug1Lk3O
-- 清空表
-- TRUNCATE TABLE check_output RESTART IDENTITY;

-- TRUNCATE TABLE check_output_log RESTART IDENTITY;