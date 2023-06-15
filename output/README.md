# 启动方式
<strong>功能：启动output组件</strong>

在output路径下运行<strong>./start.sh</strong>启动，有个小问题启动后ctrl+c无法终止streamlit和celery

涉及文件：[start.sh](./start.sh)

<strong>关键代码</strong>

```bash
# 执行命令并保存进程 PID
streamlit run streamlit.py --server.port=8888 --server.address=0.0.0.0 --browser.gatherUsageStats=false --server.enableCORS=false --server.enableXsrfProtection=false &
pids+=("$!")

python route.py &
pids+=("$!")

celery -A proj.tasks worker --loglevel=info &
pids+=("$!")

celery -A proj.tasks beat --loglevel=info &
pids+=("$!")
```

# 具体模块解释

## streamlit

<strong>功能：输入日期和类型（url，path，sql）查询分区表中的数据</strong>

涉及文件： [streamlit.py](./streamlit.py)

```bash
streamlit run streamlit.py --server.port=8888 --server.address=0.0.0.0 --browser.gatherUsageStats=false --server.enableCORS=false --server.enableXsrfProtection=false
```

运行端口： http://127.0.0.1:8888



## flask

<strong>功能：登陆，注册，webhook，search</strong>

涉及文件：[route.py](./route.py)

```bash
python route.py
```

运行端口：http://127.0.0.1:5000

路由(post,get)：

| 路由      | 功能                                     | 输入                                                    | 输出                                        |
| --------- | ---------------------------------------- | ------------------------------------------------------- | ------------------------------------------- |
| /register | 用户注册                                 | username,passwd                                         | 注册成功或用户名已存在的消息                |
| /login    | 用户登录                                 | username,passwd                                         | 登录成功写入cookie或用户名或密码错误的消息, |
| /webhook  | Webhook处理，<strong>需要先登录</strong> | check_type('url','path','sql'),headers.cookie(自动获取) | 最新的结果                                  |
| /search   | 查询操作                                 | date(2023-06-14),monitoring_type('url','path','sql')    | 查询结果或查询失败的消息                    |
| /metrics  | 获取指标数据                             | 无                                                      | 监控指标数据                                |

## Celery

<strong>功能：定时将分区表中数据记录到对应表中</strong>

涉及文件：[func.py](./proj/func.py) [task.py](./proj/task.py) [celery_config.py](./proj/celery_config.py)

```bash
celery -A proj.tasks worker --loglevel=info &
celery -A proj.tasks beat --loglevel=info
```

### `tasks.py`

`tasks.py` 文件包含了任务相关的代码，主要包括以下功能：

1. 导入必要的模块和库：从 `proj.tasks` 导入 `app` 对象、导入 `psycopg2` 库用于与 PostgreSQL 数据库进行交互、导入 `datetime` 库用于处理日期和时间相关的操作。
2. 定义数据库查询函数 db_select(query)：
   - 该函数接收一个查询语句作为参数，使用 `psycopg2` 建立与 PostgreSQL 数据库的连接。
   - 执行查询语句并获取查询结果的所有行。
   - 关闭数据库连接并返回查询结果。
3. 定义数据库插入函数 db_insert(params):：
   - 该函数接收插入参数 `params`，使用 `psycopg2` 建立与 PostgreSQL 数据库的连接。
   - 执行插入语句将参数插入到 `check_output` 表中。
   - 提交事务并关闭数据库连接。
4. 定义 Celery 任务 push()：
   - 使用 `datetime` 获取当前时间，并根据时间生成不同的表名和时间范围。
   - 构建查询语句，查询指定时间范围内的数据。
   - 调用 `db_select()` 执行查询，获取查询结果。
   - 进行数据处理，统计符合条件的行数和对应的 ID。
   - 根据结果构建插入参数，调用 `db_insert()` 插入数据。
   - 返回执行结果。

### `celery.py`

`celery.py` 文件主要用于配置 Celery 应用和定时任务的调度计划，具体功能如下：

1. 导入必要的模块和类：导入 `Celery` 类和 `crontab` 类。
2. 创建 Celery 应用对象 app：
   - 使用 `Celery` 类创建一个名为 `proj` 的 Celery 应用对象。
   - 通过 `include` 参数指定需要包含的任务模块，这里是 `proj.func`。
3. 通过配置对象加载 Celery 应用配置：
   - 使用 `config_from_object` 方法从指定的配置对象中加载 Celery 应用的配置信息。
   - 假设配置对象的路径是 `proj.celery_config`。
