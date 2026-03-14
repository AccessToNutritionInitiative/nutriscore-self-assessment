from rq import Queue

from nutri.application.workers.redis import redis_conn

queue = Queue(connection=redis_conn)
