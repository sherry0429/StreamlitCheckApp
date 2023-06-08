import streamlit as st
import psycopg2
import datetime
from proj.psql import connect_to_pg,log_insert,query_results
# psql -h pg-postgresql -p 5432 -U postgres
# passwd 7PIug1Lk3O

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