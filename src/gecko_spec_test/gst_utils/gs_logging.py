import logging
import os
import time

if os.path.isdir('log') is False:
    os.mkdir('log')

ct = int(time.perf_counter())

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

_fh = logging.FileHandler(f'log/gs_debug_{ct}.txt', encoding='utf-8')
_fh.setLevel(logging.DEBUG)
_fh.setFormatter(
    logging.Formatter(
        '[%(asctime)s] (%(relativeCreated)6d %(threadName)s) %(name)s [%(levelname)s] %(message)s'
    )
)


class Logger:
    def __init__(self, name):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(_fh)

    def debug(self, msg: str, *args):
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(msg, *args)

    def info(self, msg: str, *args: object):
        if self._logger.isEnabledFor(logging.INFO):
            self._logger.info(msg, *args)

    def error(self, msg: str, *args):
        if self._logger.isEnabledFor(logging.INFO):
            self._logger.error(msg, *args)

    def warning(self, msg: str, *args):
        if self._logger.isEnabledFor(logging.INFO):
            self._logger.warning(msg, *args)

    def critical(self, msg: str, *args):
        if self._logger.isEnabledFor(logging.INFO):
            self._logger.critical(msg, *args)


def get_logger(name: str) -> Logger:
    return Logger(name)
