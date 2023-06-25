import psycopg2
from datetime import datetime, timedelta

# 数据库连接参数
conn_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '7PIug1Lk3O',
    'host': 'pg-postgresql',
    'port': '5432',
    'sslmode': 'disable',
}


# 创建分区监测表
def create_partitioned_monitoringtable():
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS File_monitortable_test2 (
        id SERIAL,
        problem_type VARCHAR(20) NOT NULL,
        problem_content TEXT NOT NULL,
        query_time TIMESTAMP NOT NULL,
        PRIMARY KEY (id, query_time)
    ) PARTITION BY RANGE (query_time);
    '''
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    cur.execute(create_table_query)
    conn.commit()
    cur.close()
    conn.close()

# 创建每日分区表
def create_daily_partitiontable(start_date, end_date):
    current_date = start_date
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    while current_date <= end_date:
        partition_table_query = '''
        CREATE TABLE IF NOT EXISTS File_monitortable_{date} PARTITION OF File_monitortable_test2
        FOR VALUES FROM ('{date} 00:00:00') TO ('{date} 23:59:59');
        '''
        cur.execute(partition_table_query.format(date=current_date.strftime("%Y_%m_%d")))
        current_date += timedelta(days=1)
    conn.commit()
    cur.close()
    conn.close()



# 执行创建表和插入数据的操作
create_partitioned_monitoringtable()
start_date = datetime(2023, 6, 20).date()
end_date = datetime(2023, 7, 30).date()
create_daily_partitiontable(start_date, end_date)
