from multiprocessing import Process
import time
from multiprocessing.dummy import Process as Thread

def main():
    from web_demo import db
    connection_id = 0
    print('main: connection_id:{}, status:{}'.format(connection_id, db.engine.pool.status()))
    connection_id = db.engine.execute('select connection_id();').first()[0]
    db.engine.execute('select 1 from room_trumpet;')
    print('main: connection_id:{}, status:{}'.format(connection_id, db.engine.pool.status()))
    program = Process(target=kid, args=(db,))
    program.start()
    for idx in range(15):
        try:
            time.sleep(1)
            connection_id = db.engine.execute('select connection_id();').first()[0]
            print('main_{}: connection_id:{}, status:{}'.format(idx,connection_id, db.engine.pool.status()))
        except Exception as e:
            print(e)

def kid(db):
    db.engine.dispose()
    connection_id = 0
    print('kid : connection_id:{}, status:{}'.format(connection_id, db.engine.pool.status()))
    threadings = [Thread(target=work,args=(db,)) for i in range(2)]
    for thread in threadings:
        thread.start()
    for thread in threadings:
        thread.join()
    connection_id = db.engine.execute('select connection_id();').first()[0]
    print('kid : connection_id:{}, status:{}'.format(connection_id, db.engine.pool.status()))
    time.sleep(2)

def work(db):
    with db.engine.connect() as connection:
        time.sleep(2)
        connection.execute('select 1 from room_trumpet;')
        time.sleep(2)
        connection_id = connection.execute('select connection_id();').first()[0]
        print('work: connection_id:{}, status:{}'.format(connection_id, db.engine.pool.status()))
        time.sleep(2)
main()
