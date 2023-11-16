import altwalker.graphwalker as graphwalker
import altwalker.run as runner

from gst_utils.logging import get_logger

logger = get_logger('gst_main')


def __main() -> None:
    logger.debug('dbg')
    logger.info('fyi')
    logger.warning('warn')
    logger.critical('crit')
    logger.error('fucked up')

    models: list[tuple] = [('./models/mp-model.json', 'random(edge_coverage(100))')]
    res = graphwalker.check(models)
    logger.info(res)
    product = runner.online(
        test_package='combined_test_suite/tests', models=models, executor_type='python'
    )
    logger.info(product)


if __name__ == '__main__':
    __main()
