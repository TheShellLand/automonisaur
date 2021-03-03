import datetime


class Dates:
    today = f'{datetime.datetime.today()}'
    now = f'{datetime.datetime.now()}'
    iso = f'{datetime.datetime.isoformat(datetime.datetime.now())}'
    iso_short = f'{datetime.date.today().isoformat()}'

    filename_timestamp = str(datetime.datetime.now().isoformat()).replace(':', '_')
