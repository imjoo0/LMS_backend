import callapi
from LMSapp.views import *
import json
from flask import current_app, session, g 
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from datetime import datetime, timedelta, date
import pytz

# file-upload 로 자동 바꿈 방지 모듈
# from LMSapp.views import common
import requests 
import sys
import pandas as pd
from urllib.parse import quote
from flask_socketio import join_room, emit
from LMSapp import socketio, get_db

bp = Blueprint('teacher', __name__, url_prefix='/teacher')

# 전체 학생 데이터
@bp.route('/get_students_data/<int:userId>', methods=['GET'])
def get_students_data(userId):
    all_students = callapi.call_api(userId, 'get_mystudents_new')
    return jsonify({'all_students':all_students})

# 미학습 데이터 
@bp.route('/get_unlearned_data/<int:userId>', methods=['GET'])
def get_unlearned_data(userId):
    unlearned_consulting = []
    ban_data = callapi.call_api(userId, 'get_mybanid')
    # takeovers = TakeOverUser.query.filter(TakeOverUser.teacher_id == userId).all()
    # takeovers_num = len(takeovers)
    # if takeovers_num != 0 :
    #     for takeover in takeovers:
    #         ban_data += callapi.call_api(takeover.takeover_user, 'get_mybans_new')
    #         all_students += callapi.call_api(takeover.takeover_id, 'get_mystudents_new')
    db = get_db()
    cur = db.cursor()
    try:
        with cur:
            for ban in ban_data:
                 # 상담 해야 하는 날짜가 오늘 이상인 경우 , 내가 담당한 반의 consulting 기록들을 가져옵니다 
                # 상담 요청일(startdate)가 반 시작일 ban['startdate']값보다 커야 합니다 .
                #  consulting.cateogry_id < 100 = 미학습 상담 ( 자동 생성 )
                # 상담 중 진행하지 않은 미학습 상담 기록만 가져옵니다 
                # 미학습 상담의 경우 반 시작일 전에 생성된 경우는 제외 합니다.
                cur.execute('''
                SELECT consulting.origin, consulting.student_name, consulting.student_engname, consulting.id, consulting.ban_id, consulting.student_id, consulting.done, consultingcategory.id as category_id, consulting.week_code, consultingcategory.name as category, consulting.contents, consulting.startdate, consulting.deadline, consulting.missed, consulting.created_at, consulting.reason, consulting.solution, consulting.result
                FROM consulting
                LEFT JOIN consultingcategory ON consulting.category_id = consultingcategory.id
                WHERE (consulting.category_id < 100 AND consulting.done = 0 AND %s <= consulting.startdate AND consulting.startdate <= curdate() and consulting.ban_id=%s)
                ''',({ban['startdate']},ban['ban_id']) )
                unlearned_consulting.extend(cur.fetchall())  
    except:
        print('err:', sys.exc_info())
    finally:
        cur.close()
    return jsonify({'unlearned_consulting':unlearned_consulting})

# 업무 데이터 
@bp.route('/get_task_data/<int:userId>', methods=['GET'])
def get_task_data(userId):
    current_time = datetime.utcnow()
    korea_timezone = pytz.timezone('Asia/Seoul')
    korea_time = current_time + timedelta(hours=9)
    korea_time = korea_timezone.localize(korea_time)
    Today = korea_time.date()
    today_yoil = korea_time.weekday() + 1
    standard = datetime.strptime('11110101', "%Y%m%d").date()
    
    student_task = []
    ban_task = []

    ban_data = callapi.call_api(userId, 'get_mybanid')

    # takeovers = TakeOverUser.query.filter(TakeOverUser.teacher_id == userId).all()
    # takeovers_num = len(takeovers)
    # if takeovers_num != 0 :
    #     for takeover in takeovers:
    #         ban_data += callapi.call_api(takeover.takeover_user, 'get_mybans_new')
    #         all_students += callapi.call_api(takeover.takeover_id, 'get_mystudents_new')
    
    db = get_db()
    cur = db.cursor()
    try:
        with cur:
            for ban in ban_data:
                # 본원에서 요청한 학생 상담을 업무로 가져옵니다 
                # 본원 요청 업무 : week_code < 0
                # 오늘 완료한 경우 가져옵니다 
                # 완료하지 않은 경우 가져옵니다
                cur.execute('''
                SELECT consulting.origin, consulting.student_name, consulting.student_engname, consulting.id, consulting.ban_id, consulting.student_id, consulting.done, consultingcategory.id as category_id, consulting.week_code, consultingcategory.name as category, consulting.contents, consulting.startdate, consulting.deadline, consulting.missed, consulting.created_at, consulting.reason, consulting.solution, consulting.result
                FROM consulting
                LEFT JOIN consultingcategory ON consulting.category_id = consultingcategory.id
                WHERE (consulting.week_code < 0 AND consulting.startdate <= curdate() AND consulting.ban_id=%s)
                AND ( (consulting.done = 0) OR (consulting.done = 1 AND consulting.created_at = CURDATE()) )
                ''', (ban['ban_id']))
                student_task.extend(cur.fetchall())  

                # 반 업무의 경우엔, task의 category 가 11 이라 상시 업무 인 경우 
                # 업무 cycle 이 오늘 요일이 된 경우 
                # 업무의 startdate가 오늘 이상인 경우 이고 deadline 을 넘기지 않은 경우 
                # 오늘 완수한 업무이거나 done이 0인 경우
                cur.execute('''
                select taskban.id,taskban.ban_id, taskcategory.name as category, task.contents, task.deadline,task.priority,taskban.done,taskban.created_at 
                from taskban 
                left join task on taskban.task_id = task.id 
                left join taskcategory on task.category_id = taskcategory.id 
                where ( (task.category_id = 11) or ( (task.cycle = %s) or (task.cycle = 0) ) ) and ( task.startdate <= curdate() and curdate() <= task.deadline ) and taskban.ban_id=%s
                AND ( (taskban.done = 1 AND DATE(taskban.created_at) = CURDATE()) OR taskban.done = 0 );''', (today_yoil,ban['ban_id']))
                ban_task.extend(cur.fetchall())  
    except:
        print('err:', sys.exc_info())
    finally:
        cur.close()
    return jsonify({'ban_data':ban_data,'ban_task':ban_task,'student_task':student_task})
