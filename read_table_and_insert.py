"""
Brief introduction:
This code is to read the table created from the rule component. This table is
 CREATE TABLE IF NOT EXISTS t_check_role_code (
        id SERIAL PRIMARY KEY,
        role_id TEXT REFERENCES t_check_roles (id),
        code_block TEXT,
        create_time TIMESTAMP DEFAULT NOW(),
        enable BOOLEAN,
        start_time TIMESTAMP,
        end_time TIMESTAMP
    ).
This is the basic complete flow of the monitoring component.
First we iterate through the table of rule components and use enable and start_time and end_time as criteria.
The code in the code_block is read, executed and the result("yes" or "no") is obtained if the condition is met.
Then we write all kinds of required information together with the results into the partitioned monitor table "test2_monitortable_xxxx_xx_xx"(test2_monitortable_2023_06_14 for example) created by our component with day partition.
Compatible with executing python code and lua code.
If the code in code_block fails to execute or reports an error, the value of judgment_result in the monitoring table is "ero"
"""
import psycopg2
import datetime
import time
import re
import lupa
from lupa import LuaRuntime

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
    FROM t_check_role_code_ydl
    WHERE enable = TRUE AND start_time <= NOW() AND end_time >= NOW();
    '''
    cur.execute(select_query)
    rows = cur.fetchall()

    # 执行代码块
    for row in rows:
        id, role_id, code_block, create_time, enable, start_time, end_time = row
        try:
            #获取满足规则的id
            print(id)
            code_block = code_block.strip()  # 去除代码块开头和结尾的空格
            if code_block.startswith("def"):  # Python 代码
                pattern = r'def (\w+)\s*\(\):'  # 使用正则表达式模式匹配函数定义
                match = re.search(pattern, code_block)
                if match:
                    function_name = match.group(1)  # 获取函数名

                exec(code_block)  # 执行 Python 代码
                result = eval(f"{function_name}()")  # 获取 Python 函数的返回值

            else:  # Lua 代码
                pattern = r'function\s+(\w+)\s*\('  # 使用正则表达式模式匹配函数定义
                match = re.search(pattern, code_block)
                if match:
                    function_name = match.group(1)  # 获取函数名

                lua_vm = LuaRuntime()  # 创建 Lua 解释器实例
                lua_vm.execute(code_block)  # 执行 Lua 代码
                result = lua_vm.eval(f"{function_name}()")  # 获取 Lua 函数的返回值

            monitoring_result = {
                "request_type": role_id,
                "request_content": code_block,
                "judgement_result": result,
                "query_time": datetime.datetime.now()
            }
            insert_monitoring_result(monitoring_result)
        except Exception as e:
            monitoring_result = {
                "request_type": role_id,
                "request_content": code_block,
                "judgement_result": 'ero',
                "query_time": datetime.datetime.now()
            }
            insert_monitoring_result(monitoring_result)

    cur.close()
    conn.close()

def insert_monitoring_result(monitoring_result):
    # 建立数据库连接
    conn = psycopg2.connect(**conn_params)

    # 创建一个游标对象
    cur = conn.cursor()

    # 使用参数绑定插入监测结果，防止sql注入
    table_name = "test2_monitortable_" + datetime.datetime.now().strftime("%Y_%m_%d")
    query = """
    INSERT INTO {table} (request_type, request_content, judgement_result, query_time) VALUES (%s, %s, %s, %s)
    """.format(table=table_name)

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