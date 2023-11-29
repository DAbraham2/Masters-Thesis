import os
import json

def __main()->None:
    model_base = os.path.join(os.path.dirname(__file__), '../gecko_spec_test/models/mp-model.json')
    with open(model_base, encoding='utf-8') as model:
        original_content = model.read()
    with open(os.path.join(os.path.dirname(model_base), 'backup.json'), 'wt') as backup:
        backup.write(original_content)

    models = json.loads(original_content)
    for m in models['models']:
        try:
            m.pop('editor')
        except KeyError:
            continue

    modified = json.dumps(models)
    with open(model_base, mode='w') as model:
        model.write(modified)

if __name__ == '__main__':
    __main()