#!/bin/bash

# 保存命令进程的 PID
pids=()

# 设置信号处理器，捕获 SIGINT 和 SIGTERM 信号
trap "cleanup" SIGINT SIGTERM

# 命令关闭时的操作
cleanup() {
    # 发送 SIGTERM 信号终止命令进程
    for pid in "${pids[@]}"; do
        kill -TERM "$pid"
    done
    echo "命令已关闭"
    exit 0
}

# 执行命令并保存进程 PID
streamlit run streamlit.py --server.port=16593 --server.address=0.0.0.0 --browser.gatherUsageStats=false --server.enableCORS=false --server.enableXsrfProtection=false &
pids+=("$!")

python route.py &
pids+=("$!")

celery -A proj.tasks worker --loglevel=info &
pids+=("$!")

celery -A proj.tasks beat --loglevel=info &
pids+=("$!")