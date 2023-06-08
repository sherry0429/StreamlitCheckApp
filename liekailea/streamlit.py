import streamlit as st
import psycopg2
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

# Streamlit应用程序
def main():
    st.title("监测结果查询")
    date = st.text_input("请输入日期（YYYY-MM-DD）：")
    monitoring_type = st.text_input("请输入监测类型：")
    # if st.button("查询"):
    # # 查询监测结果
    #     results = query_results(date, monitoring_type)
    # # 显示查询结果
    # for result in results:
    result = (date,monitoring_type)
    st.write(result)
if __name__ == '__main__':
    main()