import datetime


def time_ago(time):
    now = datetime.datetime.utcnow()
    days, r = divmod(int((now - time).total_seconds()), 86400)
    h, r = divmod(r, 3600)
    m, s = divmod(r, 60)
    return (f'{days} days ' if days else '')+f'{h:02}:{m:02}:{s:02} ago'
