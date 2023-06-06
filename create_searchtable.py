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

# 创建search_table表
def create_search_table():
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS search_table (
        id INTEGER PRIMARY KEY,
        code TEXT NOT NULL
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
        (1, 'number = int(input("请输入一个数值：\\n"))\nif number == 1:\n    print("yes")\nelse:\n    print("no")'),
        (2, 'number = int(input("请输入一个数值：\\n"))\nif number == 2:\n    print("yes")\nelse:\n    print("no")'),
        (3, 'number = int(input("请输入一个数值：\\n"))\nif number == 3:\n    print("yes")\nelse:\n    print("no")')
    ]
    insert_query = '''
    INSERT INTO search_table (id, code)
    VALUES (%s, %s);
    '''
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    cur.executemany(insert_query, sample_data)
    conn.commit()
    cur.close()
    conn.close()

# 执行创建表和插入数据的操作
create_search_table()
insert_sample_data()
