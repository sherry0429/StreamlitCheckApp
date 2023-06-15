# 运行前准备

## 环境

服务器IP 121.40.100.184

pg数据库基本信息：

```python
'dbname': 'postgres',
'user': 'postgres',
'password': '7PIug1Lk3O',
'host': 'pg-postgresql',
'port': '5432',
'sslmode': 'disable',
```

## 读取的数据库表 t_check_role_code_ydl

| 字段名      | 类型      | 描述                                              |
| ----------- | --------- | ------------------------------------------------- |
| id          | SERIAL    | 规则的id编号（1、2、3...）                        |
| role_id     | TEXT      | 规则的角色类型("url","path","sql")                |
| code_block  | TEXT      | 规则组件的代码存放位置，可以是Python函数或Lua函数 |
| create_time | TIMESTAMP | 规则被创建的时间                                  |
| enable      | BOOLEAN   | 规则是否可执行(True/False)                        |
| start_time  | TIMESTAMP | 规则生效时间                                      |
| end_time    | TIMESTAMP | 规则失效时间                                      |



PS:如果没有此表,代码无法运行．没有的话运行以下代码(创建此表并插入一些样本数据)：

```python
import psycopg2
from datetime import datetime

# 数据库连接参数
conn_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '7PIug1Lk3O',
    'host': 'pg-postgresql',
    'port': '5432',
    'sslmode': 'disable',
}

# 创建表
def create_table():
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS t_check_role_code_ydl (
        id SERIAL PRIMARY KEY,
        role_id TEXT,
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
    
# 插入样本数据
def insert_sample_data():
    # 数据样本
    data = [
        {

            'role_id': 'url',
            'code_block': '''
    def sample_function():
        return "yes"
''',

            'create_time': datetime.now(),
            'enable': True,
            'start_time': datetime(2023, 6, 1),
            'end_time': datetime(2023, 6, 30)
        },
        {
            'role_id': 'sql',
            'code_block': '''
    function sample_function()
        if 0 < 1 then
            return "yes"
        else
            return "no"
        end
    end


    ''',

            'create_time': datetime.now(),
            'enable': True,
            'start_time': datetime(2023, 6, 11),
            'end_time': datetime(2023, 6, 30)
        },
        {

            'role_id': 'path',
            'code_block': '''
    def sample_function():
        if 0 < 1:
            return "yes"
        else:
            return "no"
    ''',

            'create_time': datetime.now(),
            'enable': False,
            'start_time': datetime(2023, 6, 1),
            'end_time': datetime(2023, 6, 30)
        }
    ]

    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()

    # 插入数据
    for item in data:
        insert_query = '''
        INSERT INTO t_check_role_code_ydl (role_id, code_block, create_time, enable, start_time, end_time)
        VALUES (%s, %s, %s, %s, %s, %s)
        '''
        cur.execute(insert_query, (item['role_id'], item['code_block'], item['create_time'], item['enable'], item['start_time'], item['end_time']))

    conn.commit()
    cur.close()
    conn.close()

#执行创建表的操作
create_table()
print("创建表成功")
insert_sample_data()
print("插入数据成功")
```



# 运行步骤

进入服务器dev-0

```
#进入代码所在文件夹
cd /development
cd yuandalin
#创建以日分区的监测表格
python create_monitor_table.py 
#循环读取规则组件的表格,执行满足要求的代码,并将结果写入检测表
python read_table_and_insert.py
```



# 代码解释

## 创建监测表

[create_monitor_table.py](./create_monitor_table.py)

### 创建分区主表create_partitioned_monitoring_table()

| 功能                 | 输入                                  | 输出                                  |
| -------------------- | ------------------------------------- | ------------------------------------- |
| 创建分区表           | 无                                    | 无                                    |
| 构建创建表的SQL语句  | 无                                    | create_table_query（创建表的SQL语句） |
| 建立数据库连接       | conn_params（数据库连接参数）         | 无                                    |
| 创建游标对象         | conn（数据库连接对象）                | 无                                    |
| 执行创建表的SQL语句  | create_table_query（创建表的SQL语句） | 无                                    |
| 提交事务             | conn（数据库连接对象）                | 无                                    |
| 关闭游标和数据库连接 | 无                                    | 无                                    |

### 表Test_monitortable_test2

