
import psycopg2
import os
import time
import logging
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
logger = logging.getLogger()

BASE_DIR = '/development/test'

# 插入处理结果到检测表
def insert_detection_result(problem_type, problem_content):
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()

    insert_query = """
    INSERT INTO File_monitortable_2023_06_21 (problem_type, problem_content, query_time)
    VALUES (%s, %s, %s)
    """
    cur.execute(insert_query, (problem_type, problem_content, datetime.now()))

    conn.commit()
    cur.close()
    conn.close()

def process_files():
    processed_files = set()  # 记录已处理的文件集合
    last_timestamp = None
    last_file_name = None

    file_list = os.listdir(BASE_DIR)
    file_list.sort()  # 按文件名排序

    if not file_list:
        logger.warning("No files found in the directory.")
    else:
        for file_name in file_list:
            if file_name in processed_files:
                continue  # 如果文件已处理过，则跳过该文件

            file_path = os.path.join(BASE_DIR, file_name)
            try:
                timestamp = int(file_name.split(".")[0])

                if last_timestamp is not None:
                    time_diff = timestamp - last_timestamp

                    if time_diff > 180:
                        logger.warning("File stopped generating. Last file: %s. Time interval: %s seconds" % (last_file_name, time_diff))
                        problem_type = "stop"
                        problem_content = "File stopped generating. Last file: {}. Time interval: {} seconds".format(last_file_name, time_diff)
                        insert_detection_result(problem_type, problem_content)
                    elif 70 <= time_diff <= 180:
                        logger.warning("Time interval breakpoint detected between %s and %s. Time interval: %s seconds" % (last_file_name, file_name, time_diff))
                        problem_type = "time"
                        problem_content = "Time interval breakpoint detected between {} and {}. Time interval: {} seconds".format(last_file_name, file_name, time_diff)
                        insert_detection_result(problem_type, problem_content)

                last_timestamp = timestamp
                last_file_name = file_name

                processed_files.add(file_name)  # 将处理过的文件加入已处理集合
            except Exception as e:
                logger.error("Error occurred while processing file: {}. Exception: {}".format(file_name, str(e)))

# 监测文件
def monitor_files():
    while True:
        process_files()
        time.sleep(120)  # 每隔120秒进行一次监测


if __name__ == "__main__":
    monitor_files()