4. 配置定时任务的调度计划：
   - 使用 `app.conf.beat_schedule` 字典定义定时任务的调度计划。
   - 创建一个名为 `"scheduled_push"` 的定时任务，指定要执行的任务名称和执行时间表。
   - 任务名称为 `"proj.func.push"`，表示要执行名为 `push` 的任务。
   - 时间表使用 `crontab` 类设置为每隔一分钟执行一次，即 `crontab(minute="*/1")`。

通过以上功能，`tasks.py` 中的任务代码被定义和实现，`celery.py` 中的配置代码将定时任务调度计划与 Celery 应用关联起来。这样，可以实现每隔一分钟执行一次 `push()` 任务的定时任务。

### `celery_config.py`

```python
BROKER_URL = 'redis://:****@redis-master'    # 使用Redis作为消息代理

CELERY_RESULT_BACKEND = 'redis://:****@redis-master:****/0'  # 把任务结果存在了Redis

## CELERY_TASK_SERIALIZER = 'msgpack'  # 任务序列化和反序列化使用msgpack方案

## CELERY_RESULT_SERIALIZER = 'json'   # 读取任务结果一般性能要求不高，所以使用了可读性更好的JSON

## CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24   # 任务过期时间，不建议直接写86400，应该让这样的magic数字表述更明显

## CELERY_ACCEPT_CONTENT = ['json', 'msgpack']     # 指定接受的内容类型

CELERYD_CONCURRENCY = 10    # 并发worker数
```

## 其他

### 数据库

[create.sql](./create.sql)

**check_output**  定时任务记录文件

| 列名       | 类型      | 约束 | 描述       |
| ---------- | --------- | ---- | ---------- |
| id         | SERIAL    | 主键 | 唯一标识符 |
| check_time | TIMESTAMP | 非空 | 检查时间   |
| result     | TEXT      | 非空 | 检查结果   |
| details    | TEXT      | 非空 | 检查详情   |

**check_output_log**  日志文件

| 列名        | 类型         | 约束 | 描述       |
| ----------- | ------------ | ---- | ---------- |
| id          | SERIAL       | 主键 | 唯一标识符 |
| output_type | VARCHAR(100) | 非空 | 输出类型   |
| result      | TEXT         | 非空 | 检查结果   |
| state_time  | TIMESTAMP    | 非空 | 状态时间   |

**users_table**  用户表

| 列名     | 类型         | 约束 | 描述       |
| -------- | ------------ | ---- | ---------- |
| id       | SERIAL       | 主键 | 唯一标识符 |
| username | VARCHAR(100) | 非空 | 用户名     |
| passwd   | VARCHAR(100) | 非空 | 密码       |
| cookie   | VARCHAR(100) | 非空 | Cookie 值  |

**users_status**  用户查询信息记录表

| 列名       | 类型         | 约束 | 描述           |
| ---------- | ------------ | ---- | -------------- |
| id         | SERIAL       | 主键 | 唯一标识符     |
| check_type | VARCHAR(100) | 非空 | 检查类型       |
| cookie     | VARCHAR(100) | 非空 | Cookie 值      |
| state_time | TIMESTAMP    | 非空 | 上次查询的时间 |

### 数据库操作函数

[psql.py](./psql.py)  主要供flask板块使用

| 函数名                                       | 功能                                 | 输入参数                                                     | 输出参数                                   |
| -------------------------------------------- | ------------------------------------ | ------------------------------------------------------------ | ------------------------------------------ |
| connect_to_pg()                              | 连接到PG数据库                       | 无                                                           | 数据库连接对象                             |
| generate_cookie(length=32)                   | 生成指定长度的随机字符串作为Cookie   | length: Cookie长度，默认为32                                 | 生成的Cookie                               |
| register(username, passwd)                   | 用户注册函数                         | username: 用户名<br>passwd: 用户密码                         | 注册结果，1表示成功注册，0表示用户名已存在 |
| login(username, passwd)                      | 用户登录函数                         | username: 用户名<br>passwd: 用户密码                         | 登录结果，返回用户的Cookie，0表示登录失败  |
| log_insert(type, result)                     | 将日志信息插入到check_output_log表中 | type: 日志类型<br>result: 日志结果                           | 无                                         |
| query_results(date, monitoring_type, mode=1) | 查询监测结果                         | date: 日期（字符串格式）<br>monitoring_type: 监测类型<br>mode: 查询模式，0表示按日期和监测类型查询，1表示仅按监测类型查询（默认为1） | 查询结果，返回查询到的行的列表             |
| get_name(cookie)                             | 根据Cookie获取用户名                 | cookie: 用户的Cookie                                         | 用户名，如果不存在对应的用户则返回None     |
| get_content(cookie, check_type)              | 根据Cookie和监测类型获取监测结果     | cookie: 用户的Cookie<br>check_type: 监测类型                 | 监测结果，返回查询到的行的列表             |
