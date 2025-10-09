import logging
import logging.handlers
import os

from utils.utils import AppConfig

LOG_DATE_FMT = "%d-%m-%Y %H:%M:%S"

config = AppConfig()

if not os.path.exists(config.log_dir):
    os.mkdir(config.log_dir)

log = logging.getLogger(config.log_name)
log.propagate = False
log.setLevel(config.log_level)

formatter = logging.Formatter(
    fmt="%(asctime)s|%(levelname)s|%(message)s", datefmt=LOG_DATE_FMT
)


def create_time_rotating_file_handler(log_level, filename, formatter):
    handler = logging.handlers.TimedRotatingFileHandler(
        f"{config.log_dir}/{filename}.log", when="midnight", backupCount=30
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
