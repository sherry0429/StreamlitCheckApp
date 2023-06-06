import streamlit as st
import re

# 初始变量
message_variable = ""

# 创建前端界面
st.title('前端信息监听')
message = st.text_input('请输入信息')

# 正则表达式模式
url_pattern = r'^https?://\S+$'  # 验证URL
file_path_pattern = r'^[a-zA-Z]:\\(?:[a-zA-Z0-9\s_@]+\\)*[a-zA-Z0-9\s_@]+\.[a-zA-Z]{2,4}$'  # 验证文件路径
sql_pattern = r'(?i)^SELECT.*$' #验证sql，忽略大小写


def extract_variable_value(sql):
    pattern = r'(\w+)\s*=\s*("[^"]+"|\w+)'

    matches = re.findall(pattern, sql)
    result = ""

    for match in matches:
        variable = match[0]
        value = match[1]
        variable_value = f"{variable}={value}"
        result += variable_value + " "

    return result.strip()

def extract_query_without_variables(sql):
    pattern =r'([\w\s.]+)\s*where'
    match = re.match(pattern, sql)

    if match:
        query = match.group(1)
        return query.strip()
    else:
        return None
    
def extract_variable_positions(sql):
    pattern = r'(\w+)\s*=\s*(\w+)'
    matches = re.findall(pattern, sql)
    positions = []

    for match in matches:
        variable = match[0]
        value = match[1]
        variable_start = sql.find(variable)
        variable_end = variable_start + len(variable) + 1
        positions.append((variable, variable_start, variable_end))

    return positions

# 处理前端输入
if message:
    if re.match(url_pattern, message):
        message_variable = message
        st.write('接收到的URL地址：', message_variable)
    elif re.match(file_path_pattern, message):
        message_variable = message
        st.write('接收到的文件路径：', message_variable)
    elif re.match(sql_pattern, message):
        message_variable = message
        result1 = extract_variable_value(message_variable)
        st.write('提取到的变量信息：',result1)
        result2 = extract_query_without_variables(message_variable)
        st.write('用户的查询语句是：',result2)
    else:
        st.error('输入格式错误，请输入URL地址、文件路径或SQL语句')
else:
    st.warning('请输入信息')