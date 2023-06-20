streamlit.py

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
def check_code_block(code_block, language):
    dete = True
    if language == 'python':
        dete = detection.validate_python_code_block(code_block)
    elif language == 'lua':
        detection.validate_lua_code_block(code_block)
    elif language == 'sql':
        detection.is_valid_sql_query(code_block)
    else:
        raise ValueError('Unsupported language')
    return dete

# 模块导入页面
def page_import():
    st.header("模块导入")
    code = st.text_area("输入代码", height=200)
    if st.button("导入"):
        # code = html.escape(code)# 对用户输入的代码块进行 HTML 转义
        if (check_code_block(code, "python")):
            try:
                now = datetime.now()  # 获取当前时间
                conn = connect_to_pg()  # 连接到 PostgreSQL 数据库
                cur = conn.cursor()
                cur.execute("INSERT INTO t_check_roles (id, code, create_time, enable) VALUES (%s, %s, %s, %s);", (current_role_id, code, now,True))
                cur.execute("INSERT INTO t_check_role_code (role_id, code_block, create_time, start_time, end_time, enable) VALUES (%s, %s, %s, %s, NULL, %s);", (current_role_id, code, now,now,True))  # 将输入的代码插入到 t_check_role_code 表格中
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


detection.py


import ast
import lupa
from lupa import LuaRuntime
import sqlparse
# 允许的Python语句和表达式
ALLOWED_STATEMENTS = {'abs', 'all', 'any', 'bin', 'bool', 'callable', 'chr', 'complex', 'dict', 'divmod', 'enumerate', 'float', 'format',
    'for', 'frozenset', 'getattr', 'hasattr', 'hash', 'hex', 'id', 'int', 'isinstance', 'issubclass', 'iter', 'len',
    'list', 'locals', 'map', 'max', 'min', 'next', 'object', 'oct', 'ord', 'pow', 'print', 'range', 'repr',
    'reversed', 'round', 'set', 'slice', 'sorted', 'str', 'sum', 'tuple', 'type', 'zip',
    '__import__', # 在Python 3中已经不再是内建函数
    }
ALLOWED_EXPRESSIONS = { '+', '-', '*', '/', '//', '%', '**', '|', '&', '^', '~', '<<', '>>', '<', '<=', '>', '>=', '==', '!=',
    'not', 'and', 'or', 'is', 'in', 'not in'}
# 验证代码块的合法性
def validate_python_code_block(code_block):
    # try:
    #     # 使用 compile() 函数编译代码块
    #     compile(code_block, '<string>', 'exec', ast.PyCF_ONLY_AST | ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)

    #     # 将代码块解析为抽象语法树
    #     tree = ast.parse(code_block)

    #     # 检查语法树中的每个节点是否允许
    #     for node in ast.walk(tree):
    #         if isinstance(node, ast.Name) and node.id in ALLOWED_STATEMENTS:
    #             raise ValueError("禁止使用该语句")
    #         elif isinstance(node, ast.BinOp) and node.op.__class__.__name__ in ALLOWED_EXPRESSIONS:
    #             raise ValueError("禁止使用该表达式")
    # except Exception as e:
    #     # 如果存在错误，返回错误消息
    #     return str(e)
    # # 如果代码块合法，返回None
    # return None
    try:
        # 使用 ast 模块解析代码
        ast.parse(code_block, mode='exec')
        return True
    except SyntaxError:
        # 如果代码存在语法错误，则返回 False
        return False







# 允许的 Lua 语句和表达式
DISALLOWED_STATEMENTS = {}
DISALLOWED_EXPRESSIONS = {}

# 验证代码块的合法性
def validate_lua_code_block(code_block):
    try:
        # 创建 Lua 运行时环境
        lua = LuaRuntime(unpack_returned_tuples=True)

        # 将代码块解析为抽象语法树
        ast = lua.compile(code_block)

        # 检查语法树中的每个节点是否允许
        for node in ast:
            if node.__class__.__name__ in DISALLOWED_STATEMENTS or node.__class__.__name__ in DISALLOWED_EXPRESSIONS:
                raise ValueError("禁止使用该语句或表达式")

        # 检查代码中是否存在危险的标准库函数
        if "os.execute" in code_block or "io.popen" in code_block:
            raise ValueError("禁止使用该函数")

        # 如果代码块合法，返回 None
        return None

    except Exception as e:
        # 如果存在错误，返回错误消息
        return str(e)



def is_valid_sql_query(query):
    """
    检查 SQL 查询是否是有效的 SQL 语句

    Args:
        query (str): SQL 查询语句

    Returns:
        bool: 如果 SQL 查询是有效的 SQL 语句，则返回 True，否则返回 False
    """

    # 解析 SQL 查询语句
    try:
        parsed_query = sqlparse.parse(query)
    except Exception as e:
        return False

    # SQL 查询是有效的 SQL 语句
    return True


postgres.py


import psycopg2



# def connect_to_pg():
#     connection = psycopg2.connect(
#         host="121.40.100.184",
#         port="5432",
#         database="postgres",
#         user="postgres",
#         password="7PIug1Lk3O"
#     )
#     return connection

conn_params = {
    "host": "pg-postgresql",
    "port": "5432",
    "database": "postgres",
    "user": "postgres",
    "password": "7PIug1Lk3O",
    "sslmode":"disable"
}

def create_table_t_check_roles():
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS t_check_roles (
        id SERIAL PRIMARY KEY,
        code TEXT NOT NULL,
        create_time TIMESTAMP NOT NULL,
        enable BOOLEAN
    );
    '''
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    cur.execute(create_table_query)
    conn.commit()
    cur.close()
    conn.close()

# 执行创建表的操作
create_table_t_check_roles()


# def main():
#     connection = connect_to_pg()
#     cursor = connection.cursor()
#     sql = "select *"
#     cursor.execute(sql)
#     rows = cursor.fetchall()
#     for row in rows:
#         print(row)
#     cursor.close()
#     connection.close()

#if __name__ == "__main__":
#    main()


def create_table_t_check_role_code():
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS t_check_role_code (
        id SERIAL PRIMARY KEY,
        role_id TEXT REFERENCES t_check_roles (id),
        code_block TEXT,
        create_time TIMESTAMP DEFAULT NOW(),
        enable BOOLEAN,
        start_time TIMESTAMP,
        end_time TIMESTAMP
    );
    '''
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    cur.execute(create_table_query)
    conn.commit()
    cur.close()
    conn.close()

# 执行创建表的操作
create_table_t_check_role_code()