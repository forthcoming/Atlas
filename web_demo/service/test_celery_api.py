# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint

test_celery_bp = Blueprint("test_celery_api", __name__)


@test_celery_bp.route("/select", methods=['GET', 'POST'])
def select():
    if request.method == 'GET':
        params = request.args
    else:
        params = request.form
    second = int(params.get('second'))

    # db.session.execute('insert into room_trumpet(amount,room_id,user_id) values(11,22,33);')
    # RoomTrumpet.query.filter(RoomTrumpet.amount==1).first()
    # room_trumpet = RoomTrumpet(amount=1,room_id=2,user_id=3)
    # db.session.add(room_trumpet)
    # db.session.commit()
    # time.sleep(20)

    from sync_task.tasks import app as celery_app
    celery_app.send_task(name='sync_task.tasks.red_package', args=[second])

    return jsonify({"code": 1, "msg": 'Success', "result": second})
