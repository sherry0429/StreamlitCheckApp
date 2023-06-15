from flask import Flask, request, jsonify, make_response, Response
from psql import log_insert, query_results,register,login,get_content,get_name
import pycurl
import time
from io import BytesIO
from prometheus_client.core import CollectorRegistry
from prometheus_client import Gauge, generate_latest

app = Flask(__name__)


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'GET':
        try:
            # 获取请求参数 date 和 monitoring_type
            username = request.args.get('username')
            passwd = request.args.get('passwd')
        except:
            # 处理异常情况并记录日志
            log_insert("flask register", "failed")
            return jsonify({'error': 'No input'})

    elif request.method == 'POST':
        try:
            # 获取请求参数 date 和 monitoring_type
            data = request.get_json()
            username = data['username']
            passwd = data['passwd']
        except:
            # 处理异常情况并记录日志
            log_insert("flask register", "failed")
            return jsonify({'error': 'Invalid input'})

    else:
        # 返回不支持的请求方法
        return jsonify({'error': ' Register Method not allowed'})
    res = register(username,passwd)
    if res:
        log_insert("flask register","user %s register" % username)
        return 'ok'
    else:
        return 'username exited'
    
@app.route('/login', methods=['GET', 'POST'])
def login_user():
    if request.method == 'GET':
        try:
            # 获取请求参数 date 和 monitoring_type
            username = request.args.get('username')
            passwd = request.args.get('passwd')
        except:
            # 处理异常情况并记录日志
            log_insert("flask login", "failed")
            return jsonify({'error': 'No input'})

    elif request.method == 'POST':
        try:
            # 获取请求参数 date 和 monitoring_type
            data = request.get_json()
            username = data['username']
            passwd = data['passwd']
        except:
            # 处理异常情况并记录日志
            log_insert("flask login", "failed")
            return jsonify({'error': 'Invalid input'})

    else:
        # 返回不支持的请求方法
        return jsonify({'error': ' Register Method not allowed'})
    cookie = login(username,passwd)
    if cookie:
        log_insert("flask login","user %s login" % username)
        resp = make_response("login success")
        resp.set_cookie('Cookie', cookie)
        return resp
    else:
        log_insert("flask login","login failed")
        return "username or passwd error!"


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        try:
            # 获取请求参数 date 和 monitoring_type
            check_type = request.args.get('check_type')
        except:
            # 处理异常情况并记录日志
            log_insert("webhoook", "failed")
            return jsonify({'error': 'No input'})

    elif request.method == 'POST':
        try:
            # 获取请求参数 date 和 monitoring_type
            data = request.get_json()
            check_type = data['check_type']
        except:
            # 处理异常情况并记录日志
            log_insert("webhook", "failed")
            return jsonify({'error': 'Invalid input'})

    else:
        # 返回不支持的请求方法
        return jsonify({'error': 'Method not allowed'})
    cookie = request.headers.get('Cookie')
    if cookie:
        cookie = cookie.split('=')[1]
        username = get_name(cookie)
        if username:
            res = get_content(cookie,check_type)
            log_insert('webhook',('user %s get %s nums %s' % (username,check_type,len(res))))
            return res
        else:
            return jsonify({'error': 'Invalid login'})
    else:   
        return jsonify({'error': 'Not login'})


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        try:
            # 获取请求参数 date 和 monitoring_type
            date = request.args.get('date')
            monitoring_type = request.args.get('monitoring_type')
        except:
            # 处理异常情况并记录日志
            log_insert("flask search", "failed")
            return jsonify({'error': 'No input'})

    elif request.method == 'POST':
        try:
            # 获取请求参数 date 和 monitoring_type
            data = request.get_json()
            date = data['date']
            monitoring_type = data['monitoring_type']
        except:
            # 处理异常情况并记录日志
            log_insert("flask search", "failed")
            return jsonify({'error': 'Invalid input'})

    else:
        # 返回不支持的请求方法
        return jsonify({'error': 'Method not allowed'})

    # 执行查询操作
    rows = query_results(date, monitoring_type)

    if rows is not None:
        # 查询结果不为空，记录成功日志并返回结果
        log_insert("flask search", "date:%s, type:%s, nums:%s" % (date,monitoring_type,len(rows)))
        return jsonify({'data': rows})
    elif rows == []:
        # 查询结果为空列表，记录结果为空日志并返回结果
        log_insert("flask search", "result None")
        return jsonify({'data': rows})
    else:
        # 查询失败，记录失败日志并返回提示信息
        log_insert("flask search", "failed")
        return jsonify({'error': 'No results'})


