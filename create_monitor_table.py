"""
create monitor table:Test_monitortable_test2 with 5 column
{id->As an identifier
request_type->Three options(URL,PATH,SQL)
request_content->To store the content of those three types of options listed ahead
judgement_result->To store the judgement of the  result after executing the rule component code
query_time->The time when the query happened}
already create the monitor table in pg database partitioned by day from 2023/06/01 to 2023/07/30
the name of the partition table is Test2_monitortable_{date}
it is an empty table now, execute_code_from_rule.py will execute the code from rule component and insert data into the monitor table
"""
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
def create_partitioned_monitoring_table():
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS Test_monitortable_test2 (
        id SERIAL,
        request_type VARCHAR(20) NOT NULL,
        request_content TEXT NOT NULL,
        judgement_result VARCHAR(3) NOT NULL,
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
def create_daily_partition_table(start_date, end_date):
    current_date = start_date
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    while current_date <= end_date:
        partition_table_query = '''
        CREATE TABLE IF NOT EXISTS Test2_monitortable_{date} PARTITION OF Test_monitortable_test2
        FOR VALUES FROM ('{date} 00:00:00') TO ('{date} 23:59:59');
        '''
        cur.execute(partition_table_query.format(date=current_date.strftime("%Y_%m_%d")))
        current_date += timedelta(days=1)
    conn.commit()
    cur.close()
    conn.close()



# 执行创建表和插入数据的操作
create_partitioned_monitoring_table()
start_date = datetime(2023, 6, 1).date()
end_date = datetime(2023, 7, 30).date()
create_daily_partition_table(start_date, end_date)
