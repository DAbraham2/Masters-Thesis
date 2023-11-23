import ast
import os.path
import sys

from gst_utils.gs_logging import get_logger

import altwalker.graphwalker as graphwalker
import altwalker.run as runner


logger = get_logger('gst_main')


def __main() -> None:
    models: list[tuple] = [
        ('./models/mp-model.json', 'quick_random(edge_coverage(100))')
    ]
    res = graphwalker.check(models)
    logger.info(res)

    state = runner.verify(
        test_package='combined_test_suite/tests', model_paths=['./models/mp-model.json']
    )

    if state['status'] is False:
        logger.error(
            'Verification issues:\n%s\n%s\n%s',
            state['issues'],
            state['methods'],
            state['missing'],
        )
        with open(
            os.path.join(os.path.dirname(__file__), 'combined_test_suite/tests/test.py')
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
            os.path.join(
                os.path.dirname(__file__), 'combined_test_suite/tests/test.py'
            ),
            'w',
        ) as f:
            f.write(ast.unparse(tree))

        sys.exit(1)

    product = runner.online(
        test_package='combined_test_suite/tests', models=models, executor_type='python'
    )
    logger.info(product)


if __name__ == '__main__':
    __main()
