import streamlit as st
import psycopg2
import datetime
# psql -h localhost -p 5432 -U postgres

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
# 查询监测结果
def query_results(date, monitoring_type):
    connection = connect_to_pg()
    cursor = connection.cursor()
    date_format = '%Y-%m-%d'
    date = datetime.strptime(date, date_format)

    query = '''
        SELECT * FROM test2_monitortable
        WHERE date_column >= %s::date
        AND date_column < %s::date AND request_type = %s;
    '''
    params = (date,(date + datetime.timedelta(days=1)), monitoring_type)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows
# Streamlit应用程序
def main():
    st.title("监测结果查询")
    date = st.text_input("请输入日期（YYYY-MM-DD）：")
    monitoring_type = st.text_input("请输入监测类型：")
    if st.button("查询"):
    # 查询监测结果
        results = query_results(date, monitoring_type)
    # 显示查询结果
    for result in results:
        st.write(result)
if __name__ == '__main__':
    main()