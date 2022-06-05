from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello https!!!"

if __name__ == '__main__':
    app.run(port=4443, ssl_context=('server.crt', 'server.key'))