def get_site_status(url):
    data = {'namelookup_time': 0, 'connect_time': 0, 'pretransfer_time': 0,
            'starttransfer_time': 0, 'total_time': 0, 'http_code': 444,
            'size_download': 0, 'header_size': 0, 'speed_download': 0, 'content':''}
    html = BytesIO()
    c = pycurl.Curl()

    c.setopt(pycurl.URL, url)
    # 请求连接的等待时间
    c.setopt(pycurl.CONNECTTIMEOUT, 5)
    # 请求超时时间
    c.setopt(pycurl.TIMEOUT, 5)
    # 屏蔽下载进度条
    c.setopt(pycurl.NOPROGRESS, 1)
    # 完成交互后强制断开连接，不重用
    c.setopt(pycurl.FORBID_REUSE, 1)
    # 指定 HTTP 重定向的最大数为 1
    c.setopt(pycurl.MAXREDIRS, 1)
    # 设置保存 DNS 信息的时间为 10 秒
    c.setopt(pycurl.DNS_CACHE_TIMEOUT, 10)
    # 设置是否验证HTTP证书
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    # 把 response body 存在 html 变量里，不输出到终端
    c.setopt(pycurl.WRITEFUNCTION, html.write)
    try:
        c.perform()
        # 变量含义，参考文档：https://curl.haxx.se/libcurl/c/curl_easy_getinfo.html
        # 获取 DNS 解析时间，单位 秒(s)
        namelookup_time = c.getinfo(c.NAMELOOKUP_TIME)
        # 获取建立连接时间，单位 秒(s)
        connect_time = c.getinfo(c.CONNECT_TIME)
        # 获取从建立连接到准备传输所消耗的时间，单位 秒(s)
        pretransfer_time = c.getinfo(c.PRETRANSFER_TIME)
        # 获取从建立连接到传输开始消耗的时间，单位 秒(s)
        starttransfer_time = c.getinfo(c.STARTTRANSFER_TIME)
        # 获取传输的总时间，单位 秒(s)
        total_time = c.getinfo(c.TOTAL_TIME)
        # 获取 HTTP 状态码
        http_code = c.getinfo(c.HTTP_CODE)
        # 获取下载数据包大小，单位 bytes
        size_download = c.getinfo(c.SIZE_DOWNLOAD)
        # 获取 HTTP 头部大小，单位 byte
        header_size = c.getinfo(c.HEADER_SIZE)
        # 获取平均下载速度，单位 bytes/s
        speed_download = c.getinfo(c.SPEED_DOWNLOAD)
        c.close()
        data = dict(namelookup_time=namelookup_time * 1000, connect_time=connect_time * 1000,
                    pretransfer_time=pretransfer_time * 1000, starttransfer_time=starttransfer_time * 1000,
                    total_time=total_time * 1000, http_code=http_code,
                    size_download=size_download, header_size=header_size,
                    speed_download=speed_download)
    # 如果站点无法访问，捕获异常，并使用前面初始化的字典 data 的值
    except Exception as e:
        print ("{} connection error: {}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), str(e)))
        c.close()
    return data


# 设置 metrics
registry = CollectorRegistry(auto_describe=False)
namelookup_time = Gauge('namelookup_time', 'namelookup time', ['url'], registry=registry)
connect_time = Gauge('connect_time', 'connect time', ['url'], registry=registry)
pretransfer_time = Gauge('pretransfer_time', 'pretransfer time time', ['url'], registry=registry)
starttransfer_time = Gauge('starttransfer_time', 'starttransfertime time', ['url'], registry=registry)
total_time = Gauge('total_time', 'total time', ['url'], registry=registry)
size_download = Gauge('size_download', 'size download', ['url'], registry=registry)
header_size = Gauge('header_size', 'header size', ['url'], registry=registry)
speed_download = Gauge('speed_download', 'speed download', ['url'], registry=registry)
http_code = Gauge('http_code', 'http code', ['url'], registry=registry)


@app.route("/metrics",methods=('GET','POST'))
def metrics():
    res = {'urls':['http://127.0.0.1:5001/search','http://127.0.0.1:5001/login','http://127.0.0.1:5001/register','http://127.0.0.1:8888']}
    for url in res['urls']:
        data = get_site_status(url)
        for key, value in data.items():
            if key == 'namelookup_time':
                namelookup_time.labels(url=url).set(float(value))
            elif key == 'connect_time':
                connect_time.labels(url=url).set(float(value))
            elif key == 'pretransfer_time':
                pretransfer_time.labels(url=url).set(float(value))
            elif key == 'starttransfer_time':
                starttransfer_time.labels(url=url).set(float(value))
            elif key == 'total_time':
                total_time.labels(url=url).set(float(value))
            elif key == 'size_download':
                size_download.labels(url=url).set(float(value))
            elif key == 'header_size':
                header_size.labels(url=url).set(float(value))
            elif key == 'speed_download':
                speed_download.labels(url=url).set(float(value))
            elif key == 'http_code':
                http_code.labels(url=url).set(int(value))
    return Response(generate_latest(registry), mimetype="text/plain")



if __name__ == '__main__':
    # 启动应用程序并监听端口 5001
    app.run(port=5001)
