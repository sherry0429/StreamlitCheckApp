import psycopg2



# def connect_to_pg():
#     connection = psycopg2.connect(
#         host="121.40.100.184",
#         port="5432",
#         database="postgres",
#         user="postgres",
#         password="7PIug1Lk3O"
#     )
#     return connection

conn_params = {
    "host": "pg-postgresql",
    "port": "5432",
    "database": "postgres",
    "user": "postgres",
    "password": "7PIug1Lk3O",
    "sslmode":"disable"
}

def create_table_t_check_roles():
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS t_check_roles (
        id SERIAL PRIMARY KEY,
        code TEXT NOT NULL,
        create_time TIMESTAMP NOT NULL,
        enable BOOLEAN
    );
    '''
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    cur.execute(create_table_query)
    conn.commit()
    cur.close()
    conn.close()

# 执行创建表的操作
create_table_t_check_roles()


# def main():
#     connection = connect_to_pg()
#     cursor = connection.cursor()
#     sql = "select *"
#     cursor.execute(sql)
#     rows = cursor.fetchall()
#     for row in rows:
#         print(row)
#     cursor.close()
#     connection.close()

#if __name__ == "__main__":
#    main()


def create_table_t_check_role_code():
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS t_check_role_code (
        id SERIAL PRIMARY KEY,
        role_id INTEGER REFERENCES t_check_roles (id),
        code_block TEXT,
        create_time TIMESTAMP DEFAULT NOW(),
        enable BOOLEAN,
        start_time TIMESTAMP,
        end_time TIMESTAMP
    );
    '''
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    cur.execute(create_table_query)
    conn.commit()
    cur.close()
    conn.close()

# 执行创建表的操作
create_table_t_check_role_code()