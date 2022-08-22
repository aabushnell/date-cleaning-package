from .settings import __DEBUG__
log_message = ""
active = False


def log(message):
    global log_message
    log_message = log_message + "\n" + message


def get_log():
    return log_message


def clear_log():
    global log_message
    log_message = ""
