from flask import Flask, request, jsonify, session
from flask_cors import CORS

from LMSapp import create_app, socketio

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        socketio.init_app(app, async_mode='eventlet')  # asyncio를 사용하기 위해 async_mode를 'eventlet_asyncio'로 설정
        socketio.run(app, host='0.0.0.0', port='2305', debug=True)
