# health_check.py
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def health_check():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def start_health_check():
    t = Thread(target=run)
    t.start()