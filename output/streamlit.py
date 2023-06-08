import streamlit as st
import psycopg2
import datetime
# psql -h pg-postgresql -p 5432 -U postgres
# passwd 7PIug1Lk3O

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

def log_insert(result):
    connection = connect_to_pg()
    cursor = connection.cursor()
    query = """
        INSERT INTO check_output_log (output_type, result, state_time)
        VALUES (%s, %s, %s);
    """
    params = ('streamlit',result,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
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
    st.write(query)
    params = (monitoring_type,)
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
    except Exception as e:
        log_insert("failed")
        return None
    cursor.close()
    connection.close()
    return rows
# Streamlit应用程序
def main():
    st.title("Monitoring Results")
    date = st.date_input('Select the Date:', datetime.datetime.today()).strftime('%Y-%m-%d')
    options = ['url', 'path', 'sql']
    monitoring_type = st.selectbox('Select the MonitoringType:', options)
    results = None
    if st.button("查询"):
        results = query_results(date, monitoring_type)
    if results is not None:
        log_insert("success")
        for result in results:
            st.write(result)
if __name__ == '__main__':
    main()