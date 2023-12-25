from flask import request, jsonify, Blueprint
from sqlalchemy.sql import text

from web_demo import db

test_celery_bp = Blueprint("test_celery_api", __name__)


@test_celery_bp.route("/select", methods=['GET', 'POST'])
def select():
    if request.method == 'GET':
        params = request.args
    else:
        params = request.form
    second = int(params.get('second'))

    sql = text('create table if not exists trumpet(amount int,user_id int,id int primary key auto_increment);')
    db.session.execute(sql)
    sql = text('insert into trumpet(amount,user_id) values(11,22);')
    db.session.execute(sql)
    # RoomTrumpet.query.filter(RoomTrumpet.amount==1).first()
    # room_trumpet = RoomTrumpet(amount=1,user_id=3)
    # db.session.add(room_trumpet)
    db.session.commit()
    # time.sleep(20)

    # from sync_task.tasks import app as celery_app
    # celery_app.send_task(name='sync_task.tasks.red_package', args=[second])

    return jsonify({"code": 1, "msg": 'Success', "result": second})
