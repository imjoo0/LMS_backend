from LMSapp.views import *
from flask import session  # 세션
from flask import Blueprint, render_template, jsonify, request, redirect, url_for
import json
import callapi
import pymysql
import requests
from urllib.parse import unquote
from datetime import datetime, timedelta, date
import pytz
from urllib.parse import quote
from flask_socketio import join_room, emit
from LMSapp import socketio

bp = Blueprint('manage', __name__, url_prefix='/manage')