import psycopg2

# 数据库连接参数
conn_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '200203',
    'host': '127.0.0.1',
    'port': '5432',
    'sslmode': 'disable',
}

# 连接数据库
conn = psycopg2.connect(**conn_params)
cur = conn.cursor()

# 用户输入
input_id = int(input("请输入要查询的 ID：\n"))

# 查询数据库
select_query = '''
SELECT code FROM search_table WHERE id = %s;
'''
cur.execute(select_query, (input_id,))
result = cur.fetchone()

# 执行代码
if result:
    code = result[0]
    exec(code)
else:
    print("未找到对应的代码")

# 关闭连接
cur.close()
conn.close()
