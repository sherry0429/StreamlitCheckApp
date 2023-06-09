import streamlit as st
import pandas as pd
import psycopg2

from datetime import datetime
# psql -h localhost -p 5432 -U postgres

current_role_id = None

def login():
    st.title("用户登录")

    role_id = st.text_input("角色 ID")
    password = st.text_input("密码", type="password")

    if st.button("登录"):
        if password == "password":
            st.success("登录成功！")
            return role_id
        else:
            st.error("密码错误！")
            return None


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




def main():

    global current_role_id  # 声明全局变量
    current_role_id = login()  # 保存角色 ID

    if current_role_id is None:
        return

    st.sidebar.title("导航")
    choice = st.sidebar.radio("选择一个页面", ("模块导入", "模块管理"))

    if choice == "模块导入":
        page_import()
    elif choice == "模块管理":
        page_management()
    

def page_import():
    st.header("模块导入")

    code = st.text_area("输入代码", height=200)
    if st.button("导入"):
        now = datetime.now()  # 获取当前时间
        conn = connect_to_pg()  # 连接到 PostgreSQL 数据库
        cur = conn.cursor()
        cur.execute("INSERT INTO t_check_role_code (role_id, code_block, create_time, start_time, end_time, enable) VALUES (%s, %s, %s, %s, NULL, %s);", (current_role_id, code, now,now,True))  # 将输入的代码插入到 t_check_role_code 表格中
        conn.commit()  # 提交事务，保存对数据库的修改
        st.success("代码导入成功！")




def page_management(role_id):
    st.header("模块管理")

    conn = connect_to_pg()  # 连接到 PostgreSQL 数据库
    cur = conn.cursor()

    # 查询当前用户可以管理的代码块
    cur.execute("""
        SELECT id, code_block, create_time, start_time, end_time, enable
        FROM t_check_role_code;
    """)
    rows = cur.fetchall()

    # 显示代码块列表
    for row in rows:
        code_id, code_block, create_time, start_time, end_time, enable = row

        with st.beta_expander(f"代码块 {code_id}"):
            # 显示代码块内容
            st.code(code_block)

            # 显示代码块的 ID、创建时间、启用时间和终止时间
            st.write(f"ID：{code_id}")
            st.write(f"创建时间：{create_time}")
            st.write(f"启用时间：{start_time}")
            st.write(f"终止时间：{end_time}")

            # 允许用户重新启用或关闭代码块
            if enable:
                if st.button("关闭"):
                    cur.execute("""
                        UPDATE t_check_role_code
                        SET end_time = %s, enable = FALSE
                        WHERE id = %s;
                    """, (datetime.now(), code_id))
                    conn.commit()  # 提交事务，保存对数据库的修改
                    st.success("关闭成功！")
            else:
                if st.button("启用"):
                    cur.execute("""
                        UPDATE t_check_role_code
                        SET start_time = %s, enable = TRUE
                        WHERE id = %s;
                    """, (datetime.now(), code_id))
                    conn.commit()  # 提交事务，保存对数据库的修改
                    st.success("启用成功！")

    conn.close()  # 关闭数据库连接


    

if __name__ == '__main__':
    main()