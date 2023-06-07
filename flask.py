from flask import Flask, render_template, request
import psycopg2
app = Flask(__name__)

@app.route('/search',methods = ['GET','POST'])
def search():
    try:
        date = request.args.get('date')
        monitoring_type = request.args.get('monitoring_type')
    except:
         return 0
    connection = psycopg2.connect(
        host="10.68.48.67",
        port="5432",
        database="postgres",
        user="postgres",
        password="root"
    )
    cursor = connection.cursor()
    # 假设您的监测结果存储在名为"monitoring_results"的表中，包含date、status和content列
    query = "SELECT * FROM monitoring_results WHERE date = %s AND monitoring_type = %s"
    params = (date, monitoring_type)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows


if __name__ == '__main__':
    app.run()