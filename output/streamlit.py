import streamlit as st
import datetime
from psql import log_insert,query_results
# psql -h pg-postgresql -p 5432 -U postgres
# passwd 7PIug1Lk3O

# Streamlit应用程序
def main():
    # 显示页面标题
    st.title("Monitoring Results")
    # 获取用户选择的日期
    date = st.date_input('Select the Date:', datetime.datetime.today()).strftime('%Y-%m-%d')
    
    # 提供监控类型选择下拉菜单
    options = ['url', 'path', 'sql']
    monitoring_type = st.selectbox('Select the MonitoringType:', options)

    results = None

    # 当用户点击"查询"按钮时执行以下操作
    if st.button("查询"):
        results = query_results(date, monitoring_type)


    # 如果查询结果不为空，则逐个显示结果并记录日志为"streamlit"和"success"
    if results is not None:
        log_insert("streamlit","success")
        for result in results:
            st.write(result)
    # 如果查询结果为空，则记录日志为"streamlit"和"failed"
    else:
        log_insert("streamlit","failed")
if __name__ == '__main__':
    main()