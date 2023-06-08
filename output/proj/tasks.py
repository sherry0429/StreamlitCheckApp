from proj.app_test import app
import psycopg2
import datetime

def db_select(query,params):
    connection = psycopg2.connect(
        host="pg-postgresql",
        port="5432",
        dbname="postgres",
        user="postgres",
        password="7PIug1Lk3O",
        sslmode="disable"
    )
    cursor = connection.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows

def db_insert(params):
    connection = psycopg2.connect(
        host="pg-postgresql",
        port="5432",
        dbname="postgres",
        user="postgres",
        password="7PIug1Lk3O",
        sslmode="disable"
    )
    cursor = connection.cursor()
    query = "INSERT INTO check_output_log VALUES('webhook',%s,"+time()+");"
    cursor.execute(query, params)
    connection.commit()
    cursor.close()
    connection.close()
    return 1

def time(q=0):
    return (datetime.datetime.now()-datetime.timedelta(minutes=q)).strftime("%Y-%m-%d %H:%M:%S")

@app.task
def push():
    query = 'SELECT * FROM check_output WHERE check_time between %s and %s'
    params = (time(1),time())
    try:
        rows = db_select(query,params)
    except:
        db_insert('query failed')
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'query failed'
    
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'push already'


@app.task
def push(x, y):
    a = x
    b = y
    return "%s + %s = %s" % (a, b, a+b)