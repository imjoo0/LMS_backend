from flask import Flask, g 

# 파일 업로드
from flask_file_upload.file_upload import FileUpload
import config
import pymysql
from flask_wtf.csrf import CSRFProtect  # csrf
from flask_cors import CORS  # CORS 추가

file_upload = FileUpload()
csrf = CSRFProtect()
app = Flask(__name__)

from flask_socketio import SocketIO
socketio = SocketIO()  # asyncio를 사용하기 위해 async_mode를 'asgi'로 설정

# 데이터베이스 연결 설정
def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host=config.Config.DB_HOST,
            user=config.Config.DB_USER,
            password=config.Config.DB_PASSWORD,
            port=config.Config.DB_PORT,
            database=config.Config.DB_DATABASE,
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

# 애플리케이션 종료 시 데이터베이스 연결 닫기
@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# 스케줄러 생성
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from datetime import datetime, timedelta

scheduler = BackgroundScheduler(timezone=timezone('Asia/Seoul'))

# 스케줄러에 작업 추가 매일 오전 12시마다 실행 -> 서버 시간대 utc 라 3으로 변경
@scheduler.scheduled_job('cron', hour='3')
def update_database():
    pydb = get_db()
    cursor = pydb.cursor()
    try:
        with cursor:
            query= "UPDATE taskban LEFT JOIN task on task.id = taskban.task_id SET taskban.done = 0 where task.cycle != 0  or task.category_id = 11;"
            cursor.execute(query)
        pydb.commit()
    except Exception as e:
        print(f"Error: {e}")
        pydb.rollback()
    finally:
        cursor.close()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config) # config.py 파일에 작성한 항목을 읽기 위해
    
    # CORS 설정
    cors = CORS(app, resources={r"/*": {"origins": config.FRONT}})

    # CSRF 설정
    csrf.init_app(app)

    # 파일 업로드 설정
    # file_upload.init_app(app, db)

    # 스케줄러 설정
    # scheduler.start()

    # bp
    from .views import main_views
    app.register_blueprint(main_views.bp)

    from .views import teacher
    app.register_blueprint(teacher.bp)

    from .views import manage
    app.register_blueprint(manage.bp)

    # from .views import admin
    # app.register_blueprint(admin.bp)

    # from .views import common
    # app.register_blueprint(common.bp)

    return app