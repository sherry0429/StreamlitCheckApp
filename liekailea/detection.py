import ast

# 允许的Python语句和表达式
DISALLOWED_STATEMENTS = {}
DISALLOWED_EXPRESSIONS = {}
# 验证代码块的合法性
def validate_python_code_block(code_block):
    try:
        # 将代码块解析为抽象语法树
        tree = ast.parse(code_block)

        # 检查语法树中的每个节点是否允许
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in DISALLOWED_STATEMENTS:
                raise ValueError("禁止使用该语句")
            elif isinstance(node, ast.BinOp) and node.op.__class__.__name__ in DISALLOWED_EXPRESSIONS:
                raise ValueError("禁止使用该表达式")
    except Exception as e:
        # 如果存在错误，返回错误消息
        return str(e)
    # 如果代码块合法，返回None
    return None




import lupa
from lupa import LuaRuntime

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




import sqlparse

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
