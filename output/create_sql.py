import psycopg2
from datetime import datetime, timedelta

# 数据库连接参数
conn_params = {
    "host":"pg-postgresql",
    "port":"5432",
    "database":"postgres",
    "user":"postgres",
    "password":"7PIug1Lk3O"
}

print("connected")
# 创建监测表
def create_monitoring_table():
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS monitor_table.monitoring_data_2 (
        id SERIAL PRIMARY KEY,
        request_type VARCHAR(20) NOT NULL,
        request_content TEXT NOT NULL,
        judgement_result VARCHAR(10) NOT NULL,
        query_time TIMESTAMP NOT NULL
    );
    '''
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    cur.execute(create_table_query)
    conn.commit()
    cur.close()
    conn.close()

# 插入样本数据
def insert_sample_data():
    sample_data = [
        ("url", "https://example.com", "ok", datetime.now()),
        ("path", "F:\week1\StreamlitCheckApp-main\test.py", "response", datetime.now()),
        ("sql", "SELECT * FROM users", "ok", datetime.now())
    ]
    insert_query = '''
    INSERT INTO monitor_table.monitoring_data_2 (request_type, request_content, judgement_result, query_time)
    VALUES (%s, %s, %s, %s);
    '''
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    cur.executemany(insert_query, sample_data)
    conn.commit()
    cur.close()
    conn.close()

# 创建分区表
def create_partition_table():
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()

    create_partition_query = '''
    CREATE TABLE IF NOT EXISTS monitor_table.monitoring_data_partition (
        id SERIAL PRIMARY KEY,
        request_type VARCHAR(20) NOT NULL,
        request_content TEXT NOT NULL,
        judgement_result VARCHAR(10) NOT NULL,
        query_time TIMESTAMP NOT NULL
    ) PARTITION BY RANGE (query_time);
    '''
    cur.execute(create_partition_query)
    conn.commit()

    start_date = datetime(2023, 6, 1)
    end_date = datetime(2024, 6, 30)

    while start_date <= end_date:
        partition_name = "monitoring_data_" + start_date.strftime("%Y%m%d")
        partition_date = start_date.strftime("%Y-%m-%d")
        
        create_partition_table_query = f'''
        CREATE TABLE IF NOT EXISTS monitor_table.{partition_name}
        PARTITION OF monitor_table.monitoring_data_partition
        FOR VALUES FROM ('{partition_date}') TO ('{partition_date}'::date + interval '1 day');
        '''
        cur.execute(create_partition_table_query)
        conn.commit()

        start_date += timedelta(days=1)

    cur.close()
    conn.close()
# 执行创建表和插入数据的操作
create_monitoring_table()
print("created monitor table")
insert_sample_data()
print("inserted example datas")
create_partition_table()
print("created partition table")