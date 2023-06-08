"""
this code is to read the table created from rule component. The table goes:
 CREATE TABLE IF NOT EXISTS t_check_role_code (
        id SERIAL PRIMARY KEY,
        role_id INTEGER REFERENCES t_check_roles (id),
        code_block TEXT,
        create_time TIMESTAMP DEFAULT NOW(),
        enable BOOLEAN,
        start_time TIMESTAMP,
        end_time TIMESTAMP
    );
We traverse the entire table and execute the python code or lua code in code_block if the conditions are met,and we insert the data into monitor table. Repeat the traversal.

"""
import psycopg2
import datetime

# 数据库连接参数
conn_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '7PIug1Lk3O',
    'host': 'pg-postgresql',
    'port': '5432',
    'sslmode': 'disable',
}

# 遍历搜索并执行代码块
def execute_code_blocks():
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()

    # 查询满足条件的记录
    select_query = '''
    SELECT *
    FROM t_check_role_code
    WHERE enable = TRUE AND start_time <= NOW() AND end_time >= NOW();
    '''
    cur.execute(select_query)
    rows = cur.fetchall()

    # 执行代码块
    for row in rows:
        id, role_id, code_block, create_time, enable, start_time, end_time = row
        try:
            result = eval(code_block)
            monitoring_result = {
                "request_type": role_id,
                "request_content": code_block,
                "judgement_result": result,
                "query_time": datetime.datetime.now()
            }
            insert_monitoring_result(monitoring_result)
        except Exception as e:
            print(f"Error executing code block with id {id}: {str(e)}")

    cur.close()
    conn.close()

def insert_monitoring_result(monitoring_result):
    # 建立数据库连接
    conn = psycopg2.connect(**conn_params)

    # 创建一个游标对象
    cur = conn.cursor()

    # 使用参数绑定插入监测结果，防止sql注入
    query = """
    INSERT INTO monitoring_table (id, role_id, code_block, create_time, enable, start_time, end_time, result, query_time)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """

    cur.execute(query, (monitoring_result['id'], monitoring_result['role_id'], monitoring_result['code_block'], monitoring_result['create_time'], monitoring_result['enable'], monitoring_result['start_time'], monitoring_result['end_time'], monitoring_result['result'], monitoring_result['query_time']))

    # 提交事务
    conn.commit()

    # 关闭游标和数据库连接
    cur.close()
    conn.close()

# 持续执行搜索和执行代码块的操作
while True:
    execute_code_blocks()
