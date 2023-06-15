"""
This code is to read the table created from the rule component. This table is
 CREATE TABLE IF NOT EXISTS t_check_role_code (
        id SERIAL PRIMARY KEY,
        role_id INTEGER REFERENCES t_check_roles (id),
        code_block TEXT, create_time
        create_time TIMESTAMP DEFAULT NOW(), enable
        enable BOOLEAN, start_time
        start_time TIMESTAMP, end_time TIMESTAMP
        end_time TIMESTAMP
    ).
This is the basic complete flow of the monitoring component.
First we iterate through the table of rule components and use enable and start_time and end_time as criteria.
The code in the code_block is read, executed and the result is obtained if the condition is met.
Then we write all kinds of required information together with the results into the test table Test_monitortable_test2 created by our component with day partition.

"""
import psycopg2
import datetime
import time
import re

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
            pattern = r'def (\w+)\s*\(\):'  # 使用正则表达式模式匹配函数定义
            match = re.search(pattern, code_block)
            if match:
                function_name = match.group(1)  # 获取函数名
            exec(code_block)
            result = eval(f"{function_name}()")
            #print(result)
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
    INSERT INTO Test_monitortable_test2 (request_type,request_content,judgement_result,query_time)
    VALUES ( %s, %s, %s, %s);
    """

    cur.execute(query, (monitoring_result['request_type'], monitoring_result['request_content'],  monitoring_result['judgement_result'],  monitoring_result['query_time']))

    # 提交事务
    conn.commit()

    # 关闭游标和数据库连接
    cur.close()
    conn.close()

# 持续执行搜索和执行代码块的操作
while True:
    execute_code_blocks()
    time.sleep(120)