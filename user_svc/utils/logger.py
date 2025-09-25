import logging
import logging.handlers
import os

from utils import get_envvar

LOG_DATE_FMT = "%d-%m-%Y %H:%M:%S"

if not os.path.exists(get_envvar("LOG_DIR")):
    os.mkdir(get_envvar("LOG_DIR"))

log = logging.getLogger(get_envvar("LOG_NAME"))
log.propagate = False
log.setLevel(get_envvar("LOG_LEVEL"))

formatter = logging.Formatter(
    fmt="%(asctime)s|%(levelname)s|%(message)s", datefmt=LOG_DATE_FMT
)


def create_time_rotating_file_handler(log_level, filename, formatter):
    handler = logging.handlers.TimedRotatingFileHandler(
        f"{get_envvar('LOG_DIR')}/{filename}.log", when="midnight", backupCount=30
    )
    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    return handler


class DebugFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.DEBUG


# debug_handler
debug_handler = create_time_rotating_file_handler(logging.DEBUG, "debug", formatter)
debug_handler.addFilter(DebugFilter())

# error_handler
error_handler = create_time_rotating_file_handler(logging.WARNING, "error", formatter)

# info_handler
info_handler = create_time_rotating_file_handler(logging.INFO, "info", formatter)

log.addHandler(debug_handler)
log.addHandler(error_handler)
log.addHandler(info_handler)
