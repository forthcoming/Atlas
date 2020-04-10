# -*- coding: utf-8 -*-
from datetime import datetime
from flask import request, jsonify, Blueprint
from web_demo.common.model import RoomTrumpet
import time
from web_demo import db,app
from sync_task.tasks import app as celery_app

test_celery_bp = Blueprint("test_celery_api", __name__)
app.register_blueprint(test_celery_bp,url_prefix='/ccktv/v1/test_celery/')

@test_celery_bp.route("/select", methods=['GET', 'POST'])
def select():
    if request.method == 'GET':
        params = request.args
    else:
        params = request.form
    product_id = params.get('product_id')
    # room_trumpet = RoomTrumpet(amount=1,room_id=2,user_id=3)
    # db.session.add(room_trumpet)
    # db.session.commit()
    # time.sleep(20)

    celery_app.send_task(name='tasks.red_package')

    return jsonify({"code": 1, "msg": 'Success', "result": product_id})
