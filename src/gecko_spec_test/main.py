import ast
import json
import os.path
import sys
import argparse
import time

from gst_utils.gs_logging import get_logger

import altwalker.graphwalker as graphwalker
import altwalker.run as runner


logger = get_logger('gst_main')

__main_parser = argparse.ArgumentParser()


def __main() -> None:
    args = __main_parser.parse_args()

    models: list[tuple] = [
        # ('./models/mp-model.json', f'random(time_duration({args.duration}))'),
        (
            os.path.join(os.path.dirname(__file__), 'models', 'combined-model.json'),
            'random(vertex_coverage(100) && edge_coverage(100))',
        ),
    ]

    res = graphwalker.check(models)
    logger.info(res)

    state = runner.verify(
        test_package='combined/tests', model_paths=['./models/combined-model.json']
    )

    if state['status'] is False and args.fix is False:
        logger.error(
            'Verification issues:\n%s\n%s\n%s',
            state['issues'],
            state['methods'],
            state['missing'],
        )
        sys.exit(1)

    if state['status'] is False and args.fix:
        with open(
            os.path.join(os.path.dirname(__file__), 'combined/tests/test.py')
        ) as f:
            content = f.read()
            tree = ast.parse(content)
        tree_classes = [cls for cls in tree.body if isinstance(cls, ast.ClassDef)]
        class_names = []
        for c in tree_classes:
            class_names.append(c.name)
        for cls, v in state['missing'].items():
            if cls in class_names:
                c = [i for i in tree_classes if i.name == cls][0]
            else:
                c = ast.ClassDef(
                    name=cls,
                    body=[],
                    bases=[],
                    keywords=[],
                    decorator_list=[],
                    type_params=[],
                )
                tree.body.append(c)
            for m in v:
                logger.warning('Missing: %s::%s', cls, m)
                fun = ast.FunctionDef(
                    name=m,
                    args=ast.arguments(
                        posonlyargs=[],
                        args=[ast.arg(arg='self')],
                        kwonlyargs=[],
                        kw_defaults=[],
                        defaults=[],
                    ),
                    body=[ast.Expr(value=ast.Constant(value=Ellipsis))],
                    decorator_list=[],
                    type_params=[],
                )
                c.body.append(fun)

        ast.fix_missing_locations(tree)

        with open(
            os.path.join(os.path.dirname(__file__), 'combined/tests/test.py'),
            'w',
        ) as f:
            f.write(ast.unparse(tree))

        sys.exit(1)

    logger.info(
        '\n\n\n\n\n\n Test will run with the following criteria: %s \n\n\n\n\n\n',
        models[0][1],
    )

    start_time = time.perf_counter_ns()
    product = runner.online(
        test_package='combined/tests', models=models, executor_type='python'
    )
    end_time = time.perf_counter_ns()
    logger.info(product)

    logger.info('Test lasted for %s seconds', ((end_time - start_time) / 1_000_000_000))


if __name__ == '__main__':
    __main_parser.add_argument('duration', help='Timeout duration in seconds', type=int)
    __main_parser.add_argument(
        '-f', '--fix', help='fix the module', action='store_true'
    )
    __main()
