import requests, hmac
import time
import settings

def build_url(endpoint):
    host = settings.SERVER_NAME
    # host = 'ibss-images.calacademy.org'
    port = settings.SERVER_PORT
    return f"{settings.SERVER_PROTOCOL}://{host}:{port}/{endpoint}"

def update_time_delta_from_response(response):
    global server_time_delta
    try:
        timestamp = response.headers['X-Timestamp']
    except KeyError:
        server_time_delta = 0
        return

    server_time_delta = int(timestamp) - int(time.time())
    print(f"Updated server time delta to {server_time_delta}")

def get_timestamp():
    """Return an integer timestamp with one second resolution for
    the current moment.
    """
    return int(time.time()) + server_time_delta


def update_time_delta():
    response = requests.get(build_url(""))
    update_time_delta_from_response(response)


def generate_token(timestamp, filename):
    """Generate the auth token for the given filename and timestamp. """
    timestamp = get_timestamp()
    msg = str(timestamp).encode() + filename.encode()
    mac = hmac.new(settings.KEY.encode(), msg=msg, digestmod='md5')
    return ':'.join((mac.hexdigest(), str(timestamp)))