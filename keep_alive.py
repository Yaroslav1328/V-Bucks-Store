from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

@app.route('/favicon.ico')
def favicon():
    return '', 204  # Заглушка, чтобы не было ошибки 404 в логах

def run():
    port = os.environ.get('PORT', 8080)  # используем PORT из окружения, если он есть
    app.run(host='0.0.0.0', port=int(port))

def keep_alive():
    t = Thread(target=run)
    t.start()
