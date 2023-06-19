import streamlit as st
import psycopg2
import re
import html
from datetime import datetime
import sys
sys.path.append('./')
import detection


current_role_id = 17




# # 使用正则表达式定义Python代码块的语法规则
# python_pattern = r'^\s*def\s+\w+\(.*\):\n(\s+.+\n)*$'
# lua_pattern = r'^\s*(function|if|for|while|repeat)\s+.*$'
# sql_pattern = r'^\s*(SELECT|INSERT|UPDATE|DELETE)\s+.*$'


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

# # 使用参数化查询的方式执行SQL语句
# def execute_sql_query(query, params):
#     conn = connect_to_pg()  # 连接到 PostgreSQL 数据库
#     cursor = conn.cursor()
#     cursor.execute(query, params)
#     result = cursor.fetchall()
#     conn.commit()
#     conn.close()
#     return result

# 检测代码块的合法性并防止SQL注入攻击
def check_code_block(code_block):
    dete = True
    # if language == 'python':
    #     dete = detection.validate_python_code_block(code_block)
    # elif language == 'lua':
    #     dete = detection.validate_lua_code_block(code_block)
    # elif language == 'sql':
    #     dete = detection.is_valid_sql_query(code_block)
    # else:
    #     raise ValueError('Unsupported language')
    if code_block.startswith("def"):
        dete = detection.validate_python_code_block(code_block)
    elif code_block.startswith("function"):
        dete = detection.validate_lua_code_block(code_block)
    else:
        dete = False
    return dete

# 模块导入页面
def page_import():
    st.header("模块导入")
    code = st.text_area("输入代码", height=200)
    language = st.selectbox("选择代码块语言类型", ["url", "path", "sql"])
    if st.button("导入"):
        # code = html.escape(code)# 对用户输入的代码块进行 HTML 转义
        if (check_code_block(code)):
            # 查询数据库以获取最后一个插入的代码块的 id 值
            with connect_to_pg() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT MAX(id) FROM t_check_roles;")
                    last_id = cur.fetchone()[0]
                    if last_id is None:
                        last_id = 0
                    new_id = last_id + 1
            try:
                now = datetime.now()  # 获取当前时间
                conn = connect_to_pg()  # 连接到 PostgreSQL 数据库
                cur = conn.cursor()
                # if(language == "sql"):
                #     code = html.escape(code)# 对用户输入的代码块进行 HTML 转义
                cur.execute("INSERT INTO t_check_roles (id, code, create_time, enable) VALUES (%s, %s, %s, %s);", (new_id, code, now,True))
                cur.execute("INSERT INTO t_check_role_code (id,role_id, code_block, create_time, start_time, end_time, enable) VALUES (%s,%s, %s, %s, %s, NULL, %s);", (new_id,current_role_id, code, now,now,True))  # 将输入的代码插入到 t_check_role_code 表格中
                conn.commit()  # 提交事务，保存对数据库的修改
                st.success("代码导入成功！")
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error("代码导入失败：" + str(e))
        else:
            st.error("导入代码失败，非法代码！")
        

# 模块管理页面
def page_management():
    st.header("模块管理")

    conn = connect_to_pg()  # 连接到 PostgreSQL 数据库
    cur = conn.cursor()

    # 查询所有模块
    cur.execute("""
        SELECT id, role_id, code_block, create_time, start_time, end_time, enable
        FROM t_check_role_code;
    """)

    rows = cur.fetchall()

    # 显示模块管理表格
    if len(rows) > 0:
        st.write("以下是所有模块的列表：")
        for row in rows:
            code_id,role_id, code_block, create_time, start_time, end_time, enable = row

            # 显示模块代码块
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
                    button_id = hash(f"close_button_{code_id}")
                    if st.button("关闭", key=button_id):
                        cur.execute("""
                            UPDATE t_check_role_code
                            SET end_time = %s, enable = FALSE
                            WHERE id = %s;
                        """, (datetime.now(), code_id))
                        conn.commit()  # 提交事务，保存对数据库的修改
                        st.success("关闭成功！")
                else:
                    button_id = hash(f"enable_button_{code_id}")
                    if st.button("启用", key=button_id):
                        cur.execute("""
                            UPDATE t_check_role_code
                            SET start_time = %s, enable = TRUE
                            WHERE id = %s;
                        """, (datetime.now(), code_id))
                        conn.commit()  # 提交事务，保存对数据库的修改
                        st.success("启用成功！")
    else:
        st.write("没有模块可供管理。")

    conn.close()
    
# 用户登录页面
# def page_login():
#     st.header("用户登录")

#     current_role_id = st.text_input("角色 ID")
#     password = st.text_input("密码", type="password")

#     if st.button("登录"):
#         if password == "password":
#             st.success("登录成功！")
#             return current_role_id
#         else:
#             st.error("密码错误！")
#             return None

# 主页面
def main():
    # global current_role_id
    # current_role_id = page_login()  # 保存角色 ID
    # if current_role_id is None:
    #      return


    st.sidebar.title("导航")
    choice = st.sidebar.radio("选择一个页面", ("模块导入", "模块管理"))
    

    if choice == "模块导入":
        page_import()
    elif choice == "模块管理":
        page_management()

if __name__ == '__main__':
    main()