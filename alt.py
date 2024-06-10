from bottle import route, run

@route('/')
def hello_world():
    return 'Hello, World!'

run(host='127.0.0.1', port=8080)
