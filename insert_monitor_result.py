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

def insert_monitoring_result(monitoring_result):
    # 建立数据库连接
    conn = psycopg2.connect(**conn_params)

    # 创建一个游标对象
    cur = conn.cursor()

    # 使用参数绑定插入监测结果
    query = """
    INSERT INTO monitoring_table (id, request_type, request_content, judgement_result, query_time)
    VALUES (%s, %s, %s, %s, %s);
    """

    cur.execute(query, (monitoring_result['id'], monitoring_result['request_type'], monitoring_result['request_content'], monitoring_result['judgement_result'], monitoring_result['query_time']))

    # 提交事务
    conn.commit()

    # 关闭游标和数据库连接
    cur.close()
    conn.close()


'''
示例调用：
monitoring_result = {
    "request_type": "Api - 1",
    "request_content": "http://example.com",
    "judgement_result": "200",
    "query_time": datetime.datetime.now()
}

insert_monitoring_result(monitoring_result)
'''