| 行号 | 内容                                    | 作用                                                         |
| ---- | --------------------------------------- | ------------------------------------------------------------ |
| 1    | `id SERIAL,#记录执行的规则id`           | 创建 `id` 列，用于记录执行的规则 id                          |
| 2    | `request_type VARCHAR(20) NOT NULL,`    | 创建 `request_type` 列，作为请求类型，并从 `t_check_role_code_ydl` 表中继承 `role_id` |
| 3    | `request_content TEXT NOT NULL,`        | 创建 `request_content` 列，作为执行的具体代码，并从 `t_check_role_code_ydl` 表中继承 `code_block` |
| 4    | `judgement_result VARCHAR(3) NOT NULL,` | 创建 `judgement_result` 列，作为执行代码后的返回结果，如果代码无法执行，返回 "ero" |
| 5    | `query_time TIMESTAMP NOT NULL,`        | 创建 `query_time` 列，作为写入时间，以该时间决定写入哪一张分区表 |
| 6    | `PRIMARY KEY (id, query_time)`          | 创建 `id` 和 `query_time` 列的联合主键                       |
| 7    | `) PARTITION BY RANGE (query_time);`    | 创建以 `query_time` 列为分区依据的分区表                     |

### 创建每日分区create_partitioned_monitoring_table()

```python
def create_daily_partition_table(start_date, end_date):
    current_date = start_date
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    while current_date <= end_date:
        #创建每日分区表,名称为(以2023年6月14日为例):Test2_monitortable_2023_06_14
        partition_table_query = '''
        CREATE TABLE IF NOT EXISTS Test2_monitortable_{date} PARTITION OF Test_monitortable_test2
        FOR VALUES FROM ('{date} 00:00:00') TO ('{date} 23:59:59');
        '''
        cur.execute(partition_table_query.format(date=current_date.strftime("%Y_%m_%d")))
        current_date += timedelta(days=1)
    conn.commit()
    cur.close()
    conn.close()
```

从6月1日创建到了7月30日,每天一张表

```python
start_date = datetime(2023, 6, 1).date()
end_date = datetime(2023, 7, 30).date()
```



## 执行监测任务

[read_table_and_insert.py](./read_table_and_insert.py)

### 查询满足要求的表中内容execute_code_blocks()

enable = True 且当前时间在规则生效时间之后,规则失效时间之前.

```python
 # 查询满足条件的记录
    select_query = '''
    SELECT *
    FROM t_check_role_code_ydl
    WHERE enable = TRUE AND start_time <= NOW() AND end_time >= NOW();
    '''
```

### 执行满足要求内容的code_block中的代码execute_code_blocks()

以def和function来判断是python代码还是lua代码,然后正则提取函数名,执行后获得结果.

| 功能                       | 输入                                   | 输出                                                         |
| -------------------------- | -------------------------------------- | ------------------------------------------------------------ |
| 迭代遍历数据库记录         | rows（数据库查询结果集）               | 无                                                           |
| 获取记录的字段值           | row（每条记录的字段值）                | id、role_id、code_block、create_time、enable、start_time、end_time |
| 执行代码块                 | code_block（代码块字符串）             | 无                                                           |
| 去除代码块开头和结尾的空格 | code_block（原始代码块字符串）         | code_block（去除空格后的代码块字符串）                       |
| 判断代码块类型             | code_block（去除空格后的代码块字符串） | 无                                                           |
| 执行 Python 代码           | code_block（Python 代码块字符串）      | 无                                                           |
| 获取 Python 函数的返回值   | function_name（函数名）                | result（Python 函数的返回值）                                |
| 执行 Lua 代码              | code_block（Lua 代码块字符串）         | 无                                                           |
| 获取 Lua 函数的返回值      | function_name（函数名）                | result（Lua 函数的返回值）                                   |
| 构建监测结果字典           | role_id（角色ID）                      | monitoring_result（监测结果字典）                            |
| 插入监测结果到数据库       | monitoring_result（监测结果字典）      | 无                                                           |
| 处理异常                   | e（异常对象）                          | 无                                                           |

### 插入当日监测表insert_monitoring_result(monitoring_result)

获取到结果后将监测结果字典插入当日分区监测表中.

| 功能                     | 输入                                                      | 输出              |
| ------------------------ | --------------------------------------------------------- | ----------------- |
| 建立数据库连接           | conn_params（数据库连接参数）                             | 无                |
| 创建游标对象             | conn（数据库连接对象）                                    | 无                |
| 使用参数绑定插入监测结果 | monitoring_result（监测结果字典）                         | 无                |
| 构建插入语句             | table_name（目标表名）、monitoring_result（监测结果字典） | query（插入语句） |
| 执行插入语句             | query（插入语句）、monitoring_result（监测结果字典）      | 无                |
| 提交事务                 | conn（数据库连接对象）                                    | 无                |