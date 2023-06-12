from flask import Flask, request, jsonify
from psql import log_insert, query_results
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        try:
            # 获取请求参数 date 和 monitoring_type
            date = request.args.get('date')
            monitoring_type = request.args.get('monitoring_type')
        except:
            # 处理异常情况并记录日志
            log_insert("route", "failed")
            return jsonify({'error': 'No input'})

    elif request.method == 'POST':
        try:
            # 获取请求参数 date 和 monitoring_type
            data = request.get_json()
            date = data['date']
            monitoring_type = data['monitoring_type']
        except:
            # 处理异常情况并记录日志
            log_insert("route", "failed")
            return jsonify({'error': 'Invalid input'})

    else:
        # 返回不支持的请求方法
        return jsonify({'error': 'Method not allowed'})

    # 执行查询操作
    rows = query_results(date, monitoring_type)

    if rows is not None:
        # 查询结果不为空，记录成功日志并返回结果
        log_insert("route", "success")
        return jsonify({'data': rows})
    elif rows == []:
        # 查询结果为空列表，记录结果为空日志并返回结果
        log_insert("route", "result None")
        return jsonify({'data': rows})
    else:
        # 查询失败，记录失败日志并返回提示信息
        log_insert("route", "failed")
        return jsonify({'error': 'No results'})

if __name__ == '__main__':
    # 启动应用程序并监听端口 5001
    app.run(port=5001)
