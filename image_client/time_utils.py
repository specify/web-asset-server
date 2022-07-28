import datetime, pytz

def get_pst_time(user_time):
    tz = pytz.timezone('America/Los_Angeles')
    localtime = user_time.astimezone(tz)
    return localtime


def get_pst_time_now():
    datetime_now = datetime.datetime.now(datetime.timezone.utc)
    return get_pst_time(datetime_now)


def get_pst_time_now_string():
    TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    return (get_pst_time_now().strftime(TIME_FORMAT))


def get_pst_date_from_datetime(user_time):
    TIME_FORMAT = "%Y-%m-%d"
    return (user_time.strftime(TIME_FORMAT))

def get_pst_date_time_from_datetime(user_time):
    TIME_FORMAT = "%Y-%m-%d  %H:%M:%S"
    return (user_time.strftime(TIME_FORMAT))
