import psycopg2
import datetime
import random
import string



# 连接到PG数据库
def connect_to_pg():

    db_config = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '7PIug1Lk3O',
    'host': 'pg-postgresql',
    'port': '5432',
    'sslmode': 'disable',
    }
    connection = psycopg2.connect(**db_config)
    return connection

def generate_cookie(length=32):
    characters = string.ascii_letters + string.digits + "_-"
    cookie = ''.join(random.choice(characters) for _ in range(length))
    return cookie

def register(username,passwd):
    connection = connect_to_pg()
    cursor = connection.cursor()
    query1 = "select * from users_table where username = %s"
    cursor.execute(query1,(username,))
    res1 = cursor.fetchall()
    if len(res1):
        cursor.close()
        connection.close()
        return 0
    else:
        set_cookie = generate_cookie(32)
        query2 = "insert INTO users_table (username, passwd, cookie) VALUES (%s, %s, %s)"
        params = (username,passwd,set_cookie)
        cursor.execute(query2, params)
        connection.commit()
        cursor.close()
        connection.close()
        return 1
    
def login(username,passwd):
    connection = connect_to_pg()
    cursor = connection.cursor()
    query = "select cookie from users_table where username = %s AND passwd = %s"
    params = (username,passwd)
    cursor.execute(query,params)
    res = cursor.fetchall()
    if len(res):
        return res[0][0]
    else:
        return 0



def log_insert(type,result):
    # 将日志信息插入到 check_output_log 表中
    connection = connect_to_pg()
    cursor = connection.cursor()
    query = """
        INSERT INTO check_output_log (output_type, result, state_time)
        VALUES (%s, %s, %s);
    """
    params = (type,result,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    cursor.execute(query, params)
    connection.commit()
    cursor.close()
    connection.close()

# 查询监测结果
def query_results(date, monitoring_type):
    connection = connect_to_pg()
    cursor = connection.cursor()
    date_format = '%Y-%m-%d'
    date = datetime.datetime.strptime(date, date_format)
    partition_name = 'test2_monitortable_' + date.strftime('%Y_%m_%d')
    query = "SELECT * FROM " + partition_name + " WHERE request_type = %s;"
    params = (monitoring_type,)
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
    except:
        return None
    cursor.close()
    connection.close()
    return rows


def get_content(cookie,check_type):
    connection = connect_to_pg()
    cursor = connection.cursor()
    query1 = "SELECT state_time FROM users_status WHERE cookie = %s AND check_type = %s"
    params1 = (cookie,check_type)
    cursor.execute(query1,params1)
    res1 = cursor.fetchall()
    if len(res1) > 0:
        date_format = "%Y-%m-%d %H:%M:%S"
        state_time = datetime.strptime(res1[0][0], date_format)
        query2 = "SELECT * FROM check_output_log WHERE check_time >= %s"
        params2 = (state_time,)
        cursor.execute(query2,params2)
        res2 = cursor.fetchall()
        query3 = "UPDATE users_status SET state_time = %s WHERE cookie = %s AND check_type = %s"
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        params3 = (time, cookie, check_type)
        cursor.execute(query3,params3)
        connection.commit()
        cursor.close()
        connection.close()
        return res2
    else:
        query2 = "SELECT * FROM check_output_log"
        cursor.execute(query2)
        res2 = cursor.fetchall()
        query3 = "insert into users_status(check_type,cookie,state_time) values(%s,%s,%s)"
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        params3 = (check_type,time,cookie)
        cursor.execute(query3,params3)
        connection.commit()
        cursor.close()
        connection.close()
        return res2

