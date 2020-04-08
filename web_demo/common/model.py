from web_demo import db
from sqlalchemy import Index


class RoomTrumpet(db.Model):
    _id = db.Column(db.Integer, autoincrement=True, primary_key=True)         # 主键
    amount = db.Column(db.Integer,nullable = False,default = 0)               # 消费金额
    room_id = db.Column(db.Integer, nullable=False, default=0)                # 房间id
    user_id = db.Column(db.Integer, nullable=False, default=0)                # 用户id

    __table_args__ = (
        Index('room_id', room_id),
        Index('user_id', user_id),
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8mb4',
        },
    )