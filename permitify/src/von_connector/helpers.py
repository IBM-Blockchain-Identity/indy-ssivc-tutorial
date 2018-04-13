import time
import datetime
from uuid import uuid4
from random import randrange


def uuid():
    return str(uuid4())


def pst():
    return '%d%d%d%d%d %d%d%d%d' % tuple(randrange(10) for i in range(9))


def now():
    return int(time.mktime(datetime.datetime.now().timetuple()))


def one_year():
    return int(
      time.mktime(
        (
          datetime.datetime.now() +
          datetime.timedelta(days=365)
        ).timetuple()
      )
    )
