import logging
import os

if os.path.isdir('log') is False:
    os.mkdir('log')

logging.basicConfig(
    filename='log/gst_debug.txt',
    encoding='utf-8',
    level=logging.DEBUG,
)

_ch = logging.StreamHandler()
_ch.setLevel(logging.INFO)
_ch.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)


class Logger:
    def __init__(self, name):
        self._logger = logging.getLogger(name)
        self._logger.addHandler(_ch)

    def debug(self, msg, *args):
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(msg=msg, *args)

    def info(self, msg: object, *args: object):
        if self._logger.isEnabledFor(logging.INFO):
            self._logger.info(msg, *args)

    def error(self, msg, *args):
        if self._logger.isEnabledFor(logging.INFO):
            self._logger.error(msg, *args)

    def warning(self, msg, *args):
        if self._logger.isEnabledFor(logging.INFO):
            self._logger.warning(msg, *args)

    def critical(self, msg, *args):
        if self._logger.isEnabledFor(logging.INFO):
            self._logger.critical(msg, *args)


def get_logger(name: str) -> Logger:
    return Logger(name)
