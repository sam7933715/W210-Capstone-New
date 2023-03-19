from flask import Flask
# Flask 為一個建置在Flask Package 內的Class, 以下建立一個Flask物件，命名為app
app = Flask(__name__, static_url_path='', static_folder='')
# static_url_path=''設定前綴網域，例如: static_url_path='/abc'，代表整個網站原先的ip url後都要在加上/abc
# static_folder=''設定根目錄
@app.route('/') # 設定網頁路徑
def root():
    return app.send_static_file('index.html')

# Router of a test API
@app.route('/api')
def hello_world():
    data = """ {
       "name":"123",
        "age":20
    } """
    return json.loads(data)

# Router of a test API
@app.route('/test')  # api route
def test():
    print("test")
    return "test"