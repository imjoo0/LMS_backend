from flask import Flask, request, jsonify, session
from flask_cors import CORS

import hashlib
import jwt
import pymysql

# from flask_session import Session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdfasdfasdfqwerty'
app.config['SESSION_TYPE'] = 'filesystem'  # 세션 저장 방식 설정
# Session(app)

cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def hello():
    return 'Hello, Flask!'

@app.route('/login', methods=['POST'])
def sign_in():
    data = request.get_json()
    user_id = data.get('user_id')
    user_pw = data.get('user_pw')
    hashed_pw = hashlib.sha256(user_pw.encode('utf-8')).hexdigest()
    db = pymysql.connect(host='127.0.0.1', user='purple', password='wjdgus00',port=3306, database='LMS', cursorclass=pymysql.cursors.DictCursor)
    try:
        with db.cursor() as cur:
            cur.execute('''
            SELECT id, user_id, user_pw, name, eng_name, mobileno, email, category
            FROM user
            WHERE user_id=%s and user_pw =%s
            ''',(user_id,hashed_pw, ) )
            result = cur.fetchone()
    except:
        print('err:', sys.exc_info())
    finally:
        db.close()
    print(result)
    if result is not None:
        payload = {
            'user_id': result['user_id'],
            'id': result['id'],
            'category': result['category']
        }
        token = jwt.encode(payload, 'asdfasdfasdfqwerty', algorithm='HS256')
        session['user_id'] = result['user_id']
        session['mytoken'] = token
        return jsonify({'result': result, 'token': token})
    else:
        return jsonify({'result':'fail', 'msg': 'id, pw 를 확인해주세요'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2305, debug=True)