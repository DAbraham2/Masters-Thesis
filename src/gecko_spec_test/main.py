from gst_utils.logging import get_logger

logger = get_logger('gst_main')


def __main() -> None:
    logger.debug('dbg')
    logger.info('fyi')
    logger.warning('warn')
    logger.critical('crit')
    logger.error('fucked up')


if __name__ == '__main__':
    __main()
