from flask import Blueprint, jsonify, request, url_for, session
from flask_wtf.csrf import generate_csrf
from LMSapp import get_db

import jwt
import hashlib
import config

bp = Blueprint('main', __name__, url_prefix='/')
SECRET_KEY = config.SECRET_KEY

@bp.app_errorhandler(400)
def handle_bad_request(e):
    print(e)
    return jsonify({'result':'fail', 'msg': e}), 400

@bp.route('/get_csrf_token', methods=['GET'])
def get_csrf_token():
    session['csrf_token'] = generate_csrf()  # 세션에 CSRF 토큰 저장
    print("Received CSRF Token:", session['csrf_token'])
    return jsonify(csrf_token=session['csrf_token'])

@bp.route('/login', methods=['POST'])
def login():
    print('here')
    import pdb ; pdb.set_trace()
    csrf_token_from_client = request.headers.get('X-CSRFToken')
    server_csrf_token = session.get('csrf_token')
    if csrf_token_from_client != server_csrf_token:
        print(f"Client CSRF Token: {csrf_token_from_client}")
        print(f"Server CSRF Token: {server_csrf_token}")
        return jsonify({'result':'fail', 'msg': 'Invalid CSRF token'}), 400
    print('here')
    data = request.get_json()
    print(data)
    user_id = data.get('user_id')
    user_pw = data.get('user_pw')
    hashed_pw = hashlib.sha256(user_pw.encode('utf-8')).hexdigest()
    
    db = get_db()
    cursor = db.cursor()
    try:
        with cursor:
            cursor.execute('''
            SELECT id, user_id, user_pw, name, eng_name, mobileno, email, category
            FROM user
            WHERE user_id=%s and user_pw =%s
            ''',(user_id,hashed_pw) )
            result = cursor.fetchone()
    except:
        print('err:', sys.exc_info())
    finally:
        cursor.close()
    if result is not None:
        payload = {
            'user_id': result['user_id'],
            'id': result['id'],
            'category': result['category']
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        # 사용자 정보를 세션에 저장
        session['user_id'] = user_id
        return jsonify({'result': result, 'token': token})
    else:
        return jsonify({'result':'fail', 'msg': 'id, pw 를 확인해주세요'})

# 로그아웃 API
@bp.route("logout", methods=['GET'])
def logout():
    # 세션에서 사용자 정보 삭제
    session.pop('user_id', None)
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return jsonify({
            'result': 'success',
            'token': jwt.encode(payload, SECRET_KEY, algorithm='HS256'),
            'msg': '로그아웃 성공'
        })
    except jwt.ExpiredSignatureError or jwt.exceptions.DecodeError:
        return jsonify({
            'result': 'fail',
            'msg': '로그아웃 실패'
        })