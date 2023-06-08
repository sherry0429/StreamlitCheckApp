import streamlit as st
import pandas as pd
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
#def main():
    # st.title("监测结果查询")
    

    
    # col1, col2, col3, col4, col5=st.columns([0.2, 1, 0.2, 1, 0.2])
    # with col1:
    #     st.empty()
    # with col2:
    #     date = st.text_input("请输入日期（YYYY-MM-DD）：")
    # with col3:
    #     st.empty()
    # with col4:
    #     monitoring_type = st.text_input("请输入监测类型：")
    # with col5:
    #     st.empty()

    # date = st.text_input("请输入日期（YYYY-MM-DD）：")
    # monitoring_type = st.text_input("请输入监测类型：")
    # if st.button("查询"):
    # # 查询监测结果
    #     results = query_results(date, monitoring_type)
    # # 显示查询结果
    # for result in results:
    # result = (date,monitoring_type)
    # st.write(result)

# def main():
#     st.sidebar.title("导航")
#     choice = st.sidebar.radio("选择一个页面", ("模块导入", "模块管理"))

#     if choice == "模块导入":
#         module_import()
#     elif choice == "模块管理":
#         module_management()

# def module_import():
#     st.title("模块导入")

#     # 输入代码块的输入框
#     code_input = st.text_area("输入代码块", height=200)

#     # 导入按钮
#     if st.button("导入"):
#         try:
#             exec(code_input)
#             st.success("模块已成功导入")
#         except Exception as e:
#             st.error(f"模块导入出错: {e}")

# def module_management():
#     st.title("模块管理")

#     # 显示模块的开关
#     st.sidebar.subheader("模块开关")
#     module_toggle = st.sidebar.checkbox("显示模块")

#     # 模块详细信息
#     if module_toggle:
#         st.subheader("模块详细信息")
#         st.write("这里是模块的详细信息")



def main():
    
    st.sidebar.title("导航")
    choice = st.sidebar.radio("选择一个页面", ("模块导入", "模块管理"))

    if choice == "模块导入":
        page_import()
    elif choice == "模块管理":
        page_management()
    
    # st.set_page_config(page_title="模块导入与管理", page_icon=":books:")

    # st.title("模块导入与管理")

    # menu = ["模块导入", "模块管理"]
    # choice = st.sidebar.selectbox("选择一个选项", menu)

    # if choice == "模块导入":
    #     page_import()
    # else:
    #     page_management()

def page_import():
    st.header("模块导入")

    code = st.text_area("输入代码", height=200)
    if st.button("导入"):
        print ("1")
        # 在这里实现导入代码的代码

def page_management():
    st.header("模块管理")

    # 在这里获取已经存在的代码块的启用情况与详细信息，存储在一个Pandas DataFrame中
    data = pd.DataFrame({
        "名称": ["代码块1", "代码块2", "代码块3"],
        "启用": [True, False, True],
        "详细信息": ["这是代码块1的详细信息", "这是代码块2的详细信息", "这是代码块3的详细信息"]
    })

    st.dataframe(data)


    

if __name__ == '__main__':
    main()