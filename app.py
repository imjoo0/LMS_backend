from flask import Flask, request, jsonify, session
from flask_cors import CORS
import config

from LMSapp import create_app, socketio

if __name__ == '__main__':
    app = create_app()
    # CORS 설정
    cors = CORS(app, resources={r"/*": {"origins": config.FRONT}})
        # socketio.init_app(app, async_mode='eventlet')  # asyncio를 사용하기 위해 async_mode를 'eventlet_asyncio'로 설정
    app.run(host='0.0.0.0', port='2305', debug=True)
