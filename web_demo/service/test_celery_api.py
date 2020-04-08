# -*- coding: utf-8 -*-
from pymongo import MongoClient, ASCENDING
from datetime import datetime
from flask import request, jsonify, Blueprint
from common.model import RoomTrumpet
import time
from web_demo import db


test_celery_bp = Blueprint("test_celery_api", __name__)

@test_celery_bp.route("/select", methods=['GET', 'POST'])
def select():
    if request.method == 'GET':
        params = request.args
    else:
        params = request.form
    product_id = params.get('product_id')
    room_trumpet = RoomTrumpet(amount=1,room_id=2,user_id=3)
    db.session.add(room_trumpet)
    # db.session.commit()
    # time.sleep(20)
    return jsonify({"code": 1, "msg": 'Success', "result": product_id})
