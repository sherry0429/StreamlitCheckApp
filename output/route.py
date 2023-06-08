from flask import Flask, request
from psql import log_insert,query_results
from prometheus_flask_exporter import PrometheusMetrics


app = Flask(__name__)
metrics = PrometheusMetrics(app)

@app.route('/search',methods = ['GET'])
def search():
    try:
        date = request.args.get('date')
        monitoring_type = request.args.get('monitoring_type')
    except:
        log_insert("route","failed")
        return "No input"
    rows = query_results(date,monitoring_type)
    if rows is not None:
        log_insert("route","success")
        return str(rows)
    elif rows == []:
        log_insert("route","result None")
        return str(rows)
    else:
        log_insert("route","failed")
        return "No results"



if __name__ == '__main__':
    app.run(port=5001)