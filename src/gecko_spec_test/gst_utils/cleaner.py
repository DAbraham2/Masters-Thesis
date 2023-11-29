from .gs_logging import get_logger

logger = get_logger(__name__)


def clean_cli_command(actual: str, expected: str) -> str:
    try:
        data = actual.split(expected)[1].strip()
        logger.debug('Cleaned data from stream: <<%s>>', data)
        return data
    except:
        logger.critical('Could not clean data...\nreturning empty string')
        return ''
