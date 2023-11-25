import functools
import logging
import os
import time
from typing import Union

if os.path.isdir('log') is False:
    os.mkdir('log')

ct = int(time.perf_counter())

_fh = logging.FileHandler(f'log/gs_debug_{ct}.txt', encoding='utf-8')
_fh.setLevel(logging.DEBUG)
_fh.setFormatter(
    logging.Formatter(
        '[%(asctime)s] (%(relativeCreated)6d %(threadName)s) %(name)s [%(levelname)s] %(message)s'
    )
)

_ch = logging.StreamHandler()
_ch.setLevel(logging.INFO)
_ch.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)


class Logger:
    def __init__(self, name):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(_fh)
        self._logger.addHandler(_ch)

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


def log(_func=None, *, given_logger: Union[Logger, logging.Logger] = None):
    def decorator_log(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(__name__)
            try:
                if given_logger is None:
                    first_args = next(
                        iter(args), None
                    )  # capture first arg to check for `self`
                    logger_params = [  # does kwargs have any logger
                        x
                        for x in kwargs.values()
                        if isinstance(x, logging.Logger) or isinstance(x, Logger)
                    ] + [  # # does args have any logger
                        x
                        for x in args
                        if isinstance(x, logging.Logger) or isinstance(x, Logger)
                    ]
                    if hasattr(first_args, '__dict__'):  # is first argument `self`
                        logger_params = (
                            logger_params
                            + [
                                x
                                for x in first_args.__dict__.values()  # does class (dict) members have any logger
                                if isinstance(x, logging.Logger)
                                or isinstance(x, Logger)
                            ]
                        )
                    h_logger = next(
                        iter(logger_params), get_logger(func.__qualname__)
                    )  # get the next/first/default logger
                else:
                    h_logger = (
                        given_logger  # logger is passed explicitly to the decorator
                    )

                logger = h_logger
            except Exception:
                pass

            try:
                logger.debug('Execution starting on %s', func.__qualname__)
                result = func(*args, **kwargs)
                logger.debug('Execution finished on %s', func.__qualname__)
                return result
            except Exception as e:
                logger.critical(
                    f'Exception raised in {func.__name__}. exception: {str(e)}'
                )
                raise e

        return wrapper

    if _func is None:
        return decorator_log
    else:
        return decorator_log(_func)
