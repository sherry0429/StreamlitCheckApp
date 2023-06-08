from proj.tasks import app
import psycopg2
import datetime

def db_select(query):
    connection = psycopg2.connect(
        host="pg-postgresql",
        port="5432",
        dbname="postgres",
        user="postgres",
        password="7PIug1Lk3O",
        sslmode="disable"
    )
    cursor = connection.cursor()
    cursor.execute(query)
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
    query = "INSERT INTO check_output(check_time,result,details) VALUES(%s,%s,%s);"
    cursor.execute(query, params)
    connection.commit()
    cursor.close()
    connection.close()
    return 1

@app.task
def push():
    t = datetime.datetime.now()
    t0 = t.strftime("%Y-%m-%d %H:%M:%S")
    t1 = (t-datetime.timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")
    table_name = "test2_monitortable_" + datetime.datetime.now().strftime("%Y_%m_%d")
    query = "SELECT * FROM {table} WHERE query_time BETWEEN '{start_time}' AND '{end_time}'".format(
        table=table_name,
        start_time=t1,
        end_time=t0
    )
    try:
        rows = db_select(query)
    except:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'query failed'
    check = 0
    num = len(rows)
    ids = []
    if rows != []:
        for row in rows:
            if row[3] == 'no':
                check += 1
                ids.append(row[0])
    if check > 0:
        params = (
            t0,f'{num} total,{check} failed',f'id {ids}'
        )
        db_insert(params)
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'push already'

